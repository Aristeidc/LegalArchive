# Changelog

Each version was built on its own branch, merged into `main` with `--no-ff`
and tagged.

## v1.0.0 — Client directory release

- New-client form moved into the side panel as its own route, `/clients/new`
- Full restyle: warm low-contrast palette as CSS variables, two-column layout
  where the list and the panel scroll separately, single column on narrow
  screens
- Fira Sans self-hosted instead of loaded from Google Fonts
- Every on-screen text in Greek
- Placeholder in the empty side panel
- Clicking the open client in the list closes it; the open row is highlighted
- Enter-to-save behaviour shared by the add and edit forms (`useEnterArming`);
  Enter in the notes field adds a new line, and notes keep their line breaks
- Missing clients and failed loads show a message in the panel instead of
  replacing the whole page
- Edit form fields have proper labels; all forms use the same field order
- Loading text no longer pushes the layout down on every list refresh
- Backend rejects blank names on create (previously only on edit) and stores
  names trimmed
- Clearer API error messages
- Python dependencies pinned; SQLite side files gitignored
- Vite template leftovers removed; page language set to Greek

## v0.10.0 — Favorites

- `is_favorite` column; favorites sort to the top of the list and of search
  results
- Star toggle in the open client's panel, set through the existing PATCH
  endpoint
- Star shown beside favorites in the list

## v0.9.0 — Alphabetical order

- List and search results sorted by the normalized name, so Greek accents and
  case don't disturb the order
- Hint under the name field: surname, name, then other names

## v0.8.0 — Route loader for client detail

- The open client is fetched by a React Router loader instead of an effect;
  the router cancels stale requests itself
- After a save, the client is reloaded and the list refreshed

## v0.7.0 — Extract ClientEdit

- Edit form moved out of `ClientInfo` into its own component
- Cancel button
- Enter moves focus to the save button instead of saving straight away

## v0.6.0 — Delete a client

- Delete button with a two-step inline confirmation naming the client
- Permanent: there is no recovery

## v0.5.0 — Edit a client

- Edit the open client in place
- Only changed fields are sent; clearing a field sends `null`
- A failed save keeps the form and its edits on screen

## v0.4.0 — Routing

- React Router: each client has its own URL (`/clients/:id`), `/` redirects
  to `/clients`
- Client list and side panel as nested routes, so the list stays in place
  while the panel changes
- Searching no longer closes the open client

## v0.3.0 — Frontend fixes

- Fast clicks between clients can no longer show the wrong client
  (`AbortController` on both fetches)
- A failed load no longer leaves a stale error after the next success
- List rows reachable and openable with the keyboard

## v0.2.1 — Search fix

- Searching for `%` no longer returns every client
- `_` is matched literally instead of as a wildcard

## v0.2.0 — Backend cleanup

- `.gitattributes` for consistent line endings
- FastAPI lifespan handler instead of the deprecated `on_event`
- Explicit column lists instead of `SELECT *`
- Single-client query shared through one helper

## v0.1.0 — First version

- FastAPI backend: create, list, get, update and delete clients
- Greek name search ignoring case, accents and Unicode form
- React frontend: client list, search and client details
