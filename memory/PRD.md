# Agent Miner — Product Requirements and Handoff

## Current specification — 2026-09-19

This document supersedes source-repository requirements in `REPO_HISTORY.md`. The user owns Digmine and requested continuation, not a redesign. Imported source main commit: `a9a6640ac3a3488ab64176805487c926098587ef` from https://github.com/lasvegasworld18-tech/Digmine.

## Original problem statement (verbatim)

Bro clone repo ini semua sesuiakan sama https://github.com/lasvegasworld18-tech/Digmine

Itu adalag github gue projek gue mau gue lanjutin build disini

Namanya ubah jadi Agent Miner

Untuk tulisan di dalamnya edit juga beberapa jangan kebanyakan pake pola x, y, z, pola ai bgt itu kata katanya gak keliatan pro

Lalu ubah juga masalah bots nya jangan dintulis bots activenya dan jangan buat nama bot seperti test gitu, buat bot nya murni seperti player tapi tentu karna untuk pemanis web, masa sepi kan gak enak,

Lalu tolong masalah create agent dll itu harus konek wallet solana dulu baru bisa masuk jadi akun per wallet dan harus holding token Agent miner(coming) semenrara pake mockup aja dulu

Tampilan tetap semua org bisa view public tapi tetap perlu login wallet untuk bermain

Jangan tambahkan kata kata atau edit kata kata yg nenjerumus ke demo, butuh ini butuh ini dll, buat seperti sudah siap semua jangan ada kata kata kalau masih test dll

### Confirmed choices
- **Seluruh koneksi wallet dan kepemilikan token disimulasikan dulu**.
- Ambient characters: **Setuju, tampilkan sebagai agent dengan nama natural**. Do not claim they are human players.
- Additional request (verbatim): **Jika sudah selesai build beritahu kekurangan dan kasih solusi nya dan masalah gld robinhood ganti ke Gldx solana di stock.fun**.
- Conversation is Indonesian. Existing product UI stays English.

## Personas
1. Visitor: sees the live public mine, agents, guide, and contest without signing in.
2. Agent Miner holder: connects a wallet account, creates one agent, configures its strategy, follows persistent progress and enters a season.
3. Project owner: iterates on the source application with clear disclosure of off-chain boundaries and no fabricated financial activity.

## Core requirements (static)
- Preserve original cave bitmap, sprites, animated mining, dashboard layout, color palette, and existing game engine.
- Agent Miner name throughout active UI and metadata. Short professional copy rather than repetitive slogans.
- No bots-active metric or CREW BOT labels. Natural autonomous residents; details identify them accurately and contest excludes them.
- Public routes remain accessible. Creating/playing/configuring/entering requires wallet ownership of an account and positive server-side holder eligibility.
- One agent per wallet identity. Reconnect restores the account. Switching isolates data. Disconnect does not stop an eligible active expedition.
- Wallet connection and holding are explicitly simulated by user choice, not real Solana proof.
- GLDX on Solana replaces requested GLD. No invented mint, rewards, fee receipts, or successful financial claim.
- No in-app demo/test/placeholder language or development-status wall. Project token may say Coming. Unknown amounts are em dashes, and claim stays disabled.

## Architecture decisions
- React 19 + TypeScript 4.9.5, PixiJS 8.21, React Router, Shadcn/Radix and Sonner. Fonts Exo 2, DM Sans, JetBrains Mono.
- Preserved source frontend `src` and `public`, and core backend Python modules. Installed source's Pixi/TS dependencies through Yarn without replacing protected environment values. Removed conflicting template jsconfig, retained tsconfig.
- Routes: `/`, `/agent`, `/strategy`, `/leaderboard`, `/rewards`, `/guide`.
- FastAPI under `/api`, MongoDB using existing MONGO_URL/DB_NAME, supervisor-managed services. Source deterministic mining/strategy/contest engine retained.
- `wallet_auth.py` adds simulated server-owned wallet identities. Provider choices Phantom, Solflare, Backpack are interface simulations, not adapters.
- Wallet addresses generated from 32 random bytes encoded as Base58, with no Solana keys or signing ability. Recovery capability and bearer tokens are SHA256 hashed in MongoDB, never stored plaintext on server.
- Account owner = wallet's stable UUID, not session ID or a submitted public address. Existing anonymous-session API no longer creates accounts without a wallet identity.
- Recovery TTL 365 days; session TTL 24 hours; application expiry checks + Mongo TTL cleanup; revocation on switch/disconnect. Basic IP-based creation/connect throttles.
- Session bearer in sessionStorage `agent-miner-access`. Simulated wallet recovery capabilities in localStorage `agent-miner-wallets`. Browser clearing loses these mock identities; not cross-device wallet authentication.
- `MOCK_HOLDER_AMOUNT=1000` is a server-side simulation fixture, not a token balance display. Holding > 0 gates writes. No public endpoint can change it. Worker pauses agents losing holder access; read-only own-agent lookup remains allowed.
- Mongo output documents exclude `_id`, and typed response models prevent credentials/internal ownership fields leaking.
- React wallet context handles session restore, connect, switch, disconnect and 10-second eligibility polling. In-flight private loads check session/generation and loaded account before rendering, preventing stale account display.

