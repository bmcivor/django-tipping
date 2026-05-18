# django-tipping — Model Layer Specification

**Status:** Draft v1 — subject to revision based on usability testing before go-live.
**Scope:** Django ORM model layer only. Views, serializers, admin customisation, templates, CI/CD, and tests are out of scope of this document (called out in §10).
**Last updated:** 2026-05-19

---

## 1. Overview & scope

django-tipping is a Django app for sports tipping. Initial deployment target is family use; longer-term target is multi-group / worldwide self-hosted deployment.

This document specifies the **model layer** for v1:

- Custom user model with email login and social auth.
- Sport / League / Season / Round / Team / Game hierarchy ("what is being tipped on"), admin-managed.
- Winner-pick tipping with universal hardcoded scoring (1 pt winner, 2 pt correct draw, 0 pt wrong).
- Round-based tip lock (first match of round locks the entire round).
- Single global pool (Pool/Group entity deferred to a future epic).
- Audit history on every entity.
- Soft-delete on user-facing entities (User, Tip).

The model layer is the foundation for the test suite, the API, and the admin UI. It should be in place — and tested — before the first PR that exposes anything to users.

---

## 2. Architectural decisions

### 2.1 App split

Three Django apps:

- **`users`** — custom `User`, groups/roles, social auth integration (`django-allauth`).
- **`competitions`** — `Sport`, `League`, `Team`, `Season`, `Round`, `Game`. The "what is being tipped on" half.
- **`tipping`** — `Tip`, scoring module, signal handlers. The "act of tipping" half.

Pool/Group will get its own app (`pools` or similar) when that epic lands. Deliberately not split out now.

### 2.2 Database & infrastructure

- **PostgreSQL** (replacing the SQLite default in current scaffolding).
- Hosting and Dockerised deployment patterned after vertex-* apps (Jenkins pipeline). Out of scope for this document, but DB choice anticipates it.

### 2.3 Auth strategy

- **`django-allauth`** for both:
  - Email + password (primary for initial users).
  - Social providers: Google, Microsoft, Apple (for later users).
- **Email verification required** on signup.
- Email is the login identifier (`USERNAME_FIELD = "email"`).
- `username` field dropped from the custom user model (no use case).

### 2.4 Audit

- **`django-simple-history`** applied to every concrete model in the spec.
- **User login events** also logged (custom log model wired to `django-allauth` login/logout signals).
- **Flat M2M (Team↔League) is NOT audited** — known limitation of `django-simple-history` with native M2M; accepted as a trade-off given how rarely the relationship changes.

### 2.5 Soft-delete

- Soft-delete applies to **user-facing entities only**: `User`, `Tip`.
- Admin-managed entities (Sport, League, Season, Round, Team, Game) are **hard-deleted** when removed. Hard-delete of `Game` cascades to dependent `Tip` rows (see §6.1).
- Soft-delete uses **two fields with distinct semantics**:
  - `is_active: bool` — "disabled but recoverable" (e.g. admin temporarily deactivates a user). For the `User` model this reuses Django's built-in `is_active`.
  - `deleted_at: datetime | null` — "soft-deleted; intent to remove". `is_active` will also be `False` when `deleted_at` is set.

The two fields are not synonyms. A row can be `is_active=False` with `deleted_at IS NULL` (paused), or both set (deleted).

### 2.6 Timezone

- All datetimes stored as **UTC** in the database.
- UI rendering responsibility (out of scope here) is to convert to local timezone for display.
- No per-user `timezone` field in v1.

---

## 3. Abstract base models

These live in a shared module (suggested: `users/abstract.py` or `tipping/abstract.py` — TBD during implementation; not a model-layer decision). Applied via multiple inheritance.

### 3.1 `AuditedModel` (abstract)

Fields:

| Field         | Type                              | Null | Default      | Notes                                       |
|---------------|-----------------------------------|------|--------------|---------------------------------------------|
| `created_at`  | `DateTimeField`                   | no   | `auto_now_add` | Set on first save.                         |
| `updated_at`  | `DateTimeField`                   | no   | `auto_now`     | Updated on every save.                     |
| `created_by`  | `ForeignKey(User, SET_NULL)`      | yes  | null         | The user who created the row. Nullable to survive user deletion. |
| `updated_by`  | `ForeignKey(User, SET_NULL)`      | yes  | null         | The user who last updated the row.         |

Setting `created_by` / `updated_by` is the responsibility of the saving code (view/admin/management command) — not enforced at the model layer. The model layer only provides the fields.

