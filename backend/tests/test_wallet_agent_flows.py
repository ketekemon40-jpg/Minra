"""Wallet auth, holder gating, agent lifecycle, strategy, and contest API regression tests."""
import os
import time
from pathlib import Path

import pytest
import requests
from dotenv import dotenv_values
from pymongo import MongoClient


def _base_url() -> str:
    value = os.environ.get("REACT_APP_BACKEND_URL")
    if value:
        return value.rstrip("/")

    env_file = Path("/app/frontend/.env")
    loaded = dotenv_values(env_file)
    fallback = loaded.get("REACT_APP_BACKEND_URL")
    if not fallback:
        pytest.skip("REACT_APP_BACKEND_URL is not available")
    return str(fallback).rstrip("/")


BASE_URL = _base_url()
API_URL = f"{BASE_URL}/api"


@pytest.fixture(scope="session")
def api_client():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="session")
def db_client():
    backend_env = dotenv_values("/app/backend/.env")
    mongo_url = backend_env.get("MONGO_URL")
    db_name = backend_env.get("DB_NAME")
    if not mongo_url or not db_name:
        pytest.skip("Missing backend Mongo env values")
    client = MongoClient(mongo_url)
    db = client[db_name]
    yield db
    client.close()


@pytest.fixture(scope="session")
def created_ids():
    return {"wallet_ids": [], "agent_ids": []}


@pytest.fixture(scope="session", autouse=True)
def cleanup_generated_data(db_client, created_ids):
    yield
    if created_ids["agent_ids"]:
        db_client.events.delete_many({"agent_id": {"$in": created_ids["agent_ids"]}})
        db_client.decision_replays.delete_many({"agent_id": {"$in": created_ids["agent_ids"]}})
        db_client.strategy_history.delete_many({"agent_id": {"$in": created_ids["agent_ids"]}})
        db_client.contest_archive.delete_many({"agent_id": {"$in": created_ids["agent_ids"]}})
        db_client.agents.delete_many({"id": {"$in": created_ids["agent_ids"]}})
    if created_ids["wallet_ids"]:
        db_client.wallet_sessions.delete_many({"wallet_id": {"$in": created_ids["wallet_ids"]}})
        db_client.wallets.delete_many({"id": {"$in": created_ids["wallet_ids"]}})


def create_wallet_and_session(api_client, provider="Phantom"):
    create = api_client.post(f"{API_URL}/wallets", json={"provider": provider})
    assert create.status_code == 201
    wallet = create.json()

    connect = api_client.post(
        f"{API_URL}/session",
        json={"wallet_id": wallet["wallet_id"], "recovery_capability": wallet["recovery_capability"]},
    )
    assert connect.status_code == 200
    session = connect.json()
    return wallet, session


def wait_for_replays(api_client, headers, timeout_seconds=30):
    deadline = time.time() + timeout_seconds
    last = None
    while time.time() < deadline:
        response = api_client.get(f"{API_URL}/agent/replay", headers=headers)
        if response.status_code == 200:
            payload = response.json()
            last = payload
            if payload.get("entries"):
                return payload
        time.sleep(2)
    return last


