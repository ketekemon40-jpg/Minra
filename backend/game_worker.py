import asyncio
import copy
import time
from collections import defaultdict
from datetime import datetime, timezone
from strategies import preset, step, score
from strategy_models import GameState
from contest_logic import ACTION_BUDGET
from decision_replay import record_decision, replay_indexes
from pymongo import UpdateOne

LOCKS = defaultdict(asyncio.Lock)

def stamp(ts=None):
    return datetime.fromtimestamp(ts or time.time(), timezone.utc).isoformat()

def game_defaults(preference='balanced', preset_key=None):
    key = preset_key or {'balanced': 'balanced', 'deep': 'prospector', 'careful': 'guardian'}.get(preference, 'balanced')
    config = preset(key)
    return {'engine_version': 2, 'strategy': config, 'strategy_name': config['name'], 'strategy_version': 1,
            'strategy_updated_at': stamp(), 'game': GameState().model_dump(), 'contest': None,
            'previous_stage': 'basecamp', 'decision_cursor': 0, 'pending_events': [], 'pending_replays': []}

async def migrate(db):
    await replay_indexes(db)
    await db.strategy_history.create_index('id', unique=True)
    await db.contest_archive.create_index('id', unique=True)
    await db.contest_archive.create_index('season_id')
    await db.agents.create_index('contest.season_id')
    now = time.time()
    async for a in db.agents.find({'engine_version': {'$ne': 2}}, {'_id': 0}):
        values = game_defaults(a['preference'])
        elapsed = a.get('elapsed_before', 0) + (now - a['started_at'] if a['status'] == 'active' else 0)
        values['decision_cursor'] = int(elapsed // 18)
        await db.agents.update_one({'id': a['id'], 'engine_version': {'$ne': 2}}, {'$set': values})

async def publish_events(db, agent):
    for collection, field in [('events', 'pending_events'), ('decision_replays', 'pending_replays')]:
        records = agent.get(field, [])
        for offset in range(0, len(records), 500):
            operations = [UpdateOne({'id': r['id']}, {'$setOnInsert': r}, upsert=True) for r in records[offset:offset+500]]
            await db[collection].bulk_write(operations, ordered=False)
    if agent.get('pending_events') or agent.get('pending_replays'):
        await db.agents.update_one({'id': agent['id'], 'revision': agent['revision']},
                                  {'$set': {'pending_events': [], 'pending_replays': []}})

async def advance_game(db, original):
    async with LOCKS[original['id']]:
        agent = await db.agents.find_one({'id': original['id']}, {'_id': 0})
        if not agent or agent['is_bot']:
            return
        await publish_events(db, agent)
        now = time.time()
        c = copy.deepcopy(agent.get('contest'))
        if agent['status'] != 'active':
            if c and c['status'] == 'active' and now >= c['ends_at']:
                await db.agents.update_one({'id': agent['id'], 'revision': agent['revision']},
                    {'$set': {'contest.status': 'closed', 'contest.completed_at': stamp(c['ends_at'])}, '$inc': {'revision': 1}})
            return
        elapsed = agent['elapsed_before'] + now - agent['started_at']
        target = int(elapsed // 18)
        cursor = agent.get('decision_cursor', agent['step'])
        stop = min(target, cursor + 4000)
        if stop <= cursor:
            if c and c['status'] == 'active' and now >= c['ends_at']:
                await db.agents.update_one({'id': agent['id'], 'revision': agent['revision']},
                    {'$set': {'contest.status': 'closed', 'contest.completed_at': stamp(c['ends_at'])}, '$inc': {'revision': 1}})
            return
        game = copy.deepcopy(agent['game'])
        old_mined, old_deliveries = game['mined'], game['deliveries']
        stage, previous_stage = agent['stage'], agent.get('previous_stage', 'basecamp')
        events, replays = [], []
        for tick in range(cursor + 1, stop + 1):
            ts = agent['started_at'] + tick * 18 - agent['elapsed_before']
            if c and c['status'] == 'active' and ts >= c['ends_at']:
                c.update(status='closed', completed_at=stamp(c['ends_at']))
            seed = f"brass-hollow-v1:{c['season_id']}" if c and c['status'] == 'active' else 'open-mine-v1'
            previous_stage = stage
            before = game
            counted_contest = copy.deepcopy(c) if c and c['status'] == 'active' else None
            game, stage, message = step(agent['strategy'], game, seed)
            replays.append(record_decision(agent, tick, ts, before, game, stage, message, counted_contest))
            if c and c['status'] == 'active':
                c['actions_used'] += 1
                c.update(score=score(game), delivered=game['delivered'], banked_points=game['banked_points'],
                         exploration_points=game['exploration_points'], penalties=game['penalties'], incidents=game['incidents'])
                if c['actions_used'] >= ACTION_BUDGET:
                    c.update(status='completed', completed_at=stamp(ts))
            if tick > stop - 36:
                events.append({'id': f"{agent['id']}:game:{tick}", 'agent_id': agent['id'],
                    'name': agent['name'], 'avatar': agent['avatar'], 'is_bot': False,
                    'stage': stage, 'message': f"{message} {game['last_reason']}", 'created_at': stamp(ts)})
        expeditions = agent['expeditions'] + game['deliveries'] - old_deliveries
        values = {'game': game, 'contest': c, 'stage': stage, 'previous_stage': previous_stage,
                  'stage_started_at': agent['started_at'] + stop * 18 - agent['elapsed_before'],
                  'step': stop, 'decision_cursor': stop, 'ore': agent['ore'] + game['mined'] - old_mined,
                  'expeditions': expeditions, 'pending_events': events, 'pending_replays': replays,
                  'discoveries': sorted(set(agent['discoveries']) | {name for threshold, name in [(1,'pyrite'), (3,'quartz'), (6,'azurite')] if expeditions >= threshold})}
        result = await db.agents.update_one({'id': agent['id'], 'revision': agent['revision'], 'status': 'active'},
                                           {'$set': values, '$inc': {'revision': 1}})
        if result.modified_count:
            await publish_events(db, {**agent, **values, 'revision': agent['revision'] + 1})