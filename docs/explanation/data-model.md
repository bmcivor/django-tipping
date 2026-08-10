# Data model

A specification, not a description — none of this is built yet.

django-tipping runs sports tipping competitions. A group of people join a
competition, pick a winner for each match in a round, and are scored on how
many they got right. This document covers the model layer needed to get the
first of those working.

## Scope

The smallest model set that supports one flow:

> A registered user joins a competition and enters a tip for each match in a
> round.

Everything not forced by that sentence is out. This is pre-1.0 with no data to
preserve, so the set is expected to change as further flows are added.

## Apps

Two, split along master data and transactional data:

| App | Models | Holds |
|---|---|---|
| `matches` | `Season`, `Team`, `Match` | The draw. The same for everyone, and where an external feed will land. |
| `competitions` | `Competition`, `Membership`, `Tip` | What users create and do. |

`competitions` imports from `matches`, and nothing goes back the other way.
Keeping that direction one-way means ingestion code for the feed cannot reach
into user data, and the schedule can be reloaded without touching anyone's
tips.

`matches` rather than `fixtures`, because Django already uses "fixtures" for
`loaddata` seed data and pytest uses it for test fixtures.

## `matches`

### `Season`

| Field | Type | Notes |
|---|---|---|
| `name` | `CharField` | The competition, e.g. "NRL" |
| `year` | `PositiveSmallIntegerField` | e.g. 2026 |

Unique on `(name, year)` as `unique_season_name_year`, so NRL 2026 and AFL 2026
can coexist while the same season cannot be entered twice. A `CheckConstraint`
holds `year` between 1900 and 2100.

### `Team`

| Field | Type | Notes |
|---|---|---|
| `location` | `CharField` | e.g. "Penrith" |
| `mascot` | `CharField` | e.g. "Panthers" |
| `abbreviation` | `CharField` | e.g. "PEN" |

### `Match`

| Field | Type | Notes |
|---|---|---|
| `season` | `FK Season` | |
| `round_number` | `PositiveSmallIntegerField` | An integer, not a row — see below |
| `home_team` | `FK Team` | `related_name="home_matches"` |
| `away_team` | `FK Team` | `related_name="away_matches"` |
| `kickoff_time` | `DateTimeField` | Per-match. The round cutoff derives from it |
| `home_score` | `PositiveSmallIntegerField` | Nullable — absent until played |
| `away_score` | `PositiveSmallIntegerField` | Nullable — absent until played |

## `competitions`

### `Competition`

| Field | Type | Notes |
|---|---|---|
| `name` | `CharField` | e.g. "McIvor family NRL 2026" |
| `season` | `FK Season` | Which season it runs on |

### `Membership`

| Field | Type | Notes |
|---|---|---|
| `user` | `FK settings.AUTH_USER_MODEL` | |
| `competition` | `FK Competition` | |

Unique on `(user, competition)`. This is the `through` model for
`Competition.members = ManyToManyField(User, through="Membership")`.

### `Tip`

| Field | Type | Notes |
|---|---|---|
| `membership` | `FK Membership` | Not `User` — see below |
| `match` | `FK Match` | |
| `selected_team` | `FK Team` | |

Unique on `(membership, match)`.

## Decisions

**`Tip` points at `Membership`, not `User`.** A tip is only meaningful inside a
competition, and going through the membership means the database refuses a tip
in a competition the user never joined. The alternative is a `User` FK plus
that rule enforced in application code.

**`Team` is a model, and splits into `location` and `mascot`.** The flow alone
doesn't force either — two `CharField`s on `Match` would do — but teams are the
natural landing point for externally sourced data, so they need somewhere to
live, and the split is cheap to reverse if a feed turns out to supply only a
full name.

`location` rather than `city`, because the first part of a team's name often
isn't one. Wests Tigers' "Wests" is a club, GWS Giants' is a region, and the
Dolphins have nothing there at all — so it also allows blank.

**`Season` exists even though nothing reads it yet.** Round 1 recurs every
year, so matches need something to hang off that distinguishes them. A
competition points at one season, which is also what tells the app which
matches its members are tipping on.

The competition and the year are separate fields rather than one name, so the
uniqueness rule can be `(name, year)`. On a single `name` field the constraint
would either be nothing, or unique on a string that has to be spelled
identically every time.

**Scores are columns on `Match`, not a `Result` table.** There is at most one
result per match and it is two integers, so a separate table buys a join and
nothing else. Null means not played yet. A `Result` model would earn its place
if a result gained its own lifecycle — provisional then confirmed, say — or
enough fields to be worth isolating.

That holds while there is one sport. NRL has a single score per side; AFL is
goals, behinds and a total, and is always displayed that way. When a second
sport arrives, the likely shape is these two columns kept as the queryable
score plus a `JSONField` for the sport-specific breakdown, which is rendered
rather than filtered on. Multi-table inheritance and `django-polymorphic` are
the alternatives, and both cost more than the problem is worth until there is
a second sport to test the assumption.

**Round is an integer on `Match`, not its own model.** With `Season` present,
`(season, round_number)` identifies a round without a table. It becomes a model
when something needs to hang off it — a stored deadline, or a round-by-round
ladder.

## Out of scope

Deliberately absent, each waiting for a flow that needs it:

- Tip scoring, ladders, finals. Match scores are stored; nothing reads them yet
- More than one sport, and therefore `Sport` and per-sport score breakdowns
- Round as an entity, and stored per-round deadlines
- Configurable tip cutoffs
- Competition invitations, joining rules, private or public comps

## Open

**How the round cutoff is determined.** Tipping for a round closes at the first
game of that round, so the cutoff is the earliest `kickoff_time` among its
matches. Two ways to get there:

- Compute it — an aggregate over the round's matches on every check. No field,
  and it stays correct if the draw moves.
- Store it — a flag on `Match` marking the round's first game, or a stored
  deadline. Cheaper to read, and needs maintaining when the draw changes.

Either way a configurable cutoff, such as an offset before that time or a
per-competition override, is a later change.
