Here's the updated action plan with all requested changes:

markdown

# Project Action Plan: WooSarr (Plex ↔ Discord Role Library Sync)

> **How to use this document (read first, AI agents):**
>
> 1. Work through phases in order. Do not start a phase until its dependencies are `[x]`.
> 2. Each task has an ID (e.g., `P2-03`). Reference IDs in commits and logs.
> 3. Mark tasks `[x]` when their **Acceptance** line is verifiably met. Never mark done on "code written".
> 4. If a decision in **§2 Decisions** is marked `OPEN`, stop and ask the human unless a default is given. Record the answer there.
> 5. Treat **§3 Non-negotiables** as hard constraints that override convenience.
> 6. Verify any external API behavior against the **§12 References** before coding against it. Mark `VERIFY` items resolved when confirmed.
> 7. Edit this file as the project evolves; keep IDs stable (don't renumber).

---

## 1. Project Summary

A single Docker container, installable on Unraid, that:

- Authenticates with a Plex server via OAuth (no stored credentials, no hardcoded tokens).
- Runs a Discord bot in a Discord server.
- Serves a configuration web UI on **port 2000**.
- Automatically grants/removes Plex library access for Plex users based on their Discord roles, **additively** (union of all role grants), respecting per-library **exemptions**, and only for Plex users with a **linked Discord account**.
- Provides pages for users, roles, libraries, and logs, plus setup assistants for Discord and Plex.

---

## 2. Decisions (edit freely)

| ID  | Decision                                       | Status      | Default / Answer                                                                                                                                                                                                                                                                                                                                                                                                        |
| --- | ---------------------------------------------- | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| D1  | Backend language/framework                     | **DECIDED** | Python 3.12 + FastAPI + `discord.py` + **`python-plexapi`** (docs reviewed: has PIN/OAuth + JWT login, user listing, per-user shared-library read via `MyPlexUser.servers[].sections()`, and `MyPlexAccount.updateFriend()` for share updates). The plexapi.dev TypeScript SDK (`@lukehagar/plexjs`) was rejected: it is auto-generated, beta, and no library-sharing methods were found in its documented method list. |
| D1a | Frontend/backend type sharing                  | DEFAULT     | Generate TypeScript types from FastAPI's OpenAPI schema (e.g., `openapi-typescript`) so the React UI gets typed API calls without a shared language                                                                                                                                                                                                                                                                     |
| D1b | Plex adapter boundary                          | DEFAULT     | All Plex access goes through a `PlexGateway` interface (our own code), so the library can be swapped or mocked without touching the sync engine                                                                                                                                                                                                                                                                         |
| D2  | Frontend                                       | DEFAULT     | React + TypeScript + Vite, built to static files served by FastAPI (single container, single port)                                                                                                                                                                                                                                                                                                                      |
| D3  | Database                                       | DEFAULT     | SQLite in `/config` (SQLAlchemy + Alembic migrations)                                                                                                                                                                                                                                                                                                                                                                   |
| D4  | How Plex users link to Discord accounts        | **DECIDED** | User self-service via Discord `/link` slash command. Command prompts user to either (a) enter their Plex username directly, or (b) authenticate via Plex OAuth for automatic username capture. After linking, do not store Plex credentials or tokens — only the plex_user_id ↔ discord_user_id mapping. We trust users (to a point). Admin can manually link/unlink in UI as fallback.                                |
| D5  | Secret storage                                 | DEFAULT     | Secrets encrypted at rest (Fernet/AES-GCM) in the DB. Master key generated on first run, stored at `/config/secrets/master.key` (mode 0600), or supplied via env var / Docker secret if provided. Never baked into image or repo.                                                                                                                                                                                       |
| D6  | Discord bot token entry                        | DEFAULT     | Entered once via Setup Assistant (Discord has no OAuth flow that issues a bot token). Stored encrypted per D5.                                                                                                                                                                                                                                                                                                          |
| D7  | Web UI authentication (who can open port 2000) | **DECIDED** | First-run setup wizard generates an initial admin user (username + password). Subsequent logins use local credentials. Also support SAML auth to integrate an external IdP for organizations.                                                                                                                                                                                                                           |
| D8  | Role-change trigger mechanism                  | DEFAULT     | Discord gateway events (`on_member_update`, `on_guild_role_update`, `on_guild_role_delete`) + periodic full reconcile (default every 15 min, configurable) as a safety net                                                                                                                                                                                                                                              |
| D9  | Library identifier                             | DEFAULT     | Plex library section key + server machine identifier (stable across renames); store title for display                                                                                                                                                                                                                                                                                                                   |
| D10 | Project/app name                               | **DECIDED** | WooSarr                                                                                                                                                                                                                                                                                                                                                                                                                 |
| D11 | Multiple Discord guilds / Plex servers         | DEFAULT     | Out of scope for v1: one guild, one Plex server                                                                                                                                                                                                                                                                                                                                                                         |
| D12 | Dry-run mode                                   | DEFAULT     | Included: global toggle that logs intended changes without applying them                                                                                                                                                                                                                                                                                                                                                |

---

## 3. Non-negotiables (from spec)

- **N1** No hardcoded credentials or tokens anywhere (code, image, template defaults, tests, logs, git history).
- **N2** Plex auth via OAuth (Plex PIN/OAuth flow).
- **N3** Role library grants are **additive**: a user's libraries = union of libraries from all their roles (+ manual grants + exempt-preserved state). Removing one role must never remove a library still granted by another role.
- **N4** Library **exemptions**: an exempt library is never added or removed by role changes; its current state per user is preserved.
- **N5** Only modify Plex users that have a **linked Discord account**.
- **N6** Plex's share update API may **replace** a user's full library list (python-plexapi's `updateFriend(sections=...)` appears to take the complete target set; `removeSections=True` removes all shares — confirm in P0-03). Always read current state, compute the full target set, then write. Never send a partial set. Revoking a user's _last_ library likely requires `removeSections=True` rather than an empty list (`sections=None` is the default and probably means "no change") — handle explicitly.
- **N7** Sensitive data (tokens, credentials) never appears in logs, API responses, or UI (show masked / "set" indicator only).
- **N8** UI: light and dark modes, colorblind mode option(s), purple as a featured color, sidebar navigation.

---

## 4. Architecture (proposed)

Container (single process group, port 2000)
├── FastAPI app
│ ├── REST API (/api/\*) ← consumed by the React UI
│ ├── Static UI (/) ← built React bundle
│ └── Auth/session middleware
├── Plex service ← OAuth, server/libraries/users/shares
├── Discord service (discord.py) ← runs in same event loop / managed task
├── Sync engine ← pure logic: compute desired state, diff, apply
├── Scheduler ← periodic reconcile
├── Secrets manager ← encrypt/decrypt, masking
├── Logging ← structured, redacting, persisted + streamable
└── SQLite (/config/app.db)

yaml

Suggested repo layout:
/backend (Python 3.12, FastAPI)
/app
api/ services/plex/(PlexGateway + python-plexapi impl) services/discord/ sync/ core/(config,secrets,logging) models/ main.py
/tests
alembic/
/frontend (React + TypeScript)
/src (pages, components, theme, api client, generated/ ← types from OpenAPI)
/docker
Dockerfile entrypoint.sh healthcheck
/unraid
template.xml
docs/
action-plan.md

ruby

### Data model (initial; adjust during P1)

- `settings` (key, value, is_secret)
- `secrets` (name, ciphertext, created_at, rotated_at)
- `users` (id, username, password_hash, is_admin, created_at) — local UI auth users
- `plex_users` (plex_id, username, email, thumb, is_home/managed, last_seen_sync)
- `discord_links` (plex_user_id ↔ discord_user_id, method[manual|self_username|self_oauth], linked_at, linked_by_discord_id)
- `discord_roles_cache` (role_id, name, color, position, managed)
- `discord_members_cache` (discord_user_id, display_name, role_ids[])
- `libraries` (section_key, title, type, is_exempt)
- `role_library_map` (role_id, library_id)
- `manual_grants` (plex_user_id, library_id) — admin-added access that role logic must not strip
- `library_state` (plex*user_id, library_id, source[role|manual|external], last_applied_at) — tracks \_why* access exists
- `sync_runs` / `audit_log` (timestamp, trigger, actor, plex_user, library, action, result, dry_run)
- `app_logs` (timestamp, level, component, message, context_json)

---

## 5. Sync Engine Rules (core logic — implement as pure, unit-tested functions)

For each Plex user **U with a linked Discord account** (N5):
role_libs = union( role_library_map[r] for r in U.discord_roles )
manual_libs = manual_grants[U]
current = libraries currently shared with U on Plex # read live (N6)
exempt = set of libraries flagged exempt

managed_universe = all libraries that appear in ANY role_library_map entry, minus exempt
desired_managed = (role_libs ∪ manual_libs) ∩ managed_universe
preserved = current ∩ (exempt ∪ not_in_managed_universe) # don't touch unmanaged/exempt
target = desired_managed ∪ preserved ∪ (manual_libs) # full set to write

if target != current and not dry_run:
write target as the COMPLETE library list for U # N6
log every add/remove with reason and source

markdown

Edge cases to cover with tests:

- User has two roles granting the same library; one role is removed → library stays.
- Library was granted manually and also by a role; role removed → library stays (manual).
- Exempt library currently shared → stays after role removal. Exempt library not shared → not added by role addition.
- Role renamed → no access change. Role deleted → treated as removal of that role for all holders.
- Role's library mapping edited (library added/removed) → reconcile all holders of that role.
- Library removed from Plex / renamed → mappings cleaned/updated gracefully.
- User has no linked Discord account → skipped entirely, logged at debug.
- Linked Discord user left the server → no role-based grants; decide policy (default: remove role-derived grants, keep manual + exempt). Mark as setting.
- Target set is empty (user loses their last managed library and has no preserved/manual/exempt libraries) → use the "remove all shares" path (`removeSections=True`), not an empty list; verify per P0-03(c).
- `Section.shared` is false for a library listed under the user's server share → treat as not shared.
- Plex API returns error mid-run → no partial writes; retry with backoff; log.
- Rate limits (Plex and Discord) respected.
- Pre-existing shares not created by this app: treated as `external`; preserved unless library is in managed universe (document this behavior clearly in UI).

---

## 6. Phased Task List

Legend: `[ ]` todo · `[~]` in progress · `[x]` done · `VERIFY` = confirm against docs first

### Phase 0 — Discovery & Decisions

- [x] **P0-01** Resolve remaining OPEN decisions with the human. **Acceptance:** §2 table updated.
- [x] **P0-02** `VERIFY` Plex auth with python-plexapi: `MyPlexPinLogin(oauth=True)` (`oauthUrl(forwardUrl=...)`, polling/callback modes) and `MyPlexJWTLogin` (keypair, `verifyJWT`/`refreshJWT`; needs `pyjwt[crypto]`). Decide which is used for the stored admin session and how the keypair/token is stored encrypted. Confirm required headers (`X-Plex-Client-Identifier`, product). **Acceptance:** short notes in `docs/plex-notes.md` with a working example.
- [x] **P0-03** `VERIFY` (gate for all Plex write code) Spike script against a real/test Plex server using python-plexapi. Answer each, with notes in `docs/plex-notes.md`:
  - (a) Does `updateFriend(user, server, sections=[...])` **replace** the user's library set or merge?
  - (b) Does `MyPlexServerShare.sections()` return only shared sections, or all sections with a `shared` flag? (Filter on `Section.shared` until proven.)
  - (c) How to revoke the **last** library (`removeSections=True` vs empty list)?
  - (d) Does updating sections reset `allowSync`, `allowChannels`, `allowCameraUpload`, or content filters (`filterMovies/Television/Music`)? If so, read and re-send existing values.
  - (e) Does `updateFriend` work for Plex Home / managed users (`home`/`restricted`), or are `createHomeUser`/`createExistingUser` needed?
  - (f) How to obtain the server's `machineIdentifier` and map `LibrarySection` ↔ shared `Section.key`.
  - **Acceptance:** tested script proves read-then-write preserves existing access (N6) and documents answers (a)–(f).
- [x] **P0-04** Choose Plex SDK. **Resolved:** `python-plexapi` (see D1). Reconfirm only if P0-03 uncovers a blocker; fallback is raw HTTP to plex.tv behind `PlexGateway`.
- [x] **P0-05** `VERIFY` Discord requirements: required gateway intents (Guild Members is privileged), bot permissions, slash commands, and OAuth2 scopes if used for D4. **Acceptance:** `docs/discord-notes.md`.
- [x] **P0-06** Confirm Unraid template requirements (appdata path, port mapping, icon, WebUI link). **Acceptance:** notes in `docs/unraid-notes.md`.

### Phase 1 — Foundation

_Depends on: P0-01, P0-04_

- [x] **P1-01** Initialize git repository with `.gitignore`, commit conventions, and initial commit. Push to GitHub. **Acceptance:** repo exists on GitHub with clean history and no secrets.
- [x] **P1-02** Scaffold repo layout (§4), tooling (lint, format, type-check, pytest, vitest), pre-commit with secret scanning. **Acceptance:** CI-style local command runs green on empty project.
- [x] **P1-03** Config loader: env + `/config` paths, no secrets in env defaults. **Acceptance:** app boots with only `/config` volume.
- [x] **P1-04** DB models + Alembic migrations (§4 data model). **Acceptance:** fresh DB migrates; migration tests pass.
- [x] **P1-05** Secrets manager (N1, N7, D5): encrypt/decrypt, key generation, rotation function, masking helper. **Acceptance:** unit tests; key file perms 0600; plaintext never in DB.
- [x] **P1-06** Logging system: structured logs, levels, **redaction filter** for tokens/secrets, persisted to DB + rotating file, queryable/streamable. **Acceptance:** test proves a known token string is redacted in all outputs.
- [x] **P1-07** FastAPI skeleton, health endpoint, error handling, API versioning, session handling. **Acceptance:** `/api/health` returns 200 on port 2000.
- [ ] **P1-08** OpenAPI → TypeScript type pipeline (D1a): script exports FastAPI's OpenAPI schema and generates `frontend/src/generated/` types; CI/local check fails if generated types are stale. **Acceptance:** changing an API response model changes the generated types and breaks the frontend build until fixed.

### Phase 2 — Containerization (early, so it's always deployable)

_Depends on: P1-07_

- [ ] **P2-01** Multi-stage Dockerfile (build UI, slim runtime, non-root user, PUID/PGID support for Unraid). **Acceptance:** image builds; runs; persists to `/config`.
- [ ] **P2-02** Healthcheck + graceful shutdown. **Acceptance:** `docker ps` shows healthy; SIGTERM stops cleanly.
- [ ] **P2-03** Unraid Community Apps template XML (port 2000, `/config` → `/mnt/user/appdata/woosarr`, WebUI URL, icon, description). **Acceptance:** template validates; installs via "Add Container" on test Unraid.
- [ ] **P2-04** GitHub Actions workflow to build and publish Docker image to GHCR/Docker Hub on push to main and tagged releases. Versioned tags, multi-arch if feasible. **Acceptance:** tagged release produces a pullable image; workflow runs on push.

### Phase 3 — Plex Integration

_Depends on: P1-05, P0-02, P0-03_

- [ ] **P3-00** Define `PlexGateway` interface (D1b): `list_users()`, `list_libraries()`, `get_user_shared_library_keys(user)`, `set_user_libraries(user, full_set)`, plus auth methods; implement with python-plexapi and a fake in-memory implementation for tests. **Acceptance:** sync engine tests run entirely against the fake.
- [ ] **P3-01** Plex OAuth login flow using `MyPlexPinLogin(oauth=True)` (and JWT refresh per P0-02): start, poll/callback via API endpoints (not blocking threads on the request path), store token encrypted, handle expiry/revocation (N1, N2). **Acceptance:** can sign in via browser; no token appears in logs/UI.
- [ ] **P3-02** Server discovery/selection (list owned servers, choose one, store machine identifier). **Acceptance:** selected server persisted.
- [ ] **P3-03** Library sync: fetch libraries (key, title, type), upsert to DB, handle removals/renames. **Acceptance:** libraries match Plex.
- [ ] **P3-04** User sync: fetch all users with access (incl. managed/home), store, mark removed. **Acceptance:** users match Plex.
- [ ] **P3-05** Per-user library share read + write via `PlexGateway`, using **read-then-write full set** (N6): read `MyPlexUser.servers[].sections()` filtered on `Section.shared`; write via `updateFriend(sections=full_set)`; use `removeSections=True` only when the target set is empty; preserve existing `allowSync/allowChannels/allowCameraUpload/filters` per P0-03(d); handle managed users per P0-03(e). **Acceptance:** integration test: add one library to a user without losing existing ones; remove one without affecting others; remove the last library; settings/filters unchanged afterward.
- [ ] **P3-06** Error handling: retries, backoff, rate limiting, connection-lost state surfaced in UI. **Acceptance:** simulated failures logged and recovered.
- [ ] **P3-07** Async integration: python-plexapi is synchronous (`requests`). Run all Plex calls in a thread pool/executor (or dedicated worker) so they never block the FastAPI/discord.py event loop; enforce per-user serialization. **Acceptance:** a slow Plex call does not stall API responses or the Discord gateway heartbeat.

### Phase 4 — Discord Integration

_Depends on: P1-05, P0-05_

- [ ] **P4-01** Bot lifecycle manager: start/stop/restart from settings without container restart; token from secrets manager. **Acceptance:** bot connects/disconnects via API call.
- [ ] **P4-02** Guild selection + cache of roles and members (requires Members intent). **Acceptance:** roles/members appear in DB.
- [ ] **P4-03** Event handlers: member role add/remove, role update, role delete, member join/leave → emit events to sync engine queue. **Acceptance:** events logged and queued.
- [ ] **P4-04** Account linking per D4: `/link` slash command that prompts user to either enter their Plex username directly or authenticate via Plex OAuth for automatic username capture. After linking, discard credentials/tokens — store only the plex_user_id ↔ discord_user_id mapping. Also provide manual link/unlink API for admins. **Acceptance:** a Plex user can be linked via both methods; link audit logged with method; no credentials stored after linking.
- [ ] **P4-05** Reconnect/resume handling and permission-error reporting (missing intent, missing permissions) surfaced in UI. **Acceptance:** clear error messages shown.

### Phase 5 — Sync Engine

_Depends on: P3-05, P4-03, P4-04_

- [ ] **P5-01** Implement pure desired-state calculator per §5 with exemptions, manual grants, and N3–N6. **Acceptance:** unit tests cover every edge case listed in §5; 100% branch coverage on this module.
- [ ] **P5-02** Diff + apply layer with dry-run (D12), per-user transactional behavior, and audit logging (who/what/why). **Acceptance:** dry-run produces identical plan without writes.
- [ ] **P5-03** Event-driven triggers (D8): debounce/queue role events per user; handle role modified/deleted and mapping changes (reconcile affected users). **Acceptance:** integration tests for each trigger.
- [ ] **P5-04** Periodic full reconcile + manual "Sync now" (per-user and global). **Acceptance:** drift introduced manually in Plex is corrected only where policy says so.
- [ ] **P5-05** Concurrency control (single-writer lock per user/global) and idempotency. **Acceptance:** running twice yields no changes the second time.

### Phase 6 — Web UI: Shell, Auth, Theming

_Depends on: P1-07, P3-01_

- [ ] **P6-01** UI auth per D7: first-run setup wizard to create initial admin user (username + password). Subsequent logins use local credentials. Support SAML auth for external IdP integration. Session cookies, CSRF protection, logout. **Acceptance:** fresh container → setup wizard → admin login; SAML config option available.
- [ ] **P6-02** App shell with **sidebar navigation** (Dashboard, Users, Roles, Libraries, Logs, Settings, Setup). **Acceptance:** responsive, keyboard accessible.
- [ ] **P6-03** Theme system: light/dark (follow OS + manual toggle), purple as featured accent, **colorblind mode(s)** (e.g., deuteranopia/protanopia/tritanopia-safe palettes; never rely on color alone — add icons/text). **Acceptance:** all pages pass WCAG AA contrast in every mode; theme persisted.
- [ ] **P6-04** Shared components: data tables (search/sort/filter), modals, toasts, confirmation dialogs, status badges, empty states. **Acceptance:** Storybook or documented examples.

### Phase 7 — Web UI: Feature Pages

_Depends on: P6-02, P5-02_

- [ ] **P7-01** **Users page:** list Plex users with linked Discord account, Discord roles, and Plex libraries shared. Show flag indicating if user authenticated to link (OAuth vs username entry). Actions: admin can link/unlink Discord, **add/remove libraries manually** to one or multiple users (bulk select), show access source (role/manual/exempt/external). **Acceptance:** manual grants persist across role changes (N3, manual_grants); link method visible; admin unlink works.
- [ ] **P7-02** **Roles page:** list Discord server roles (members count, color); assign/unassign Plex libraries to each role; show preview of impact ("N users will gain/lose X") before saving. **Acceptance:** saving a mapping triggers reconcile (P5-03).
- [ ] **P7-03** **Libraries page:** show Plex server info + libraries; toggle **exempt** per library with explanation; show which roles reference each library. **Acceptance:** exempt flag respected by engine (N4).
- [ ] **P7-04** **Dashboard:** connection status for Plex and Discord, last sync, pending errors, dry-run indicator. **Acceptance:** reflects live status.
- [ ] **P7-05** **Settings page:** theme, reconcile interval, dry-run toggle, policy for users who leave the server, secret rotation (masked, replace-only), log retention, SAML config. **Acceptance:** no secret ever returned by API (N7).

### Phase 8 — Logs Page & Observability

_Depends on: P1-06, P6-02_

- [ ] **P8-01** Logs page: live tail (SSE/WebSocket), filter by level/component/user/date, search, export. **Acceptance:** handles 10k+ lines smoothly (pagination/virtualization).
- [ ] **P8-02** Audit view for permission changes (who/what/why/when, dry-run flag). **Acceptance:** every Plex share change appears with its triggering event.
- [ ] **P8-03** Log level control + retention/rotation. **Acceptance:** debug level reveals detailed sync decisions without exposing secrets.

### Phase 9 — Setup Assistants

_Depends on: P6-02, P3-01, P4-01_

- [ ] **P9-01** **Discord bot creation wizard:** step-by-step (create application, add bot, enable Members intent, copy token, invite URL generated with correct permissions/scopes, choose guild); validates token and intents live; clear failure messages. **Acceptance:** a new user can complete setup without leaving the wizard except for Discord's site.
- [ ] **P9-02** **Plex integration wizard:** OAuth sign-in, server pick, library fetch, permission check, test share-read. **Acceptance:** completes end to end; failures give actionable guidance.
- [ ] **P9-03** First-run onboarding flow tying P9-01/02 together and gating the rest of the UI until complete. **Acceptance:** fresh container → working system via UI only.

### Phase 10 — Security Hardening

_Can run in parallel from Phase 3 onward; must finish before release_

- [ ] **P10-01** Secret scan of repo/image/history (e.g., gitleaks, trufflehog). **Acceptance:** zero findings.
- [ ] **P10-02** Log redaction audit across all code paths, including exception traces and HTTP client debug logs. **Acceptance:** automated test with canary secrets.
- [ ] **P10-03** Web security: CSRF, secure/HttpOnly/SameSite cookies, security headers, input validation, rate limiting on auth endpoints, CORS locked down. **Acceptance:** checklist passed.
- [ ] **P10-04** Document reverse-proxy/HTTPS recommendation (port 2000 is HTTP by default). **Acceptance:** in README.
- [ ] **P10-05** Least-privilege: non-root container, minimal image, dependency audit (pip-audit / npm audit). **Acceptance:** no high/critical vulns unresolved.
- [ ] **P10-06** Threat-model pass: account-linking spoofing (can a user claim someone else's Plex account?), privilege escalation via Discord roles, token theft from `/config`. **Acceptance:** `docs/threat-model.md` with mitigations.

### Phase 11 — Testing & QA

- [ ] **P11-01** Unit tests (sync engine, secrets, redaction) — see P5-01.
- [ ] **P11-02** Integration tests with mocked Plex/Discord APIs. **Acceptance:** full role-add/remove/modify flows pass.
- [ ] **P11-03** End-to-end tests of UI flows (Playwright). **Acceptance:** wizards, mappings, exemptions, manual grants.
- [ ] **P11-04** Live test against a real Plex test server and test Discord guild: verify N3, N4, N5, N6 with real data. **Acceptance:** documented test log.
- [ ] **P11-05** Accessibility and theme review (light/dark/each colorblind mode). **Acceptance:** checklist.
- [ ] **P11-06** Unraid install/upgrade/restart/persistence test. **Acceptance:** settings survive container update.

### Phase 12 — Documentation & Release

- [ ] **P12-01** README: what WooSarr does, install on Unraid, first-run walkthrough, FAQ.
- [ ] **P12-02** Docs: sync rules explained for admins (additive, exemptions, manual grants, external shares).
- [ ] **P12-03** Backup/restore & secret key handling guidance (losing `master.key` = re-enter secrets).
- [ ] **P12-04** v1.0 release: changelog, tagged image, Unraid template submission (Community Apps).

---

## 7. Acceptance Criteria Map (spec → tasks)

| Spec requirement                                                                                      | Tasks                |
| ----------------------------------------------------------------------------------------------------- | -------------------- |
| Docker container, loadable in Unraid                                                                  | P2-01–P2-04          |
| Plex integration, OAuth, no hardcoded creds/tokens                                                    | P3-01, P1-05, P10-01 |
| Discord bot integration                                                                               | P4-\*                |
| Web config UI on port 2000, sidebar nav                                                               | P1-07, P6-02         |
| Users page (linked Discord, roles, libraries, manual add/remove, link method flag, admin unlink)      | P7-01                |
| Roles page (assign libraries to roles)                                                                | P7-02                |
| Libraries page (exemptions)                                                                           | P7-03                |
| Auto assign/remove on role add/remove/modify; exemptions; additive; no access loss; linked users only | P5-\* , §5           |
| Logs page, detailed logging                                                                           | P8-\*                |
| Secure sensitive data                                                                                 | P1-05, P1-06, P10-\* |
| Light/dark, colorblind, purple                                                                        | P6-03                |
| Setup assistants (Discord, Plex)                                                                      | P9-\*                |
| Git repo on GitHub                                                                                    | P1-01                |
| GitHub workflow for Docker build/publish                                                              | P2-04                |

---

## 8. Risks & Open Questions

- **R1** Plex share API semantics (replace vs merge, last-library removal, filter/permission side effects, managed/home users) are not fully documented in python-plexapi's reference → resolve in P0-03 before any write code.
- **R7** python-plexapi is synchronous and community-maintained; its docs mark many `MyPlexUser` fields "Unknown." Isolate behind `PlexGateway` (D1b), pin the version, and keep contract tests with recorded fixtures.
- **R2** Plex has no per-library "revoke only this" call; our read-modify-write may race with changes made directly in Plex → use per-user lock and re-read immediately before write.
- **R3** Discord Members intent is privileged; bots in 100+ servers need verification (not an issue for single-guild use, but document).
- **R4** Linking trust (D4): without proof of ownership, anyone could claim to be a Plex user and gain their libraries. Mitigation: OAuth option provides proof; username-only option is trust-based as decided.
- **R5** Master key stored beside the DB offers limited protection if `/config` leaks; document option to supply the key externally (env/secret).
- **R6** Plex/Discord API changes → isolate behind service interfaces; contract tests with recorded fixtures.
- **Q1** What should happen to role-derived access when a user leaves the Discord server? (default: remove role-derived, keep manual/exempt)
- **Q2** Should libraries not mapped to any role be left entirely alone? (default: yes, "unmanaged")
- **Q3** Should the app notify users on Discord when access changes? (default: no, v1.1 candidate)

---

## 9. Conventions for AI Agents

- Prefer small, reviewable commits; message format: `P5-01: implement desired-state calculator`.
- Write tests alongside code; do not mark a task done without passing tests.
- Never print, log, commit, or echo secrets, even in test output. Use canary values for tests.
- When behavior is ambiguous, write the assumption into §2 or §8 and ask the human rather than guessing silently.
- Keep sync logic pure and separate from I/O so it can be tested without Plex/Discord.
- Update this file's checkboxes and Decisions table as work proceeds.

---

## 10. Definition of Done (v1.0)

- [ ] Fresh Unraid install → onboarding wizards → working sync with only UI interaction.
- [ ] All N1–N8 verified by tests or documented manual checks.
- [ ] No secrets in repo, image, logs, or API responses.
- [ ] Settings and secrets survive container update/restart.
- [ ] README and Unraid template published.
- [ ] Git repo on GitHub with clean history.
- [ ] GitHub Actions workflow builds and publishes Docker images.

---

## 11. Suggested Milestones

| Milestone           | Phases  | Outcome                                                    |
| ------------------- | ------- | ---------------------------------------------------------- |
| M1 Walking skeleton | 0–2     | Container runs on Unraid, UI loads on :2000                |
| M2 Integrations     | 3–4     | Plex + Discord connected, data visible                     |
| M3 Core value       | 5, 7    | Roles → libraries working with exemptions & manual control |
| M4 Polish           | 6, 8, 9 | Themes, logs, setup wizards                                |
| M5 Release          | 10–12   | Hardened, tested, documented, published                    |

---

## 12. References

- Plex Media Server API: https://developer.plex.tv/pms/
- Plex API SDKs: https://plexapi.dev/SDKs
- **python-plexapi (chosen):** https://python-plexapi.readthedocs.io/en/latest/ — key module: https://python-plexapi.readthedocs.io/en/latest/modules/myplex.html (`MyPlexAccount.updateFriend`, `MyPlexUser`, `MyPlexServerShare`, `MyPlexPinLogin`, `MyPlexJWTLogin`)
- Python SDK docs: https://github.com/LukasParke/plexapi-dev-docs/tree/main/sdks/python
- TypeScript SDK docs: https://github.com/LukasParke/plexapi-dev-docs/tree/main/sdks/typescript
- Go SDK docs: https://github.com/LukasParke/plexapi-dev-docs/tree/main/sdks/go
- Discord developer docs: https://docs.discord.com/developers/intro
- discord.py docs: https://discordpy.readthedocs.io/en/stable/
- Unraid Docker templates: https://github.com/unraid/docker-templates
- Unraid Community Apps: https://github.com/unraid/community-apps
