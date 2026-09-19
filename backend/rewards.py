"""Read-only reward receipts. Unknown chain totals stay null; there is no claim/transfer operation."""
import os
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Header


class RewardInfo(BaseModel):
    asset: str = 'GLDX'
    asset_name: str = 'Gold xStock'
    network: str = 'Solana'
    platform: str = 'Stonk.fun'
    platform_url: str
    distribution_mode: str = 'automatic'
    distribution_basis: str = 'eligible_holdings'
    agent_required: bool = False
    contest_affects_holder_share: bool = False
    token_status: str = 'coming'
    chain_connected: bool = False


class RewardReceipt(BaseModel):
    signature: str
    amount: str
    received_at: str
    source: str


class ReceiptHistory(BaseModel):
    wallet_address: str
    asset: str = 'GLDX'
    total_received: Optional[str] = None
    receipt_count: int = 0
    last_received_at: Optional[str] = None
    observed_at: Optional[str] = None
    chain_connected: bool = False
    transactions: list[RewardReceipt] = Field(default_factory=list)


def make_rewards_router(wallet_auth):
    router = APIRouter(prefix='/api/rewards')

    @router.get('', response_model=RewardInfo)
    async def info():
        return RewardInfo(platform_url=os.environ['REWARD_PLATFORM_URL'])

    @router.get('/receipts', response_model=ReceiptHistory)
    async def receipts(authorization: Optional[str] = Header(None)):
        # Existing authentication validates the session, with no holder requirement for historical reads.
        _, wallet = await wallet_auth.current(authorization)
        # User explicitly chose an empty history until an actual on-chain indexer is connected.
        # Do not treat game ore, mock holder_amount, or arbitrary GLDX transfers as distributions.
        return ReceiptHistory(wallet_address=wallet['address'])
    return router