class TestPublicAndWalletAuth:
    def test_health_and_public_endpoints(self, api_client):
        health = api_client.get(f"{API_URL}/health")
        assert health.status_code == 200
        health_data = health.json()
        assert health_data["status"] == "ok"
        assert isinstance(health_data["worker_online"], bool)

        world = api_client.get(f"{API_URL}/world")
        assert world.status_code == 200
        world_data = world.json()
        assert isinstance(world_data["agents"], list)
        assert "active_agents" in world_data

        board = api_client.get(f"{API_URL}/contest/leaderboard")
        assert board.status_code == 200
        board_data = board.json()
        assert "season" in board_data
        assert "entries" in board_data

    def test_session_without_wallet_identity_fails(self, api_client):
        response = api_client.post(f"{API_URL}/session", json={})
        assert response.status_code == 422
        detail = response.json().get("detail", [])
        assert isinstance(detail, list)

    def test_anonymous_or_forged_bearer_rejected(self, api_client):
        response = api_client.get(f"{API_URL}/agent", headers={"Authorization": "Bearer source-anon-token"})
        assert response.status_code == 401
        assert "Reconnect your wallet" in response.json().get("detail", "")

    def test_wallet_payload_injection_rejected(self, api_client):
        response = api_client.post(
            f"{API_URL}/wallets",
            json={"provider": "Phantom", "owner": "injected", "holder_amount": 9999},
        )
        assert response.status_code == 422
        detail_text = str(response.json())
        assert "Extra" in detail_text or "extra" in detail_text

    def test_forged_recovery_rejected(self, api_client, created_ids):
        wallet_resp = api_client.post(f"{API_URL}/wallets", json={"provider": "Phantom"})
        assert wallet_resp.status_code == 201
        wallet = wallet_resp.json()
        created_ids["wallet_ids"].append(wallet["wallet_id"])

        forged = api_client.post(
            f"{API_URL}/session",
            json={"wallet_id": wallet["wallet_id"], "recovery_capability": "x" * 48},
        )
        assert forged.status_code == 401
        assert "could not be restored" in forged.json().get("detail", "")

    def test_switch_revokes_old_token_and_disconnect_revokes_current(self, api_client, created_ids):
        wallet1, session1 = create_wallet_and_session(api_client, "Phantom")
        created_ids["wallet_ids"].append(wallet1["wallet_id"])

        wallet2_resp = api_client.post(f"{API_URL}/wallets", json={"provider": "Solflare"})
        assert wallet2_resp.status_code == 201
        wallet2 = wallet2_resp.json()
        created_ids["wallet_ids"].append(wallet2["wallet_id"])

        switched = api_client.post(
            f"{API_URL}/session",
            json={"wallet_id": wallet2["wallet_id"], "recovery_capability": wallet2["recovery_capability"]},
            headers={"Authorization": f"Bearer {session1['token']}"},
        )
        assert switched.status_code == 200
        session2 = switched.json()

        old_me = api_client.get(f"{API_URL}/session/me", headers={"Authorization": f"Bearer {session1['token']}"})
        assert old_me.status_code == 401

        current_me = api_client.get(f"{API_URL}/session/me", headers={"Authorization": f"Bearer {session2['token']}"})
        assert current_me.status_code == 200
        assert current_me.json()["wallet_id"] == wallet2["wallet_id"]

        disconnect = api_client.post(
            f"{API_URL}/session/disconnect", headers={"Authorization": f"Bearer {session2['token']}"}
        )
        assert disconnect.status_code == 200
        assert disconnect.json()["disconnected"] is True

        after_disconnect = api_client.get(
            f"{API_URL}/session/me", headers={"Authorization": f"Bearer {session2['token']}"}
        )
        assert after_disconnect.status_code == 401


