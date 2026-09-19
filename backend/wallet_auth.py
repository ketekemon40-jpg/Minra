"""Explicitly simulated wallet identities. Never authorizes real funds or proves Solana ownership."""
import hashlib
import os
import secrets
import time
import uuid
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Header, HTTPException, Request
from typing import Optional
from wallet_models import WalletCreate, WalletConnect, WalletCreated, WalletOut, WalletSession


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def now():
    return datetime.now(timezone.utc)


def public_wallet(wallet):
    return WalletOut(wallet_id=wallet['id'], address=wallet['address'], provider=wallet['provider'],
                     holder_amount=wallet['holder_amount'], eligible=wallet['holder_amount'] > 0)


def base58_address():
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    raw = secrets.token_bytes(32)
    number, result = int.from_bytes(raw, 'big'), ''
    while number:
        number, remainder = divmod(number, 58)
        result = alphabet[remainder] + result
    return '1' * (len(raw) - len(raw.lstrip(b'\0'))) + result


class WalletAuth:
    def __init__(self, db):
        self.db = db
        self.ttl = int(os.environ['WALLET_SESSION_TTL_SECONDS'])
        self.recovery_ttl = int(os.environ['WALLET_RECOVERY_TTL_SECONDS'])
        self.initial_holding = int(os.environ['MOCK_HOLDER_AMOUNT'])
        self.limits = defaultdict(deque)
        self.router = APIRouter(prefix='/api')
        self.register_routes()

    async def indexes(self):
        await self.db.wallets.create_index('id', unique=True)
        await self.db.wallets.create_index('address', unique=True)
        await self.db.wallets.create_index('recovery_hash', unique=True)
        await self.db.wallet_sessions.create_index('token_hash', unique=True)
        await self.db.wallet_sessions.create_index('expires_at', expireAfterSeconds=0)

    def throttle(self, request, kind, limit):
        key = (request.client.host if request.client else 'unknown', kind)
        stamp = time.monotonic()
        for old_key in list(self.limits):
            if not self.limits[old_key] or self.limits[old_key][-1] < stamp - 60:
                del self.limits[old_key]
        queue = self.limits[key]
        while queue and queue[0] < stamp - 60:
            queue.popleft()
        if len(queue) >= limit:
            raise HTTPException(429, 'Please wait a moment before trying again.', headers={'Retry-After': '60'})
        queue.append(stamp)

    async def current(self, authorization):
        if not authorization or not authorization.startswith('Bearer '):
            raise HTTPException(401, 'Connect your wallet to continue.')
        session = await self.db.wallet_sessions.find_one(
            {'token_hash': digest(authorization[7:]), 'revoked': False, 'expires_at': {'$gt': now()}}, {'_id': 0})
        if not session:
            raise HTTPException(401, 'Reconnect your wallet to continue.')
        wallet = await self.db.wallets.find_one({'id': session['wallet_id'], 'revoked': False}, {'_id': 0})
        if not wallet:
            raise HTTPException(401, 'Reconnect your wallet to continue.')
        return session, wallet

    async def owner(self, authorization, require_holder=True):
        _, wallet = await self.current(authorization)
        if require_holder and wallet['holder_amount'] <= 0:
            raise HTTPException(403, 'Minera holdings are required to play.')
        return wallet['id']

    def register_routes(self):
        @self.router.post('/wallets', response_model=WalletCreated, status_code=201)
        async def create(data: WalletCreate, request: Request):
            if os.environ['WALLET_MODE'] != 'simulated':
                raise HTTPException(503, 'Wallet connection is unavailable.')
            self.throttle(request, 'create', 20)
            recovery = secrets.token_urlsafe(48)
            wallet = {'id': str(uuid.uuid4()), 'address': base58_address(), 'provider': data.provider,
                      'holder_amount': self.initial_holding, 'recovery_hash': digest(recovery),
                      'recovery_expires_at': now() + timedelta(seconds=self.recovery_ttl),
                      'revoked': False, 'created_at': now().isoformat(), 'mode': 'simulated'}
            await self.db.wallets.insert_one(wallet.copy())
            return WalletCreated(**public_wallet(wallet).model_dump(), recovery_capability=recovery)

        @self.router.post('/session', response_model=WalletSession)
        async def connect(data: WalletConnect, request: Request, authorization: Optional[str] = Header(None)):
            self.throttle(request, 'connect', 60)
            wallet = await self.db.wallets.find_one({'id': data.wallet_id, 'revoked': False,
                'recovery_hash': digest(data.recovery_capability), 'recovery_expires_at': {'$gt': now()}}, {'_id': 0})
            if not wallet:
                raise HTTPException(401, 'This wallet connection could not be restored.')
            if authorization and authorization.startswith('Bearer '):
                await self.db.wallet_sessions.update_one({'token_hash': digest(authorization[7:])}, {'$set': {'revoked': True}})
            token, expires = secrets.token_urlsafe(48), now() + timedelta(seconds=self.ttl)
            await self.db.wallet_sessions.insert_one({'id': str(uuid.uuid4()), 'wallet_id': wallet['id'],
                'token_hash': digest(token), 'created_at': now(), 'expires_at': expires, 'revoked': False})
            return WalletSession(token=token, wallet=public_wallet(wallet), expires_at=expires.isoformat())

        @self.router.get('/session/me', response_model=WalletOut)
        async def me(authorization: Optional[str] = Header(None)):
            _, wallet = await self.current(authorization)
            return public_wallet(wallet)

        @self.router.post('/session/disconnect')
        async def disconnect(authorization: Optional[str] = Header(None)):
            session, _ = await self.current(authorization)
            await self.db.wallet_sessions.update_one({'id': session['id']}, {'$set': {'revoked': True}})
            return {'disconnected': True}