`Meta.abstract = True`.

### 3.2 `SoftDeletableModel` (abstract)

Fields:

| Field         | Type                | Null | Default | Notes                                                          |
|---------------|---------------------|------|---------|----------------------------------------------------------------|
| `is_active`   | `BooleanField`      | no   | `True`  | For models other than `User`. The `User` model uses Django's built-in `is_active` (do not re-declare). |
| `deleted_at`  | `DateTimeField`     | yes  | null    | Set when the row is soft-deleted. `is_active` should be `False` when set. |

Provides a `delete()` override that sets `is_active=False` and `deleted_at=now()` instead of removing the row. A `hard_delete()` method preserves access to true deletion. Default manager filters out rows where `deleted_at IS NOT NULL`; a secondary `all_objects` manager exposes everything.

`Meta.abstract = True`.

### 3.3 `HistoricalRecords` mixin

Every concrete model in this spec declares a `history = HistoricalRecords()` field (from `django-simple-history`). This generates a `historical_<modelname>` table tracking every field change with timestamp and (optionally) the editing user.

---

## 4. App: `users`

### 4.1 `User`

Custom user model — subclass of `AbstractBaseUser` (via `django-allauth`-compatible `AbstractUser`-style pattern). Set as `AUTH_USER_MODEL` in settings.

Fields:

| Field             | Type                | Null | Unique | Default      | Notes                                              |
|-------------------|---------------------|------|--------|--------------|----------------------------------------------------|
| `email`           | `EmailField`        | no   | yes    | —            | Login identifier. `USERNAME_FIELD = "email"`.      |
| `display_name`    | `CharField(150)`    | no   | yes    | —            | Shown on leaderboards, tipping UI. Unique globally.|
| `first_name`      | `CharField(150)`    | yes  | no     | empty string | Django default; kept.                              |
| `last_name`       | `CharField(150)`    | yes  | no     | empty string | Django default; kept.                              |
| `is_active`       | `BooleanField`      | no   | no     | `True`       | Django built-in; reused for soft-delete `is_active`.|
| `is_staff`        | `BooleanField`      | no   | no     | `False`      | Django built-in; required for admin access.        |
| `is_superuser`    | `BooleanField`      | no   | no     | `False`      | Django built-in.                                   |
| `deleted_at`      | `DateTimeField`     | yes  | no     | null         | Soft-delete timestamp.                             |
| `date_joined`     | `DateTimeField`     | no   | no     | `auto_now_add` | Django default.                                  |
| `last_login`      | `DateTimeField`     | yes  | no     | null         | Django default.                                    |

`username` field is **explicitly removed** (override `username = None` in the model).

Inherits: `AbstractBaseUser`, `PermissionsMixin`, `SoftDeletableModel` semantics (uses built-in `is_active` + new `deleted_at`), `HistoricalRecords`.

`REQUIRED_FIELDS = ["display_name"]` (so `createsuperuser` prompts for it).

Notes:

- A user soft-delete (`deleted_at` set) **does not** soft-delete their tips. Tips remain visible on leaderboards attributed to the soft-deleted user (resolved §6.1).
- Email verification is enforced by `django-allauth` configuration, not at the model layer.
- Password handling is delegated to `AbstractBaseUser`.

### 4.2 Groups & roles

Two Django `Group` rows seeded by migration:

- **`Admin`** — full CRUD on `Sport`, `League`, `Season`, `Round`, `Team`, `Game` (including result entry). Members can also tip (see Tipper group).
- **`Tipper`** — required to submit tips. Membership is auto-granted on email verification (see §7.3 — flagged as open product question in §8).

`is_staff` and `is_superuser` remain available; `Admin` group membership is the canonical signal for "manages competitions". A given user can be in both `Admin` and `Tipper`.

### 4.3 `UserLoginEvent`

