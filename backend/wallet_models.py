from pydantic import BaseModel, ConfigDict, Field
from typing import Literal, Optional


class WalletCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    provider: Literal['Phantom', 'Solflare', 'Backpack']


class WalletConnect(BaseModel):
    model_config = ConfigDict(extra='forbid')
    wallet_id: str = Field(min_length=8, max_length=80)
    recovery_capability: str = Field(min_length=32, max_length=200)


class WalletOut(BaseModel):
    wallet_id: str
    address: str
    provider: str
    holder_amount: int
    eligible: bool
    network: str = 'Solana'
    mode: str = 'simulated'
    token_status: str = 'coming'


class WalletCreated(WalletOut):
    recovery_capability: str


class WalletSession(BaseModel):
    token: str
    wallet: WalletOut
    expires_at: str


class RewardOut(BaseModel):
    status: str = 'coming'
    asset: str = 'GLDX'
    network: str = 'Solana'
    platform: str = 'Stock.fun'
    platform_url: str
    platform_verified: bool = False
    distribution_basis: str = 'pro_rata_holdings'
    agent_required: bool = False
    contest_affects_holder_share: bool = False
    period_hours: Optional[int] = None
    finances: None = None
    pool_balance: None = None
    estimated: None = None
    claimable: None = None
    fee_allocation: None = None
    fee_received: None = None
    transactions: list = Field(default_factory=list)
    contracts: dict = Field(default_factory=lambda: {'AGENT_MINER': None, 'GLDX': None, 'vault': None})