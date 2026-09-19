"""Immutable records of executed decisions, published from the mining worker's atomic outbox."""
from datetime import datetime, timezone
from replay_models import DecisionReplay, ReplayState, ReplayPage
from strategies import score
from typing import Literal, Optional
from fastapi import APIRouter, Header, Query


def record_decision(agent, sequence, timestamp, before, after, stage, message, contest):
    banked = after['banked_points'] - before['banked_points']
    exploration = after['exploration_points'] - before['exploration_points']
    penalty = after['penalties'] - before['penalties']
    score_before, score_after = score(before), score(after)
    parts = []
    if banked:
        parts.append(f'Delivered ore added {banked} banked points.')
    if exploration:
        parts.append(f'A new depth milestone added {exploration} points.')
    if penalty:
        parts.append(f'A setback added a {penalty}-point deduction.')
        if before['banked_points'] + before['exploration_points'] - before['penalties'] - penalty < 0:
            parts.append('The score cannot fall below zero.')
    if not parts:
        parts.append('No points changed on this decision.')
        if after['cargo'] > before['cargo']:
            parts.append('Ore in the cart earns points only after delivery.')
    item = DecisionReplay(id=f"{agent['id']}:decision:{sequence}", agent_id=agent['id'], sequence=sequence,
        created_at=datetime.fromtimestamp(timestamp, timezone.utc).isoformat(), action=after['last_action'],
        stage=stage, reason=after['last_reason'], message=message, strategy_name=agent['strategy_name'],
        strategy_version=agent['strategy_version'], scope='contest' if contest else 'expedition',
        season_id=contest['season_id'] if contest else None, before=ReplayState(**before), after=ReplayState(**after),
        score_before=score_before, score_after=score_after, score_delta=score_after-score_before,
        banked_delta=banked, exploration_delta=exploration, penalty_delta=penalty, score_explanation=' '.join(parts))
    return {**item.model_dump(), 'owner': agent['owner']}


async def replay_indexes(db):
    await db.decision_replays.create_index('id', unique=True)
    await db.decision_replays.create_index([('owner', 1), ('agent_id', 1), ('sequence', -1)], unique=True)


def make_replay_router(db, wallet_auth):
    router = APIRouter(prefix='/api')

    @router.get('/agent/replay', response_model=ReplayPage)
    async def replay(authorization: Optional[str] = Header(None), before: Optional[int] = Query(None, ge=1),
                     limit: int = Query(80, ge=1, le=200), scope: Literal['all', 'contest', 'expedition'] = 'all',
                     change: Literal['all', 'gain', 'loss', 'steady'] = 'all'):
        uid = await wallet_auth.owner(authorization, require_holder=False)
        agent = await db.agents.find_one({'owner': uid}, {'_id': 0, 'id': 1})
        if not agent:
            return ReplayPage()
        base = {'owner': uid, 'agent_id': agent['id']}
        filters = {**base}
        if scope != 'all':
            filters['scope'] = scope
        if change != 'all':
            filters['score_delta'] = {'gain': {'$gt': 0}, 'loss': {'$lt': 0}, 'steady': 0}[change]
        query = {**filters}
        if before is not None:
            query['sequence'] = {'$lt': before}
        rows = await db.decision_replays.find(query, {'_id': 0, 'owner': 0}).sort('sequence', -1).limit(limit+1).to_list(limit+1)
        has_more = len(rows) > limit
        entries = [DecisionReplay(**r) for r in reversed(rows[:limit])]
        return ReplayPage(agent_id=agent['id'], total=await db.decision_replays.count_documents(filters),
                          recorded_total=await db.decision_replays.count_documents(base), has_more=has_more,
                          next_before=entries[0].sequence if has_more and entries else None, entries=entries)
    return router