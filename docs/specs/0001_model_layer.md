# django-tipping model layer spec v1

## 1. Purpose

Define the database model layer for django-tipping: a sports tipping web app where users predict winners of scheduled games and accumulate points across a season. The model layer must support:

- Importing fixtures/results from an external feed (TheSportsDB free tier day-one) without manual entry
- Users submitting one tip per game
- Per-group and global season leaderboards
- Historical leaderboard access for past seasons

## 2. Scope

**In scope:** all Django models needed to support fixtures, tips, scoring, groups, leaderboards; field-level constraints and validation; relationship cardinality and `on_delete` behaviour; indexes required for the leaderboard queries described below.

**Out of scope (later phases):** feed sync implementation (this spec defines the surface the sync writes to, not the sync itself); view / template / API layer; authentication backend choices beyond Django defaults; notifications / email; admin customisations beyond what's needed for owner-managed membership.

## 3. Assumptions

- **Single data source day-one**: TheSportsDB free tier (30 req/min, key `123`, v1 endpoints). Schema accommodates one external `source_id` per entity; multi-source reconciliation is out of scope.
- **NRL only day-one**: Sport / League entities exist for multi-sport future, but only NRL is seeded.
- **Family-scale usage day-one**: low concurrency, ~dozens of users, ~200 games/season. No partitioning, no caching layer.
- **Postgres** in production (so `CheckConstraint`, partial unique indexes are available). Dev may use SQLite; constraints are written for Postgres.
- All `DateTimeField`s timezone-aware, UTC stored; display conversion in views.

## 4. Conventions

- snake_case fields, PascalCase models, Django `BigAutoField` PKs.
- `created_at` / `updated_at` only where listed.
- `source_id` columns: nullable `PositiveIntegerField`, indexed. Used as upsert key by future sync job. Nullable so seed/test data can be inserted without external ID.
- Every FK declares explicit `on_delete`.
- DB-level enforcement wherever possible (uniqueness, CHECK, NOT NULL). App-level validation via `clean()` only when the rule can't be expressed in SQL.

## 5. Entities

### 5.1 Sport

| Field | Type | Notes |
|---|---|---|
| `name` | CharField(50), unique | |

No `source_id` — sport names are seeded manually. Seeded value: `Sport(name="Rugby League")`.

### 5.2 League

| Field | Type | Notes |
|---|---|---|
| `sport` | FK Sport, `on_delete=PROTECT` | deleting a Sport with leagues should fail |
| `name` | CharField(100) | |
| `source_id` | PositiveIntegerField, null, indexed | TheSportsDB `idLeague` |
| `created_at` | DateTimeField(auto_now_add=True) | |

Constraints: `UniqueConstraint(sport, name)`; `UniqueConstraint(source_id)` partial `WHERE source_id IS NOT NULL`.

Seeded: `League(sport=<Rugby League>, name="NRL", source_id=4416)`.

### 5.3 Season

| Field | Type | Notes |
|---|---|---|
| `league` | FK League, `on_delete=PROTECT` | |
| `year` | PositiveSmallIntegerField | matches TheSportsDB `strSeason` for single-year leagues like NRL |
| `start_date` | DateField | used by group-leaderboard membership-overlap query |
| `end_date` | DateField | inclusive of finals |

Constraints: `UniqueConstraint(league, year)`; `CheckConstraint(end_date >= start_date)`.

### 5.4 Team

| Field | Type | Notes |
|---|---|---|
| `league` | FK League, `on_delete=PROTECT` | |
| `name` | CharField(100) | from feed, e.g. "Canterbury Bankstown Bulldogs" |
| `short_name` | CharField(10), nullable | feed sometimes provides `strTeamShort` |
| `source_id` | PositiveIntegerField, null, indexed | TheSportsDB `idTeam` |

Constraints: `UniqueConstraint(league, source_id)` partial; `UniqueConstraint(league, name)`.

### 5.5 Round

| Field | Type | Notes |
|---|---|---|
| `season` | FK Season, `on_delete=CASCADE` | a round has no meaning outside its season |
| `number` | IntegerField | raw `intRound` from feed (1..27ish regular, 500-range trials, etc.) |

Constraints: `UniqueConstraint(season, number)`.

App-level: a helper derives round type (preseason/regular/finals) from `number`.

### 5.6 Game

| Field | Type | Notes |
|---|---|---|
| `round` | FK Round, `on_delete=CASCADE` | |
| `home_team` | FK Team, `on_delete=PROTECT`, related_name="home_games" | |
| `away_team` | FK Team, `on_delete=PROTECT`, related_name="away_games" | |
| `kickoff` | DateTimeField | UTC |
| `home_score` | PositiveSmallIntegerField, nullable | null until match has a result |
| `away_score` | PositiveSmallIntegerField, nullable | null until match has a result |
| `status` | CharField(30) | passes through feed `strStatus` |
| `postponed` | BooleanField, default=False | mirrors feed `strPostponed == "yes"` |
| `venue_name` | CharField(120), nullable | string-only at eventsseason endpoint; no Venue entity v1 |
| `source_id` | PositiveIntegerField, null, indexed | TheSportsDB `idEvent` |
| `updated_at` | DateTimeField(auto_now=True) | last touched (by sync or manually) |