## Implemented — 2026-09-19
- Imported original mine assets, natural 12-agent roster and animations. Brand, document metadata, creation flow and all six routes now use Agent Miner.
- Resident agents named Flint, Moss, Copper, Echo, Pip, Bramble, Rivet, Nova, Dusty, Fern, Ember, Atlas. Uniform AGENT roster tags; detailed identity says autonomous resident vs wallet agent. No resident entries in contest.
- Replaced anonymous creation with wallet/holder-gated flow. New wallet from Connect to play proceeds to creation; reconnecting an existing wallet restores its agent instead of opening duplicate creation.
- Stable one-agent-per-wallet uniqueness, session expiry/revocation, input injection rejection, server holding checks, worker auto-pause on lost eligibility.
- Existing start/pause/resume, offline progression, journal, discoveries, presets, advanced IF/THEN rules, evaluation, version history, weekly 600-decision contest preserved.
- Professional copy refreshed across Mine, My Agent, Strategy, Contest, Guide, Rewards and dialogs. No UI demo/test language.
- GLDX / Gold xStock / Solana labels and reward formula updated. User-requested Stock.fun provided as reference link only. Null finance metadata, no financial transactions and disabled claim remain intentional.
- Responsive wallet panel, long address wrapping, account switching, and all existing page layouts verified.

## Verification
- Testing agent: `test_reports/iteration_1.json`; `backend/tests/test_wallet_agent_flows.py`, **11/11 passing**. Covers public access, input forgery, switch/disconnect revocation, wallet uniqueness, zero-holding mutation gates, worker auto-pause, strategy/contest, reward restrictions. Test fixtures clean only their own generated records.
- Tested frontend six routes, provider switching, reconnect, mining lifecycle, strategies, leaderboard, public access and map rendering at **1920x800** and **390x844**. No horizontal overflow found.
- Fixed both reported hook dependency warnings: stable walletId dependency and hoisted typed agent response. Also suppress stale agent render immediately on wallet switch.
- Final `frontend/build-final.log`: **Compiled successfully**, no lint warnings.
- Final main-agent browser smoke: connect→create Rowan→start; switch to independent Solflare account; restore Phantom's Rowan; navigate all routes at 390px; disconnect to public mode; reconnect without duplicate create dialog. All passed. Exact generated wallet identities subsequently cleaned without touching residents or unrelated users.
- Original Pixi rendering capped at 45 FPS. Browser automation emits non-blocking WebGL ReadPixels warnings; no application synchronous pixel readback exists. Canvas renders and animates correctly; no renderer rewrite made merely to hide browser warnings.

## Known boundaries and solutions
1. **SIMULATED wallets/holdings**: no real adapter, signed challenge, RPC balance, or on-chain ownership. Keep this mode as requested. Any future real-money phase requires signed nonces, official Agent Miner mint, Token-2022-aware holdings lookup and invalidation/reconciliation. Do not describe the current gate as genuine Solana authentication.
2. **Stock.fun discrepancy**: live https://stock.fun inspected during build is a congress/insider trade tracking product. Source project previously referenced Stonk.fun / stonkfun.xyz, which is a different platform. GLDX token existence does not verify support or fee integration at either service. Current UI only links Stock.fun, never claims it is a verified launch/fee partner. Before integration obtain the precise intended platform/listing and official fee mechanics.
3. **GLDX finance not connected**: no claim, fee ingestion, allocation ledger, funded prize or settlement. GLDX confirmed as Gold xStock tracking SPDR Gold Shares via https://www.kraken.com/xstocks/gldx and https://assets.backed.fi/ research. Do not hardcode a candidate mint without issuer verification. Verify Token-2022 properties, eligibility restrictions, funding rules and source records before actual distributions.
4. **Original hosted DB not in GitHub**: source code/art recovered, not original live accounts and balances. Original progress needs a separately authorized database export/import and explicit wallet-linking migration. No evidence of any previous DB contents was available here.
5. **Mock recovery browser-bound**: retaining browser recovery data permits reconnect; clearing it loses access. Production recovery must rely on cryptographic wallet proof, not these mock capabilities.

## Prioritized backlog / next tasks
### P0 — before real funds, NOT part of selected simulated scope
- Resolve Stock.fun vs Stonk.fun and obtain official intended product URL.
- Verify Agent Miner and GLDX official mints, issuer terms, network/token program, restrictions and fee routing.
- Only upon a new user request, replace simulated connection with real wallet-signature ownership and on-chain holder checks; preserve account migration intentionally.
- Establish separate contest funding and holder allocation ledger before transfers; no invented returns or paid-power mechanic.
- Import original hosted DB only if provided and authorized; never claim source cloning migrated hosted data.

### P1 — visible follow-up features
- Agent decision replay with explanation of score changes.
- Previous-season standings and personal season history.
- Shareable agent/discovery cards.
- Wallet re-connect recovery UX for expired capabilities; maintain current simulation boundaries.

### P2 — scale and polish
- Leaderboard pagination / own rank beyond 100; more mine biomes and cosmetic discoveries.
- Worker leader election and durable distributed rate limiting before multi-instance operation.
- Profile low-end mobile Pixi rendering if a real-device slowdown is reported.

## Latest handoff
Preview: https://miner-hub-10.preview.emergentagent.com
No keys, signatures, transfers or real token operations requested from user. Report simulated boundaries and Stock.fun discrepancy to the owner, without adding development warnings to the interface.