class TestHolderGatingAndAgentProgress:
    def test_one_agent_per_wallet_and_persistence_lookup(self, api_client, created_ids):
        wallet, session = create_wallet_and_session(api_client, "Backpack")
        created_ids["wallet_ids"].append(wallet["wallet_id"])
        headers = {"Authorization": f"Bearer {session['token']}"}

        create = api_client.post(
            f"{API_URL}/agent",
            headers=headers,
            json={"name": "Alder", "avatar": "brass", "preference": "balanced", "strategy_preset": "balanced"},
        )
        assert create.status_code == 201
        agent = create.json()
        created_ids["agent_ids"].append(agent["id"])
        assert agent["name"] == "Alder"

        second = api_client.post(
            f"{API_URL}/agent",
            headers=headers,
            json={"name": "Birch", "avatar": "sage", "preference": "deep", "strategy_preset": "prospector"},
        )
        assert second.status_code == 409

        me = api_client.get(f"{API_URL}/agent", headers=headers)
        assert me.status_code == 200
        assert me.json()["agent"]["id"] == agent["id"]

    def test_holder_zero_blocks_mutations_but_allows_own_view(self, api_client, db_client, created_ids):
        wallet, session = create_wallet_and_session(api_client, "Phantom")
        created_ids["wallet_ids"].append(wallet["wallet_id"])
        headers = {"Authorization": f"Bearer {session['token']}"}

        created = api_client.post(
            f"{API_URL}/agent",
            headers=headers,
            json={"name": "Cedar", "avatar": "copper", "preference": "balanced", "strategy_preset": "balanced"},
        )
        assert created.status_code == 201
        agent = created.json()
        created_ids["agent_ids"].append(agent["id"])

        db_client.wallets.update_one({"id": wallet["wallet_id"]}, {"$set": {"holder_amount": 0}})

        own_view = api_client.get(f"{API_URL}/agent", headers=headers)
        assert own_view.status_code == 200
        assert own_view.json()["agent"]["id"] == agent["id"]

        mutate_endpoints = [
            ("/agent", {"name": "Dune", "avatar": "brass", "preference": "balanced", "strategy_preset": "balanced"}),
            ("/agent/action", {"action": "start"}),
            (
                "/agent/strategy",
                {
                    "expected_version": 1,
                    "strategy": {
                        "name": "Locked Strategy",
                        "target_depth": 3,
                        "risk": 40,
                        "haul_threshold": 75,
                        "energy_reserve": 30,
                        "repair_threshold": 30,
                        "ore_priority": "balanced",
                        "rules": [],
                    },
                },
            ),
            (
                "/agent/strategy/evaluate",
                {
                    "decisions": 120,
                    "strategy": {
                        "name": "Locked Strategy",
                        "target_depth": 3,
                        "risk": 40,
                        "haul_threshold": 75,
                        "energy_reserve": 30,
                        "repair_threshold": 30,
                        "ore_priority": "balanced",
                        "rules": [],
                    },
                },
            ),
            ("/contest/enter", None),
        ]

        for endpoint, payload in mutate_endpoints:
            response = api_client.post(f"{API_URL}{endpoint}", headers=headers, json=payload)
            assert response.status_code == 403
            assert "holdings are required" in response.json().get("detail", "")

        holder_notice = api_client.get(f"{API_URL}/session/me", headers=headers)
        assert holder_notice.status_code == 200
        assert holder_notice.json()["eligible"] is False

        db_client.wallets.update_one({"id": wallet["wallet_id"]}, {"$set": {"holder_amount": 1000}})

    def test_worker_pauses_active_agent_when_holder_access_lost(self, api_client, db_client, created_ids):
        wallet, session = create_wallet_and_session(api_client, "Solflare")
        created_ids["wallet_ids"].append(wallet["wallet_id"])
        headers = {"Authorization": f"Bearer {session['token']}"}

        create = api_client.post(
            f"{API_URL}/agent",
            headers=headers,
            json={"name": "Elm", "avatar": "ice", "preference": "balanced", "strategy_preset": "balanced"},
        )
        assert create.status_code == 201
        agent = create.json()
        created_ids["agent_ids"].append(agent["id"])

        started = api_client.post(f"{API_URL}/agent/action", headers=headers, json={"action": "start"})
        assert started.status_code == 200

        time.sleep(3)
        db_client.wallets.update_one({"id": wallet["wallet_id"]}, {"$set": {"holder_amount": 0}})

        time.sleep(5)
        after_revoke = api_client.get(f"{API_URL}/agent", headers=headers)
        assert after_revoke.status_code == 200
        revoked_agent = after_revoke.json()["agent"]
        assert revoked_agent["status"] == "paused"
        frozen_step = revoked_agent["step"]

        time.sleep(4)
        still_paused = api_client.get(f"{API_URL}/agent", headers=headers)
        assert still_paused.status_code == 200
        frozen_again = still_paused.json()["agent"]
        assert frozen_again["step"] == frozen_step

        db_client.wallets.update_one({"id": wallet["wallet_id"]}, {"$set": {"holder_amount": 1000}})


