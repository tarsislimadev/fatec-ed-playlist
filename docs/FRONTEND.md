# FRONTEND PLAN - React Mobile-First App (Music Player)

## Goal

Build a mobile-first React app for a complete music player experience, aligned with [docs/PLAN.md](docs/PLAN.md) and the PDF requirements:
- library management
- mood queues by BPM
- replay next track
- playback history
- statistics
- menu screens for auth, legal pages, and profile

## Mandatory UI Rules

- Use whites and blues as the visual base.
- Use buttons instead of links for main interactions and menu navigation actions.
- All form components must be rendered as modals in their pages.
- Prioritize mobile-first layouts and interactions.

## Proposed Stack

- React 18+
- Vite + TypeScript
- React Router
- React Hook Form + Zod
- Axios
- Context API or Zustand
- CSS Modules or Tailwind

## Project Structure

```txt
frontend/
  src/
    app/
      App.tsx
      routes.tsx
      providers/
        AuthProvider.tsx
        PlayerProvider.tsx
    styles/
      tokens.css
      global.css
    components/
      ui/
        Button.tsx
        Input.tsx
        Modal.tsx
        SectionCard.tsx
      menu/
        MainMenuButtons.tsx
      forms/
        SignInForm.tsx
        SignUpForm.tsx
        PasswordForm.tsx
        ProfileForm.tsx
      player/
        TrackList.tsx
        MoodQueueCard.tsx
        StatsPanel.tsx
        HistoryList.tsx
    pages/
      IndexPage.tsx
      SignInPage.tsx
      SignUpPage.tsx
      PasswordPage.tsx
      TermsPage.tsx
      PrivacyPage.tsx
      ProfilePage.tsx
      LibraryPage.tsx
      QueuesPage.tsx
      HistoryPage.tsx
      StatsPage.tsx
    services/
      api.ts
      auth.service.ts
      profile.service.ts
      tracks.service.ts
      queues.service.ts
      playback.service.ts
      stats.service.ts
    constants/
      menu.ts
      routes.ts
    types/
      auth.ts
      track.ts
      queue.ts
      stats.ts
    main.tsx
```

## Color Tokens (Whites and Blues)

`src/styles/tokens.css`

```css
:root {
  --bg: #f5faff;
  --surface: #ffffff;
  --text: #102a43;
  --primary: #1565d8;
  --primary-strong: #0f4fae;
  --primary-soft: #dbeafe;
  --border: #c6d8f2;
  --muted: #6b84a3;
}
```

## Menus Required on Index

Index must expose button items for:
- sign in
- sign up
- password
- terms
- privacy
- profile

Additional player buttons can exist after authentication:
- library
- queues
- history
- stats

## Pages and Modal Forms

### 1) Sign In page

- Inputs: email, password.
- Form opens in modal.
- API: `POST /api/v1/auth/sign-in`

### 2) Sign Up page

- Inputs: name, email, password.
- Form opens in modal.
- API: `POST /api/v1/auth/sign-up`

### 3) Password page

- Input: email.
- Form opens in modal.
- API: `POST /api/v1/auth/password/request`

### 4) Terms page

- Text page (from API).
- API: `GET /api/v1/content/terms`

### 5) Privacy page

- Text page (from API).
- API: `GET /api/v1/content/privacy`

### 6) Profile page

- Filled inputs in modal.
- Inputs: name, email.
- APIs:
  - `GET /api/v1/profile/me`
  - `PATCH /api/v1/profile/me`

## Music Player Pages

### Library page

- Add, remove, search, and list tracks.
- Add track form modal with: titulo, artista, genero, bpm.
- APIs:
  - `POST /api/v1/tracks`
  - `DELETE /api/v1/tracks/{id}`
  - `GET /api/v1/tracks/{id}`
  - `GET /api/v1/tracks?titulo=...`
  - `GET /api/v1/tracks`

### Queues page

- Rebuild queues from library.
- View each mood queue without dequeue.
- APIs:
  - `POST /api/v1/queues/rebuild`
  - `GET /api/v1/queues/{mood}`

### Playback action

- Button: replay next for selected mood.
- API: `POST /api/v1/playback/next`

### History page

- Show playback history in order.
- API: `GET /api/v1/history`

### Stats page

- Show totals for library, queues, and played tracks.
- API: `GET /api/v1/stats`

## Routing Plan

```txt
/            -> IndexPage
/sign-in     -> SignInPage (modal form)
/sign-up     -> SignUpPage (modal form)
/password    -> PasswordPage (modal form)
/terms       -> TermsPage
/privacy     -> PrivacyPage
/profile     -> ProfilePage (modal form pre-filled)
/library     -> LibraryPage
/queues      -> QueuesPage
/history     -> HistoryPage
/stats       -> StatsPage
```

## Modal Standard

- One reusable modal component.
- Focus trap and keyboard close.
- Overlay close with safe submit handling.
- Used in all form pages: sign in, sign up, password, profile, add track.

## Mobile-First Rules

- Design base: 320px width.
- Touch targets >= 44px.
- Single-column default.
- Sticky bottom action area for key buttons on mobile.
- Tablet/desktop add wider containers and card grids.

## State and Flow

- Auth state provider for token/user session.
- Player state for selected mood and last played track.
- Queue/state refresh after add/remove track or queue rebuild.

## Validation

- name: required, min 2 chars
- email: valid format
- password: min 8 chars
- bpm: numeric and > 0

## Delivery Phases

1. Bootstrap app, routes, and theme tokens.
2. Build button/input/modal UI kit.
3. Implement index menu and auth/legal/profile pages.
4. Implement library and queue pages.
5. Implement playback, history, and stats pages.
6. Integrate all APIs and loading/error states.
7. Run responsive and accessibility checks.
8. Build and deploy.

## Deployment

- Build: `npm run build`
- Output: `dist/`
- Platforms: Vercel, Netlify, Cloudflare Pages, or Nginx static host
- Env:
  - `VITE_API_BASE_URL`

## Definition of Done

- index contains all required menu items
- all required forms are modal-based
- white/blue design language applied globally
- button-first interaction style implemented
- music player flows (library, queues, playback, history, stats) working end-to-end
