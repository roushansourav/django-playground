# Django Playground — Design

## Purpose

Learning project for a developer experienced in other languages but new to Python/Django.
Goal: reach expert-level Django by building one real portfolio-quality full-stack app,
not a pile of disconnected tutorials.

## Learner profile

- Comfortable with general programming concepts; new to Python and Django specifically.
- Wants breadth across common real-world domains (content, commerce, collaboration, social)
  so the finished project reads as a credible portfolio piece.
- Learning format: concept explained, then an exercise attempted independently, then a
  reference solution built for comparison/review.

## Architecture

Single Django project, one app per domain, single React frontend consuming a DRF API.

Rejected alternatives:
- **Separate Django project per domain** — repeats settings/auth/config boilerplate four
  times; produces four disconnected toy repos instead of one portfolio piece.
- **One app repurposed per stage** — the four domains don't share models cleanly; forcing
  them into one app gets hacky once e-commerce and social features arrive.

```
django-playground/
  backend/
    manage.py
    config/            # project settings, root urls
    apps/
      core/            # custom User model, shared mixins/permissions
      blog/
      shop/
      tasks/
      social/
    tests/
  frontend/            # React (Vite)
  docs/superpowers/specs/
```

- Database: SQLite for all stages. Postgres migration is an explicit future stage, not
  part of this design.
- API: Django REST Framework, mounted alongside server-rendered views where relevant
  (Stage 1-2 use templates; Stage 3+ moves to DRF + React).
- Frontend: React (Vite), added once DRF endpoints exist (Stage 3).

## Curriculum stages

Each stage: concept explanation, then an exercise, then a reference solution, then review.
Every stage ends in something runnable — no dangling stubs.

0. **Python idioms refresher** — comprehensions, generators, decorators, context managers,
   dataclasses, typing, OOP patterns Django relies on. Short, since general programming
   knowledge already exists.
1. **Django fundamentals** — project/app setup, models, migrations, admin, views, URLs,
   templates. Build: Blog CRUD.
2. **Forms, auth, class-based views, testing basics** — extend Blog (comments, tags, user
   accounts). Introduce pytest-django.
3. **DRF fundamentals** — serializers, viewsets, routers, auth (session/token/JWT). Expose
   Blog as an API; wire up React to consume it.
4. **E-commerce app** — FK/M2M-heavy models, cart/checkout logic, DB transactions, signals,
   Celery for async work (order confirmation emails).
5. **Task manager app** — team/permission modeling, custom DRF permissions, nested routes,
   Django Channels for real-time board updates.
6. **Social app** — feeds, cursor pagination, Redis caching, N+1 query fixes, full-text
   search.
7. **Expert cross-cutting** — pytest-django + factory_boy in depth, CI, Docker, deployment,
   query profiling, security hardening, logging/monitoring, applied across all four apps.

## Exercise / solution workflow

Git branches, not parallel folders — a Django app can't cleanly exist twice in one
codebase, so branches are the mechanism:

- Learner works on `main`.
- Before each stage, a checkpoint tag is created (`stage-N-start`).
- After the learner's attempt, a reference implementation is built on `solution/stage-N`
  for comparison and review.

## Testing & tooling

pytest-django + factory_boy from Stage 2 onward. TDD encouraged per exercise where it fits
naturally, not forced where it doesn't (e.g. exploratory Stage 0 syntax drills).

## Out of scope (explicit)

- Postgres migration, mobile clients, payment gateway integration (real Stripe/etc. keys),
  production infra beyond a basic Docker/deploy walkthrough in Stage 7.