Constraints:

- `UniqueConstraint(round, source_id)` partial
- `CheckConstraint(home_team_id != away_team_id)`
- `CheckConstraint((home_score IS NULL AND away_score IS NULL) OR (home_score IS NOT NULL AND away_score IS NOT NULL))` — scores written as a pair

Indexes: `(round, kickoff)` for round-lock derivation; `(status)` for sync/scoring filters.

Derived (not stored): `result` = HOME_WIN if home_score > away_score, AWAY_WIN if reversed, DRAW if equal, None otherwise.

### 5.7 User (custom)

Defined in `users.models.User(AbstractUser)`. `AUTH_USER_MODEL = "users.User"`.

Inherited & used: `username`, `password`, `is_active`, `is_staff`, `is_superuser`, `date_joined`.

Overrides / additions:

| Field | Type | Notes |
|---|---|---|
| `email` | EmailField, unique, required | override default (Django's default is optional + non-unique) |
| `display_name` | CharField(50) | shown on leaderboards |

Custom `UserManager` to enforce required email at `create_user` / `create_superuser`.

`USERNAME_FIELD` stays `username` for v1. Email-as-login is an auth-backend concern, out of scope here.

### 5.8 Group

| Field | Type | Notes |
|---|---|---|
| `name` | CharField(80) | |
| `owner` | FK User, `on_delete=PROTECT`, related_name="owned_groups" | owner can't be deleted while owning a group; ownership transfer required |
| `created_at` | DateTimeField(auto_now_add=True) | |

Constraints: `UniqueConstraint(owner, name)`.

### 5.9 Membership

| Field | Type | Notes |
|---|---|---|
| `group` | FK Group, `on_delete=CASCADE` | |
| `user` | FK User, `on_delete=CASCADE` | |
| `joined_at` | DateTimeField(auto_now_add=True) | |
| `left_at` | DateTimeField, nullable | null = currently active; supports rejoin via new row |

Constraints:

- `UniqueConstraint(group, user)` partial `WHERE left_at IS NULL` — at most one active membership per (group, user) but rejoin allowed
- `CheckConstraint(left_at IS NULL OR left_at > joined_at)`

Index: `(group, user, left_at)` for historical-leaderboard query.

### 5.10 Tip

| Field | Type | Notes |
|---|---|---|
| `user` | FK User, `on_delete=CASCADE` | |
| `game` | FK Game, `on_delete=CASCADE` | |
| `choice` | CharField(4), TextChoices: `HOME` / `AWAY` / `DRAW` | |
| `submitted_at` | DateTimeField(auto_now_add=True) | |
| `updated_at` | DateTimeField(auto_now=True) | |

Constraints: `UniqueConstraint(user, game)`.

App-level validation (`clean()`):

- Reject create/update if current time >= round lock time (`min(game.kickoff)` across the round's games). DB-level enforcement too complex for v1.

## 6. Cross-cutting rules

- **Round lock time**: `min(kickoff)` across the round's games. Not stored. If query cost matters later, materialise as a column populated by sync.
- **Missed tip**: absence of a Tip row = 0 for that game. No sentinel rows.
- **Scoring** (per Tip where `Game.status == "Match Finished"`):
  - +1 if `choice` matches result AND result != DRAW
  - +2 if `choice == DRAW` AND result == DRAW
  - else 0
- **Global leaderboard, season S**: Users with any Tip on a Game in Season S. Ordered by sum(points) desc.
- **Group leaderboard, season S, group G**: Users where a Membership(group=G, user=U) exists with `joined_at <= S.end_date` AND `(left_at IS NULL OR left_at >= S.start_date)`, AND U has any Tip on a Game in S. Same ordering.

## 7. Feed sync surface

The sync job (separate spec) writes to:

- **League**: manually seeded; sync only reads.
- **Season**: created when new season appears; `start_date`/`end_date` derived from min/max kickoff in that season's events.
- **Team**: upsert by `(league, source_id)`.
- **Round**: get-or-create by `(season, number)` from each event's `intRound`.
- **Game**: upsert by `(round, source_id)`; sync writes `kickoff`, `home_score`, `away_score`, `status`, `postponed`, `venue_name`, `updated_at`.

Sync does NOT write: Sport, User, Group, Membership, Tip.

## 8. Seeding plan

Single Django data migration creates:

- `Sport(name="Rugby League")`
- `League(sport=<above>, name="NRL", source_id=4416)`

No teams, seasons, rounds, games seeded — sync populates on first run.

## 9. Out of scope for v1

Leaderboard tiebreakers; auto-tipping; group join codes / invite links / approval flow; email verification; profile fields beyond `display_name`; bye representation (implicit via no Game); margin / exact-score prediction; multi-sport data day-one; multi-source ID reconciliation; materialised leaderboards; soft delete.

## 10. Open questions

- Whether `Season.start_date` / `end_date` must be provided at creation (this spec assumes yes) or are backfilled by sync.
