# Minera — Product Requirements and Handoff

## Current specification — 2026-09-19

**Latest branding update (round 5, 2026-09-19): Minera supersedes Agent Miner as the product/token name in all current user-facing copy.** Historical requests and records below retain the old name for provenance only.

User request (verbatim): "Bro untuk nama ubah dari agent miner menjadi Minera, bro keren kan\n\nSama logo nya pake ini aja ya edit biar pas ukurannya model dll jangan asal tempel doang, udah itu aja". User supplied `Screenshot_20260919_233720_Chrome.jpg`: https://customer-assets-39nsmqrw.emergentagent.net/job_miner-hub-10/artifacts/ln3kotus_Screenshot_20260919_233720_Chrome.jpg.

Implemented: Minera name in header wordmark, home title/short about/tagline, footer, wallet/token/holder labels, guide/reward copy, browser/social/mobile metadata and API title/holder error message. Supplied pixel mascot retained, precisely masked to remove screenshot background/rings/decorations without deleting dark boots. Transparent full-body brand PNG uses original proportions; helmet/face crops remain legible at16–64px; centered full-mascot touch icons180/192/512px generated. Header uses38×48px desktop /31×40px mobile with `object-fit:contain`; footer uses22px/19px face mark. Favicon, manifest and touch icon configured. Source image and deterministic asset preparation script retained at `public/assets/branding/minera-original.jpg` and `scripts/prepare_minera_brand.py`.

Scope: identity/copy/assets only, no added features or gameplay/financial changes. Original sessions, agent IDs, DB state, strategy drafts and browser keys `agent-miner-access`, `agent-miner-wallets`, `agent-miner-draft-*` deliberately unchanged to preserve existing accounts/progress. Integration playbook consulted before the sole auth-adjacent edit (403 text only).

Verification: production build compiled successfully (`frontend/build-minera.log`). Desktop1920×800 and mobile390×844 screenshots: clean transparent logo, correct proportions, no overlap/overflow. All seven routes scanned for stale visible brand names (none), wallet dialog still opens, header link returns home, footer mark loads. Only historical/internal namespaces retain the old spelling.

**Home metric correction (round 4, 2026-09-19):** User request (verbatim): "Bro 1 lagi sama rewards holder asset di home di section agent on shift, ore collectes dll, itu ubah jadi Distribution, GLDx nya jadi nanti itu akan mencakup total gldx yg udah di distribusi ke seluruh holder via stonk.fun". Implemented: fourth home metric now labeled `Distribution`, displays the cumulative amount in `GLDx` for **all holders via Stonk.fun**, never the connected wallet's receipt total. Public `/api/rewards` metadata has `distribution_scope=all_holders` and `total_distributed_gldx=null` until authentic on-chain data is connected. UI reads this global field and refreshes every60s; unknown/error remains an em dash, not a fabricated zero. Individual rewards dashboard is unchanged. Future indexer must populate this global aggregate from actual finalized distributor receipts with signature deduplication, not game state or mock holdings.

**Latest copy correction (round 3):** Home about is now a brief crypto-style project introduction, NOT a long description of mechanics. This supersedes the earlier request for a longer home explanation. No changes to features, rewards, wallet behavior, or animation.

User request (verbatim): "Edit deskripsi home itu terlalu panjang, dan terlalu jelasin hal gak perlu, yg gue butuh tuh kata kata deskripsi aja buat projek ini apa bukan jelasin semua bro, Seperti about agent miner is Autounmous agent mining bla bla bla gitu paham gak ? Deskripsi about projek yg biasa di pake crypto, itu aja"

Implemented 2026-09-19: replaced both explanatory paragraphs with: "Agent Miner is an autonomous mining ecosystem on Solana. Independent agents bring its underground world to life, with GLDX rewards for eligible token holders." Existing headline, tagline, links and all functionality unchanged.

**Latest user-approved update (round 2) supersedes prior claim/Stock.fun notes:** platform is Stonk.fun, canonical website https://www.stonkfun.xyz. GLDX payouts are external automatic distributions, never an Agent Miner claim operation. Wallet and holder access stay simulated. Reward screen shows empty receipt records with unknown totals until authentic on-chain receipt ingestion is requested. Added immutable decision replay and continuous miner motion; verification below.

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

### Follow-up request (verbatim)
Sory bro bukan stock.fun tapi stonk.fun gldx nya