class TestStrategyContestRewards:
    def test_strategy_presets_and_save_evaluate_and_contest_entry(self, api_client, created_ids):
        wallet, session = create_wallet_and_session(api_client, "Phantom")
        created_ids["wallet_ids"].append(wallet["wallet_id"])
        headers = {"Authorization": f"Bearer {session['token']}"}

        create = api_client.post(
            f"{API_URL}/agent",
            headers=headers,
            json={"name": "Grove", "avatar": "sage", "preference": "balanced", "strategy_preset": "balanced"},
        )
        assert create.status_code == 201
        agent = create.json()
        created_ids["agent_ids"].append(agent["id"])

        presets = api_client.get(f"{API_URL}/strategy/presets")
        assert presets.status_code == 200
        preset_data = presets.json()
        assert len(preset_data) == 4

        current = api_client.get(f"{API_URL}/agent/strategy", headers=headers)
        assert current.status_code == 200
        strategy_data = current.json()
        assert strategy_data["version"] >= 1

        new_strategy = {
            "name": "Long Route Strategy",
            "target_depth": 4,
            "risk": 35,
            "haul_threshold": 70,
            "energy_reserve": 25,
            "repair_threshold": 28,
            "ore_priority": "rich",
            "rules": [
                {
                    "id": "energy_guard",
                    "name": "Energy guard",
                    "enabled": True,
                    "match": "all",
                    "groups": [
                        {
                            "match": "all",
                            "conditions": [
                                {"field": "energy", "operator": "lte", "value": 30},
                                {"field": "tool", "operator": "lte", "value": 45},
                            ],
                        }
                    ],
                    "action": "repair",
                }
            ],
        }
        saved = api_client.post(
            f"{API_URL}/agent/strategy",
            headers=headers,
            json={"strategy": new_strategy, "expected_version": strategy_data["version"]},
        )
        assert saved.status_code == 200
        saved_data = saved.json()
        assert saved_data["strategy"]["name"] == "Long Route Strategy"
        assert saved_data["version"] == strategy_data["version"] + 1

        evaluated = api_client.post(
            f"{API_URL}/agent/strategy/evaluate",
            headers=headers,
            json={"strategy": new_strategy, "decisions": 120},
        )
        assert evaluated.status_code == 200
        eval_data = evaluated.json()
        assert "score" in eval_data
        assert isinstance(eval_data["trace"], list)

        entered = api_client.post(f"{API_URL}/contest/enter", headers=headers)
        assert entered.status_code == 200
        entered_data = entered.json()
        assert entered_data["contest"]["status"] == "active"

        second_entry = api_client.post(f"{API_URL}/contest/enter", headers=headers)
        assert second_entry.status_code == 409

    def test_rewards_surface_and_claim_rejected(self, api_client, created_ids):
        rewards = api_client.get(f"{API_URL}/rewards")
        assert rewards.status_code == 200
        rewards_data = rewards.json()
        assert rewards_data["asset"] == "GLDX"
        assert rewards_data["platform"] == "Stonk.fun"
        assert rewards_data["platform_url"] == "https://www.stonkfun.xyz"
        assert rewards_data["distribution_mode"] == "automatic"
        assert rewards_data["chain_connected"] is False

        public_receipts = api_client.get(f"{API_URL}/rewards/receipts")
        assert public_receipts.status_code == 401

        wallet, session = create_wallet_and_session(api_client, "Solflare")
        created_ids["wallet_ids"].append(wallet["wallet_id"])
        auth_headers = {"Authorization": f"Bearer {session['token']}"}

        receipts = api_client.get(f"{API_URL}/rewards/receipts", headers=auth_headers)
        assert receipts.status_code == 200
        receipt_data = receipts.json()
        assert receipt_data["wallet_address"] == wallet["address"]
        assert receipt_data["transactions"] == []
        assert receipt_data["total_received"] is None
        assert receipt_data["last_received_at"] is None
        assert receipt_data["observed_at"] is None
        assert receipt_data["chain_connected"] is False

        claim = api_client.post(f"{API_URL}/rewards/claim", headers={"Authorization": f"Bearer {session['token']}"})
        assert claim.status_code == 404