A lightweight log model for auth audit (since `django-simple-history` doesn't capture login/logout).

| Field        | Type                              | Null | Default        | Notes                                              |
|--------------|-----------------------------------|------|----------------|----------------------------------------------------|
| `user`       | `ForeignKey(User, SET_NULL)`      | yes  | —              | The user (nullable to survive hard-deletion).      |
| `event_type` | `CharField(choices=...)`          | no   | —              | Choices: `LOGIN`, `LOGOUT`, `LOGIN_FAILED`.        |
| `timestamp`  | `DateTimeField`                   | no   | `auto_now_add` | Event time.                                        |
| `ip_address` | `GenericIPAddressField`           | yes  | null           | Captured from request.                             |
| `user_agent` | `CharField(512)`                  | yes  | null           | Captured from request headers.                     |

Populated by signal handlers attached to `django-allauth`'s `user_logged_in`, `user_logged_out`, and `user_login_failed` signals.

Not soft-deletable. No history tracking on this model (it is itself the audit trail).

---

## 5. App: `competitions`

### 5.1 `Sport`

| Field         | Type                | Null | Unique | Notes                                |
|---------------|---------------------|------|--------|--------------------------------------|
| `name`        | `CharField(100)`    | no   | yes    | E.g. "Rugby League".                 |
| `slug`        | `SlugField(100)`    | no   | yes    | URL-safe identifier.                 |
| `description` | `TextField`         | yes  | no     | Optional admin notes.                |

Inherits: `AuditedModel`, `HistoricalRecords`. **Not** soft-deletable.

### 5.2 `League`

| Field      | Type                              | Null | Unique               | Notes                                       |
|------------|-----------------------------------|------|----------------------|---------------------------------------------|
| `name`     | `CharField(150)`                  | no   | yes (with `sport`)   | E.g. "NRL".                                 |
| `slug`     | `SlugField(150)`                  | no   | yes (with `sport`)   |                                             |
| `sport`    | `ForeignKey(Sport, PROTECT)`      | no   | —                    | A league belongs to one sport.              |
| `country`  | `CharField(100)`                  | yes  | no                   | E.g. "Australia".                           |

Inherits: `AuditedModel`, `HistoricalRecords`. **Not** soft-deletable.

`Meta.unique_together = [("sport", "name"), ("sport", "slug")]`.

### 5.3 `Team`

| Field     | Type                | Null | Unique             | Notes                          |
|-----------|---------------------|------|--------------------|--------------------------------|
| `name`    | `CharField(150)`    | no   | yes (with `slug`)  | E.g. "Penrith Panthers".       |
| `slug`    | `SlugField(150)`    | no   | yes (with `name`)  |                                |
| `leagues` | `ManyToManyField(League)` | —  | —                  | Flat M2M. Not audited by simple-history (accepted trade-off, §2.4). |

Inherits: `AuditedModel`, `HistoricalRecords`. **Not** soft-deletable.

### 5.4 `Season`

| Field         | Type                              | Null | Unique             | Notes                                  |
|---------------|-----------------------------------|------|--------------------|----------------------------------------|
| `league`      | `ForeignKey(League, PROTECT)`     | no   | —                  |                                        |
| `year`        | `PositiveSmallIntegerField`       | no   | yes (with `league`)| E.g. 2026.                             |
| `name`        | `CharField(150)`                  | no   | no                 | E.g. "NRL 2026".                       |
| `start_date`  | `DateField`                       | yes  | no                 | Optional.                              |
| `end_date`    | `DateField`                       | yes  | no                 | Optional.                              |

Inherits: `AuditedModel`, `HistoricalRecords`. **Not** soft-deletable.

`Meta.unique_together = [("league", "year")]`.

### 5.5 `Round`

| Field        | Type                              | Null | Unique               | Notes                                                       |
|--------------|-----------------------------------|------|----------------------|-------------------------------------------------------------|
| `season`     | `ForeignKey(Season, PROTECT)`     | no   | —                    |                                                             |
| `number`     | `PositiveSmallIntegerField`       | no   | yes (with `season`)  | E.g. 1, 2, 3 ... 27.                                        |
| `name`       | `CharField(150)`                  | yes  | no                   | Optional — e.g. "Magic Round", "Finals Week 1".             |
| `locks_at`   | `DateTimeField`                   | yes  | no                   | UTC. Stored, auto-populated from `min(games.match_date)` via signal (§7.3). Admin can override. Nullable until at least one game is attached to the round. |

Inherits: `AuditedModel`, `HistoricalRecords`. **Not** soft-deletable.

`Meta.unique_together = [("season", "number")]`.
`Meta.ordering = ["season", "number"]`.

### 5.6 `Game`

| Field         | Type                              | Null | Notes                                              |
|---------------|-----------------------------------|------|----------------------------------------------------|
| `round`       | `ForeignKey(Round, PROTECT)`      | no   |                                                    |
| `home_team`   | `ForeignKey(Team, PROTECT, related_name="home_games")` | no |                                |
| `away_team`   | `ForeignKey(Team, PROTECT, related_name="away_games")` | no |                                |
| `match_date`  | `DateTimeField`                   | no   | UTC.                                               |
| `venue`       | `CharField(200)`                  | yes  | Optional.                                          |
| `home_score`  | `PositiveSmallIntegerField`       | yes  | NULL until result entered.                         |
| `away_score`  | `PositiveSmallIntegerField`       | yes  | NULL until result entered.                         |

Inherits: `AuditedModel`, `HistoricalRecords`. **Not** soft-deletable.

Constraints:

- `CheckConstraint(check=Q(home_team__ne=F("away_team")), name="game_home_away_distinct")` — DB-level rejection of self-play. (Django syntax: `~Q(home_team=F("away_team"))`.)
- `CheckConstraint` linking the score fields: either both populated or both null. Prevents half-entered results.

`Meta.ordering = ["match_date"]`.

Derived "winner" (used by scoring) is computed: `home_team` if `home_score > away_score`, `away_team` if `away_score > home_score`, draw if equal. No stored `winner` field — single source of truth is the scores.

Game hard-deletion **cascades to `Tip`** (see §6.1).

---

## 6. App: `tipping`

### 6.1 `Tip`

| Field             | Type                                              | Null | Default | Notes                                                |
|-------------------|---------------------------------------------------|------|---------|------------------------------------------------------|
| `user`            | `ForeignKey(User, CASCADE)`                       | no   | —       | Tip belongs to a user.                               |
| `game`            | `ForeignKey(Game, CASCADE)`                       | no   | —       | Hard-delete of game removes tip (UI confirmation-gates this — §7.4). |
| `round`           | `ForeignKey(Round, CASCADE)`                      | no   | —       | **Denormalised** from `game.round` for query simplicity. Maintained via `save()` override / signal. |
| `pick`            | `CharField(8, choices=[HOME, AWAY, DRAW])`        | yes  | null    | NULL = no pick yet (pre-created row or reset).       |
| `points_awarded`  | `PositiveSmallIntegerField`                       | no   | `0`     | Re-computed by signal on game result change.         |
| `is_active`       | `BooleanField`                                    | no   | `True`  | Soft-delete flag.                                    |
| `deleted_at`      | `DateTimeField`                                   | yes  | null    | Soft-delete timestamp.                               |

Inherits: `AuditedModel`, `SoftDeletableModel`, `HistoricalRecords`.

Constraints:

- `UniqueConstraint(fields=["user", "game"], condition=Q(is_active=True), name="tip_unique_active_user_game")` — one active tip per user per game. Soft-deleted rows allowed in addition.
- `CheckConstraint` ensuring `points_awarded == 0` when `pick IS NULL` (a tip with no pick can't have scored).

Notes:

- `pick` is **nullable** because pre-created rows (§7.2) exist before the user picks. Reset is `pick → NULL` (not a soft-delete).
- Soft-delete fields on `Tip` are **unused in v1**. They exist for symmetry with `SoftDeletableModel` and for future cases (e.g. admin removing a tip after a dispute). Documenting them here means the constraint and migrations are right from day 1.
- `Tip.user` uses `CASCADE` to handle hard user deletion if it ever happens; soft-delete of a user does **not** affect tips (resolved §2.5 / §4.1).
- `Tip.game` uses `CASCADE`; UI confirmation-gates game deletion (§7.4).
- `Tip.round` is denormalised — kept in sync via `save()` override; if `game.round` ever changes (rare), a signal must update `round` on dependent tips. This is an implementation note for code, not a schema concern.

### 6.2 Scoring module — `tipping/scoring.py`

Pure-Python module, no models.

```python
POINTS_CORRECT_WINNER = 1
POINTS_CORRECT_DRAW = 2
POINTS_INCORRECT = 0

def calculate_points(tip, game) -> int:
    """Return points awarded for `tip` given the final state of `game`.

    Args:
        tip: A Tip instance with .pick in {HOME, AWAY, DRAW, None}.
        game: A Game instance with .home_score and .away_score populated.

    Returns:
        Integer points. 0 if game has no result yet, tip has no pick, or pick is wrong.
    """
```

Universal across sports for v1. Per-sport variation deferred (§9).

### 6.3 Signals — see §7.3

---

## 7. Cross-cutting concerns

### 7.1 Constraints & validators (summary)

- `Game`: home_team ≠ away_team (DB constraint). Both scores populated or both null (DB constraint).
- `Tip`: one active tip per (user, game) (DB conditional unique). `points_awarded == 0` when `pick IS NULL` (DB constraint).
- `User.email` unique. `User.display_name` unique.
- `Sport.name` / `Sport.slug` unique.
- `League` unique on `(sport, name)` and `(sport, slug)`.
- `Season` unique on `(league, year)`.
- `Round` unique on `(season, number)`.

### 7.2 Tip lifecycle

```
+-----------------------------------------------------------------+
| Trigger                | Effect on Tip                          |
+-----------------------------------------------------------------+
| Game added to a round  | Pre-create one Tip row per active      |
|                        | Tipper, pick=NULL, points_awarded=0.   |
+-----------------------------------------------------------------+
| User added to Tipper   | Pre-create one Tip row per Game in     |
| group                  | every open (not-yet-locked) round.     |
+-----------------------------------------------------------------+
| User submits/edits     | Update pick on existing row. Allowed   |
| pick                   | only while now() < round.locks_at.     |
|                        | Change captured by simple-history.     |
+-----------------------------------------------------------------+
| User "resets" round    | Set pick=NULL on every Tip for that    |
|                        | round (only while round is open).      |
|                        | History captures the change.           |
+-----------------------------------------------------------------+
| Round locks            | now() >= round.locks_at — model layer  |
| (time-based)           | does not enforce this; application     |
|                        | code rejects edits past lock.          |
+-----------------------------------------------------------------+
| Game result entered    | Signal recomputes points_awarded for   |
|                        | every Tip on that game.                |
+-----------------------------------------------------------------+
| Game result corrected  | Same signal re-fires; points may shift |
|                        | retroactively. History captures the    |
|                        | change.                                |
+-----------------------------------------------------------------+
| Game hard-deleted      | CASCADE removes Tips. UI confirmation- |
|                        | gates this (not enforced at model      |
|                        | layer).                                |
+-----------------------------------------------------------------+
| User soft-deleted      | Tips unaffected. Remain on leaderboard |
|                        | attributed to (now-soft-deleted) user. |
+-----------------------------------------------------------------+
```

### 7.3 Signal map

| Signal source / event                          | Handler responsibility                                                                 |
|------------------------------------------------|----------------------------------------------------------------------------------------|
| `Game.post_save` (new game on a round)         | Recompute `round.locks_at` to `min(games.match_date)`; pre-create Tip rows for all current Tippers on this game. |
| `Game.post_save` (score fields changed)        | For every Tip on this game, recompute `points_awarded` via `tipping.scoring.calculate_points`. Save (which writes history). |
| `Group.user_set` m2m_changed (`Tipper` group)  | When user added: pre-create Tip rows for that user across every open Round's Games. When user removed: no automatic cleanup — existing tips stand. |
| `django-allauth` `user_logged_in`              | Insert `UserLoginEvent(event_type=LOGIN, ...)`.                                        |
| `django-allauth` `user_logged_out`             | Insert `UserLoginEvent(event_type=LOGOUT, ...)`.                                       |
| `django-allauth` `user_login_failed`           | Insert `UserLoginEvent(event_type=LOGIN_FAILED, user=None, ...)`.                      |
| `django-allauth` `email_confirmed`             | **(Open question — see §8)** Add user to `Tipper` group.                               |

Signal handlers live in each app's `signals.py`, wired in `apps.py`'s `ready()`.

### 7.4 UI-layer responsibilities (noted, not enforced here)

These are mentioned because the model layer leaves them open by design:

- Confirmation-gate `Game` hard-delete (cascades to tips).
- Confirmation-gate `User` soft-delete.
- Reject tip submission past `round.locks_at`.
- Render UTC datetimes in user's local timezone.

---

## 8. Open product questions (resolve before implementation)

These were flagged during scoping and have **not** been resolved. They affect behaviour, not schema, so the model layer can land first; the answers determine the signal handlers and the views.

1. **Tipper group auto-join on email verification.** Proposed: yes, auto-join on `email_confirmed` signal. Alternative: admin must manually add new users to the Tipper group. Auto-join is better UX; manual is stricter access control. Default to auto-join unless decided otherwise.
2. **Multi-league tipping scope.** When multiple `League` rows are active simultaneously (multi-sport design), does a Tipper get pre-created Tip rows for **every** active league's open rounds? Or do tippers opt in per-league? Model supports either — the difference is whether pre-create is scoped to a league subset per user (requires a `User`↔`League` join table) or unconditional.
3. **Round lifecycle states.** v1 treats a round as "open until `locks_at`". No explicit `STATUS = {DRAFT, OPEN, LOCKED, COMPLETED}` field. May want one once usability testing reveals workflows (e.g. admin wants to publish a round explicitly).
4. **Confirmation/reversal flows for result correction.** Re-firing the scoring signal on every score change is technically correct; whether the user-facing leaderboard should display "points adjusted on date X" is a UI question.

---

## 9. Deferred to future epics (not in v1 model layer)

Documenting these so they aren't forgotten and so the v1 design doesn't accidentally box them out.

- **Pool / Group entity.** Multi-group worldwide deployment. Probably a `Group` (tenant) entity + `Pool` (competition inside a group) entity. Per-group scoring config lives here.
- **Per-group scoring rules.** Currently hardcoded constants in `tipping/scoring.py`; will become per-group config.
- **API integration** for fixture and result ingest (avoid manual admin entry). When this lands, `Round.locks_at` auto-populates from feed data, results auto-populate, scoring signal handles the rest.
- **Email notifications** triggered by the post-result signal (round summary emails, leaderboard updates).
- **Conditional/bonus scoring** (e.g. NRL Dally M winner picked during grand final round).
- **Per-sport scoring variation.**
- **Tip "joker" / double-points mechanic** (explicitly out of v1 per scoping).
- **Postponed / cancelled game handling.** v1 has no explicit status field; relies on scores remaining NULL. Future work may need an explicit `status` enum on `Game`.
- **Historical-season import.** v1 is forward-only (current/future seasons).

---

## 10. Out of scope (not the model layer)

This document covers schema, constraints, signals, abstract models, and scoring constants. The following are explicitly **not** specified here and are owned by other documents / future tickets:

- Views, URLs, serializers, REST/HTML API surface.
- Django admin customisation (`admin.py` configuration).
- Templates / frontend.
- Test layer (unit, integration, contract) — separate phase.
- CI/CD pipeline (Jenkins, Docker images, frontend/backend split).
- Deployment, hosting, secrets management.
- Logging, metrics, observability.
- Performance tuning, indexes beyond uniqueness constraints (revisit after load patterns emerge).

---

## Appendix A: Decisions log (for traceability)

Decisions captured during scoping rounds 1–4 (May 2026). Each line: decision → source round.

- Multi-sport, admin-controlled — R1
- Single global pool v1; Pool/Group entity deferred — R1, R2
- Multi-group worldwide is long-term direction — R1
- App split: `users`, `competitions`, `tipping` (3 apps; pools to be its own app later) — R1, R2
- PostgreSQL — R1
- Whole model layer in scope (fields, constraints, signals, abstracts, scoring constants) — R1
- Winner-pick only; draw = 2 pt; correct = 1 pt; wrong = 0 — R1, R3, R3
- Scoring constants hardcoded for v1; universal across sports — R1, R2
- Round is first-class entity; games sort by round — R1
- Round-level lock (first match locks round) — R1
- `locks_at` stored, auto-populated by signal — R2, R3
- Tip editable until lock; reset = `pick → NULL` (not soft-delete) — R1, R3
- Audit history via `django-simple-history` on everything; M2M not audited — R1, R3
- No joker/double-points — R1
- Manual result entry for v1; signal re-fires on every score change — R1, R3
- Finals scored same as regular season — R1
- Custom `AbstractUser`; drop `username`; email login; add `display_name` (unique); keep `first_name`/`last_name` — R1, R3
- `django-allauth` for email + Google/Microsoft/Apple — R2
- Email verification required — R3
- Email/password fallback alongside social — R2
- Audit User logins via `UserLoginEvent` model — R3
- `Admin` group: full CRUD; `Tipper` group: explicit membership required — R2, R3
- Audit fields on every entity (`created_at`, `updated_at`, `created_by`, `updated_by`) — R1
- Soft-delete on user-facing entities only; `is_active` + `deleted_at` as distinct fields — R1, R3
- Soft-deleted user retains tip attribution on leaderboard — R3
- Current/forward only — no historical season import — R1
- Team↔League: flat M2M — R2
- UTC storage; UI renders local — R1
- DB constraint: Game `home_team` ≠ `away_team` — R3
- `Tip.round` denormalised — R3
- `Tip` unique on `(user, game)` where `is_active=True` — R3
- Pre-create Tip rows on Round/Game creation and Tipper-group join — R3
- Game hard-delete cascades to Tips; UI confirmation-gates — R3
