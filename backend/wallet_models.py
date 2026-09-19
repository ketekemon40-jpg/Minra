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

