# BACKEND PLAN - FastAPI REST API (Music Player)

## Goal

Transform the project into a full music player backend using FastAPI REST, preserving the playlist domain from the PDF and from [docs/PLAN.md](docs/PLAN.md):
- music library management
- mood queues by BPM
- playback flow
- playback history
- statistics
- auth and profile menus

## Scope from PDF and PLAN

Core business requirements to keep in API format:
- `Musica` with `id`, `titulo`, `artista`, `genero`, `bpm`
- linked-list/FIFO logic as domain engine
- mood queues by BPM
- replay next track and push to history
- list queue contents without removing
- statistics endpoint
- input validation and sequential non-reused IDs

## Proposed Stack

- Python 3.12+
- FastAPI + Uvicorn
- Pydantic
- SQLAlchemy 2.0 + Alembic
- PostgreSQL (prod), SQLite (dev)
- Passlib + bcrypt
- python-jose (JWT)
- pytest + httpx

## Project Structure

```txt
backend/
  app/
    main.py
    core/
      config.py
      security.py
      dependencies.py
    domain/
      playlist_engine.py      # linked-list + FIFO classes adapted from app.py
      bpm_classifier.py
    db/
      session.py
      models/
        user.py
        track.py
        playback_history.py
    schemas/
      auth.py
      profile.py
      track.py
      queue.py
      history.py
      stats.py
      content.py
    services/
      auth_service.py
      profile_service.py
      track_service.py
      queue_service.py
      playback_service.py
      content_service.py
    api/
      router.py
      v1/
        auth.py
        profile.py
        content.py
        tracks.py
        queues.py
        playback.py
        stats.py
        health.py
  tests/
    test_auth.py
    test_tracks.py
    test_queues.py
    test_playback.py
    test_stats.py
  requirements.txt
  .env.example
  Dockerfile
```

## Data Models

### User
- id
- name
- email (unique)
- password_hash
- created_at
- updated_at

### Track
- id (sequential, no reuse)
- titulo
- artista
- genero
- bpm
- created_at

### PlaybackHistory
- id
- user_id
- track_id
- mood
- played_at

## API Contract

### A) Menu and identity endpoints (requested)

#### `GET /api/v1/index`
Returns menu items:
- sign in
- sign up
- password
- terms
- privacy
- profile

#### `POST /api/v1/auth/sign-in`
Input:
- email
- password

#### `POST /api/v1/auth/sign-up`
Input:
- name
- email
- password

#### `POST /api/v1/auth/password/request`
Input:
- email

#### `GET /api/v1/content/terms`
Returns terms text.

#### `GET /api/v1/content/privacy`
Returns privacy text.

#### `GET /api/v1/profile/me`
Returns filled profile fields.

#### `PATCH /api/v1/profile/me`
Updates profile fields.

### B) Music player endpoints (core domain)

#### `POST /api/v1/tracks`
Add track to library (titulo, artista, genero, bpm).

#### `DELETE /api/v1/tracks/{id}`
Remove track from library by id.

#### `GET /api/v1/tracks/{id}`
Search track by id.

#### `GET /api/v1/tracks?titulo=...`
Search track by title.

#### `GET /api/v1/tracks`
List full library.

#### `POST /api/v1/queues/rebuild`
Rebuild mood queues from current library.

#### `GET /api/v1/queues/{mood}`
Show queue content without dequeue.

#### `POST /api/v1/playback/next`
Request body:
```json
{ "mood": "Relaxar|Focar|Animar|Treinar" }
```
Dequeues next song from selected mood queue and enqueues in history.

#### `GET /api/v1/history`
List playback history in playback order.

#### `GET /api/v1/stats`
Return:
- total tracks in library
- size of each mood queue
- total played tracks

## BPM Rules

- Relaxar: bpm <= 80
- Focar: 81 to 120
- Animar: 121 to 160
- Treinar: bpm > 160

## Validation Rules

- BPM must be numeric and > 0
- id must exist for removal/search
- replay next on empty queue returns handled error
- email unique and valid
- password min length 8

## Security Plan

- hash passwords only
- JWT bearer auth
- protect profile and music endpoints
- rate limit sign-in and password request

## Delivery Phases

1. Bootstrap FastAPI and health route.
2. Implement auth/menu/content/profile endpoints.
3. Implement track CRUD + search.
4. Implement queue rebuild and view.
5. Implement playback next + history + stats.
6. Add integration tests and OpenAPI examples.
7. Dockerize and deploy.

## Deploy Notes

- `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- production with reverse proxy
- env vars:
  - `DATABASE_URL`
  - `SECRET_KEY`
  - `ACCESS_TOKEN_EXPIRE_MINUTES`
  - `CORS_ORIGINS`

## Definition of Done

- all requested menu endpoints implemented
- all player domain endpoints implemented
- queue rebuild/playback/history/stats working end-to-end
- docs and tests updated
- API ready for React mobile-first frontend