class TestReplayContractAndPersistence:
    """Decision replay API, ownership scope, cursor pagination and replay arithmetic validations."""

    def test_replay_requires_valid_bearer_and_no_agent_empty(self, api_client, created_ids):
        unauth = api_client.get(f"{API_URL}/agent/replay")
        assert unauth.status_code == 401

        forged = api_client.get(
            f"{API_URL}/agent/replay", headers={"Authorization": "Bearer source-anon-token"}
        )
        assert forged.status_code == 401

        wallet, session = create_wallet_and_session(api_client, "Phantom")
        created_ids["wallet_ids"].append(wallet["wallet_id"])
        response = api_client.get(
            f"{API_URL}/agent/replay", headers={"Authorization": f"Bearer {session['token']}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["agent_id"] is None
        assert data["entries"] == []
        assert data["total"] == 0

        wallet2_resp = api_client.post(f"{API_URL}/wallets", json={"provider": "Solflare"})
        assert wallet2_resp.status_code == 201
        wallet2 = wallet2_resp.json()
        created_ids["wallet_ids"].append(wallet2["wallet_id"])

        switched = api_client.post(
            f"{API_URL}/session",
            json={"wallet_id": wallet2["wallet_id"], "recovery_capability": wallet2["recovery_capability"]},
            headers={"Authorization": f"Bearer {session['token']}"},
        )
        assert switched.status_code == 200

        revoked = api_client.get(
            f"{API_URL}/agent/replay", headers={"Authorization": f"Bearer {session['token']}"}
        )
        assert revoked.status_code == 401

    def test_replay_records_generate_and_arithmetic_matches(self, api_client, db_client, created_ids):
        wallet, session = create_wallet_and_session(api_client, "Backpack")
        created_ids["wallet_ids"].append(wallet["wallet_id"])
        headers = {"Authorization": f"Bearer {session['token']}"}

        create = api_client.post(
            f"{API_URL}/agent",
            headers=headers,
            json={"name": "ReplayProbe", "avatar": "brass", "preference": "deep", "strategy_preset": "prospector"},
        )
        assert create.status_code == 201
        agent = create.json()
        created_ids["agent_ids"].append(agent["id"])

        start = api_client.post(f"{API_URL}/agent/action", headers=headers, json={"action": "start"})
        assert start.status_code == 200

        accelerated_start = time.time() - 280
        db_client.agents.update_one(
            {"id": agent["id"]}, {"$set": {"started_at": accelerated_start, "stage_started_at": accelerated_start}}
        )

        replay = wait_for_replays(api_client, headers, timeout_seconds=35)
        assert replay is not None
        entries = replay.get("entries", [])
        assert len(entries) > 0

        ids = [row["id"] for row in entries]
        assert len(ids) == len(set(ids))

        for row in entries:
            assert row["score_after"] - row["score_before"] == row["score_delta"]
            assert row["after"]["banked_points"] - row["before"]["banked_points"] == row["banked_delta"]
            assert (
                row["after"]["exploration_points"] - row["before"]["exploration_points"]
                == row["exploration_delta"]
            )
            assert row["after"]["penalties"] - row["before"]["penalties"] == row["penalty_delta"]
            assert row["score_after"] >= 0

        pause = api_client.post(f"{API_URL}/agent/action", headers=headers, json={"action": "pause"})
        assert pause.status_code == 200

    def test_replay_filters_and_before_cursor_no_overlap(self, api_client, created_ids):
        wallet, session = create_wallet_and_session(api_client, "Solflare")
        created_ids["wallet_ids"].append(wallet["wallet_id"])
        headers = {"Authorization": f"Bearer {session['token']}"}

        create = api_client.post(
            f"{API_URL}/agent",
            headers=headers,
            json={"name": "CursorProbe", "avatar": "sage", "preference": "balanced", "strategy_preset": "balanced"},
        )
        assert create.status_code == 201
        created_ids["agent_ids"].append(create.json()["id"])

        assert api_client.post(f"{API_URL}/agent/action", headers=headers, json={"action": "start"}).status_code == 200
        replay = wait_for_replays(api_client, headers, timeout_seconds=35)
        assert replay is not None
        assert replay["entries"]

        first_page = api_client.get(
            f"{API_URL}/agent/replay?limit=3&scope=all&change=all", headers=headers
        )
        assert first_page.status_code == 200
        first_data = first_page.json()
        assert len(first_data["entries"]) <= 3

        if first_data["has_more"] and first_data["next_before"]:
            second_page = api_client.get(
                f"{API_URL}/agent/replay?limit=3&before={first_data['next_before']}", headers=headers
            )
            assert second_page.status_code == 200
            second_data = second_page.json()
            first_ids = {r["id"] for r in first_data["entries"]}
            second_ids = {r["id"] for r in second_data["entries"]}
            assert first_ids.isdisjoint(second_ids)

        gain = api_client.get(f"{API_URL}/agent/replay?change=gain&limit=5", headers=headers)
        loss = api_client.get(f"{API_URL}/agent/replay?change=loss&limit=5", headers=headers)
        steady = api_client.get(f"{API_URL}/agent/replay?change=steady&limit=5", headers=headers)
        for resp in [gain, loss, steady]:
            assert resp.status_code == 200
            assert "total" in resp.json()

        out_of_bounds_limit = api_client.get(f"{API_URL}/agent/replay?limit=201", headers=headers)
        assert out_of_bounds_limit.status_code == 422

        invalid_scope = api_client.get(f"{API_URL}/agent/replay?scope=bad", headers=headers)
        assert invalid_scope.status_code == 422

        pause = api_client.post(f"{API_URL}/agent/action", headers=headers, json={"action": "pause"})
        assert pause.status_code == 200

    def test_replay_read_allowed_after_holder_loss_and_owner_scoped(self, api_client, db_client, created_ids):
        wallet1, session1 = create_wallet_and_session(api_client, "Phantom")
        created_ids["wallet_ids"].append(wallet1["wallet_id"])
        headers1 = {"Authorization": f"Bearer {session1['token']}"}

        create1 = api_client.post(
            f"{API_URL}/agent",
            headers=headers1,
            json={"name": "OwnerOne", "avatar": "copper", "preference": "careful", "strategy_preset": "guardian"},
        )
        assert create1.status_code == 201
        agent1 = create1.json()
        created_ids["agent_ids"].append(agent1["id"])

        assert api_client.post(f"{API_URL}/agent/action", headers=headers1, json={"action": "start"}).status_code == 200
        replay1 = wait_for_replays(api_client, headers1, timeout_seconds=35)
        assert replay1 is not None
        assert replay1.get("agent_id") == agent1["id"]

        db_client.wallets.update_one({"id": wallet1["wallet_id"]}, {"$set": {"holder_amount": 0}})
        replay_after_loss = api_client.get(f"{API_URL}/agent/replay", headers=headers1)
        assert replay_after_loss.status_code == 200
        assert replay_after_loss.json()["agent_id"] == agent1["id"]

        wallet2, session2 = create_wallet_and_session(api_client, "Solflare")
        created_ids["wallet_ids"].append(wallet2["wallet_id"])
        headers2 = {"Authorization": f"Bearer {session2['token']}"}
        replay2 = api_client.get(f"{API_URL}/agent/replay", headers=headers2)
        assert replay2.status_code == 200
        assert replay2.json()["agent_id"] is None

        db_client.wallets.update_one({"id": wallet1["wallet_id"]}, {"$set": {"holder_amount": 1000}})

        pause = api_client.post(f"{API_URL}/agent/action", headers=headers1, json={"action": "pause"})
        assert pause.status_code in (200, 409)