Oke build ini 1 Replay Keputusan: Tambahkan replay keputusan agent agar pemain bisa melihat penyebab skor naik atau turun , 2 konsep claimble gldx itu gak perlu ada pencetan tombol claim karna distribusi itu otomatis dari sistemnya si stonk.fun, dashboard rewards pengguna hanya menunjukan dia sudah menerima brp lewat onchain, 3 tolong lah di bagian depan home di Agent miner kata kata nya kasih deskripsi about yang panjang lah biar org tau konsepnya kaya apa, misal hold agent miner get Gldx, lalu jelasin agent nya sistemnya juga deskripsi diatas itu pake kata kata yang pas dan pro jangan pake pola x y z ngulang ngulang

Choice: **Pertahankan wallet simulasi; tampilkan riwayat kosong tanpa mengarang transaksi sampai pembacaan on-chain disambungkan**.

Additional input (verbatim): **Animasi minging, jangan ada jeda seperti lagging tbtb berenti lalu muncul lagi dengan posisi acak, buatlah benar benar smooth berjalan layaknya bot mining animasi asli tanpa ada jeda diam seperti saat ini**.

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
- No in-app demo/test/placeholder language or development-status wall. Project token may say Coming. Unknown amounts are em dashes. No claim or claimable concept: rewards are automatic external receipts.

## Architecture decisions
- React 19 + TypeScript 4.9.5, PixiJS 8.21, React Router, Shadcn/Radix and Sonner. Fonts Exo 2, DM Sans, JetBrains Mono.
- Preserved source frontend `src` and `public`, and core backend Python modules. Installed source's Pixi/TS dependencies through Yarn without replacing protected environment values. Removed conflicting template jsconfig, retained tsconfig.
- Routes: `/`, `/agent`, `/agent/replay`, `/strategy`, `/leaderboard`, `/rewards`, `/guide`.
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
2. **Platform naming resolved by user**: Stonk.fun, not Stock.fun. `https://stonk.fun` failed DNS; canonical `https://www.stonkfun.xyz` verified via its live product and terms. Live listings include GLDX reward pairs (e.g. GP, WOW). Brand Stonk.fun links to the working canonical site. Agent Miner token is still Coming; no Agent Miner-specific listing, mint, distributor, or integration is claimed verified.
3. **GLDX receipt ingestion intentionally not connected**: no on-chain indexer or actual transaction records. API exposes `chain_connected:false`, totals and timestamps `null`, empty transaction array. The UI never equates the server's mock holding with financial rewards. Future work should verify official GLDX/Agent Miner mints and distributor source, then index finalized incoming reward transfers with idempotent signatures. Do not build a claim service: Stonk.fun administers payouts. StonkFun terms state no guaranteed schedule/amount and apply issuer/jurisdiction restrictions.
4. **Original hosted DB not in GitHub**: source code/art recovered, not original live accounts and balances. Original progress needs a separately authorized database export/import and explicit wallet-linking migration. No evidence of any previous DB contents was available here.
5. **Mock recovery browser-bound**: retaining browser recovery data permits reconnect; clearing it loses access. Production recovery must rely on cryptographic wallet proof, not these mock capabilities.

## Prioritized backlog / next tasks
### P0 — before real funds, NOT part of selected simulated scope
- Platform name and canonical URL resolved; obtain Agent Miner-specific listing/distributor only when real receipt ingestion is requested.
- Verify Agent Miner and GLDX official mints, issuer terms, network/token program, restrictions and fee routing.
- Only upon a new user request, replace simulated connection with real wallet-signature ownership and on-chain holder checks; preserve account migration intentionally.
- Keep contest funding separate from Stonk.fun holder distributions; no invented returns, payout controls, or paid-power mechanic.
- Import original hosted DB only if provided and authorized; never claim source cloning migrated hosted data.

### P1 — visible follow-up features
- Decision replay implemented; next optional extension is side-by-side comparison of runs or strategy versions.
- Previous-season standings and personal season history.
- Shareable agent/discovery cards.
- Wallet re-connect recovery UX for expired capabilities; maintain current simulation boundaries.

### P2 — scale and polish
- Leaderboard pagination / own rank beyond 100; more mine biomes and cosmetic discoveries.
- Worker leader election and durable distributed rate limiting before multi-instance operation.
- Continuous miner animation implemented and verified. Continue profiling real-device frame pacing if further slowdown is reported.

## Latest handoff
Preview: https://miner-hub-10.preview.emergentagent.com
No keys, signatures, transfers or real token operations requested from user. Report that wallet/holding are simulated and chain receipt history deliberately empty; platform typo is resolved.

## Implemented — 2026-09-19, round 2

### Decision replay
- New private read-only `/api/agent/replay`, backed by `decision_replays`; authorization uses existing session-derived wallet owner, never client-supplied identity. Former holders can read their own records.
- Captures actual executions with stable lifetime sequence, before/after resources, action, rule reason, strategy/version, timestamp, contest/open scope, score transition and component deltas. No guessed reconstruction of earlier unrecorded decisions.
- Atomic agent-revision update includes pending replay outbox. Bounded bulk upserts keyed by immutable decision ID publish after successful CAS; retries are idempotent; matching revision clears pending records.
- Pagination newest window with chronological display and exclusive `before` cursor; scope/score-change filters. `limit` 1..200. Index includes owner+agent+sequence; response model removes internal owner and `_id`.
- New `/agent/replay` with before/after resources, score explanation, play/pause, speed, previous/next/restart, scrubber, filters, earlier pages and refresh. Linked from My Agent tab and telemetry. Empty first-decision history polls every 2s while agent active.
- Existing strategy and scoring engine unchanged; contest scoring boundaries are marked separately from open expeditions.

### Reward receipt model
- All claim buttons, claimable balances, projected rewards and manual pool withdrawal concepts removed. `/api/rewards/claim` removed (404).
- Public `/api/rewards` returns Stonk.fun metadata and automatic distribution mode. `/api/rewards/receipts` returns only authenticated wallet address plus empty/null receipt fields; no holder requirement for this read.
- Sidebar shows GLDX received; full dashboard shows total received, recorded transfers, last receipt and empty receipt history. Refresh, error/retry, public connect and wallet isolation states implemented.
- Canonical website verified via crawl, including GLDX paired listings; no external API/financial integration or fake transactions added.

### Home and animation
- Expanded professional English description above map: holding eligibility, automatic GLDX receipts, autonomous strategy, persistent expeditions, wallet access and contest independence. Existing original map/art/layout retained.
- Replaced server-clock/index-based position assignment with persistent agent-ID motion state. Updated goals continue from current position; delayed/reordered responses or skewed timestamps never reposition actors.
- Monotonic `performance.now` frame timing, 50ms delta cap, smooth acceleration/deceleration, cruise48–53 units/s and explicit54-unit/s step ceiling. No large catch-up jump after hidden tab/view pause.
- Continuous work poses, pickaxe swings, footsteps, cart motion and small local workstation trips rather than frozen sprites. Facing follows travel direction. Names fade on overlap rather than blink off. Removed actors are cleaned from stage.
- Frame cap60; cached spark/ember geometry avoids per-frame Graphics clearing. Original art uses nearest sprite texture scaling. Reduced-motion respected. Read-only `mine-canvas.minerSnapshot()` exposes render-position telemetry for continuity measurement.

### Round 2 verification and fixes
- Testing agent report `test_reports/iteration_2.json`, backend suite **15/15 passed**. Reviewed test changes (new replay tests + replacement of obsolete claim assertion with404 and receipts contract).
- Reported first-replay delay traced to 8s empty-history poll; now2s. Pure UI connect/create Aster/start/navigate replay produced first real record in **20.75s** (18s engine decision + worker/poll delay), with correct +10 depth points and resources.
- Reported motion sampling peak85.53 units/s: changed to monotonic render clock and explicit per-frame cap with lower cruise. Rechecked **41 seconds**, 275 samples, ten deliberately reordered/time-skewed/delayed world replies: max sampled speed **60.28 units/s**, max render-time speed47.15, max sampled displacement9.15, no missing actors or teleports.
- Pause freezes exact positions/phases/tool rotations; resume continues. Screenshot overflow lists empty at1920x800 and390x844 for home, mine, receipts, populated replay. Filters and null receipts verified in pure UI flow.
- `frontend/build-updates-final.log`: **Compiled successfully**, no warnings.
- All temporary UI QA agents cleaned by exact IDs; existing user agent `Gyat` and12 residents preserved. Cleanup details recorded in `test_reports/round2_followup.md`.