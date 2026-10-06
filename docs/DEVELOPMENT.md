# LegalArchive — developer notes

Internal client directory for a small Greek law firm — the first part of a
larger archive system. Runs on the office network; the interface is in Greek.

**Status: v1.0.0** — the client directory is complete. The document archive
(the project's original goal) is next; see [TODO.md](TODO.md). Release history
is in [CHANGELOG.md](../CHANGELOG.md).

## What it does

- Client list, alphabetical, with favorites pinned to the top
- Name search that ignores case, accents and Unicode form (`παπαδοπουλος`
  finds `Παπαδόπουλος`)
- Each client has its own URL (`/clients/4`) — bookmarks, the back button and
  several clients in separate browser tabs all work
- Add, view, edit and delete clients in a side panel next to the list
- One shared favorites list for the whole firm

## Stack

| Part     | Technology                                              |
|----------|---------------------------------------------------------|
| Backend  | Python, FastAPI, Uvicorn, SQLite (built-in `sqlite3`), Pydantic |
| Frontend | React 19, TypeScript, Vite, React Router (data mode)    |
| Font     | Fira Sans, self-hosted via `@fontsource/fira-sans`      |

## Requirements

- Python 3.10+
- Node.js 20.19+ or 22.12+ (required by Vite)

## Setup

Backend:

```powershell
cd server
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

On macOS/Linux the activation line is `source venv/bin/activate`.

Frontend:

```powershell
cd client
npm install
```

## Running

Two terminals, one per half.

```powershell
# terminal 1
cd server
venv\Scripts\Activate.ps1
uvicorn main:app --reload
```

```powershell
# terminal 2
cd client
npm run dev
```

- App: **http://localhost:5173**
- API: `http://localhost:8000`, with interactive docs at
  **http://localhost:8000/docs**

The `/docs` form pre-fills request bodies with placeholder values like
`"string"`. Clear the fields you aren't testing, or they are saved as real data.

Other frontend scripts: `npm run build` (type-check + production build into
`client/dist`), `npm run preview` (serve that build), `npm run lint` (oxlint).

## Project layout

```
LegalArchive/
├── client/
│   ├── index.html
│   └── src/
│       ├── main.tsx              entry point — fonts, global CSS, <RouterProvider>
│       ├── router.tsx            every URL and what renders there, plus the client loader
│       ├── RootLayout.tsx        header + <Outlet/>
│       ├── ClientsPage.tsx       list fetch, search state, side-panel <Outlet/>
│       ├── types.ts              Client, ClientForm, ClientCreate, ClientUpdate
│       ├── index.css             all styles; colours as :root variables
│       ├── hooks/
│       │   └── useEnterArming.ts
│       └── components/
│           ├── ClientList.tsx    list rows as links, favorite star
│           ├── ClientSearch.tsx
│           ├── ClientInfo.tsx    read-only view, favorite toggle, delete
│           ├── ClientEdit.tsx    edit form, sends only changed fields
│           ├── ClientAdd.tsx     new-client form
│           ├── ClientError.tsx   not-found / load-failed message in the panel
│           └── EmptyPanel.tsx    placeholder when no client is open
└── server/
    ├── main.py                   FastAPI app, CORS, routes
    ├── database.py               connection, schema, fetch_client, CLIENT_COLUMNS
    ├── models.py                 Pydantic request/response models
    ├── text_normalizer.py        Greek name normalization for search
    ├── requirements.txt
    └── LegalArchive.db           created on first run — gitignored
```

## Frontend routes

| URL            | Side panel shows                         |
|----------------|------------------------------------------|
| `/`            | redirects to `/clients`                  |
| `/clients`     | placeholder (`EmptyPanel`)               |
| `/clients/new` | new-client form (`ClientAdd`)            |
| `/clients/:id` | the client (`ClientInfo`); `ClientError` if missing or the load fails |

The list stays mounted on every `/clients/*` route; only the panel swaps.
Clicking the open client in the list again closes it.

## API endpoints

| Method | Path            | Notes                                                        |
|--------|-----------------|--------------------------------------------------------------|
| GET    | `/clients`      | All clients, favorites first, then alphabetical. Optional `?name=` filter. |
| GET    | `/clients/{id}` | One client. 404 if absent.                                   |
| POST   | `/clients`      | Create. `full_name` required; blank → 400. Stored trimmed.   |
| PATCH  | `/clients/{id}` | Partial update — send only changed fields. Empty body → 400; null or blank `full_name` → 400; 404 if absent. |
| DELETE | `/clients/{id}` | **Permanent.** 204 on success, 404 if absent.                |

## Data model

One table, `clients`.

| Column                 | Notes                                                  |
|------------------------|--------------------------------------------------------|
| `client_id`            | Server-generated                                       |
| `full_name`            | Required. As entered, for display                      |
| `full_name_normalized` | Server-generated, for search and sorting only. Never returned by the API |
| `is_favorite`          | `INTEGER NOT NULL DEFAULT 0`, returned as a boolean     |
| `phone`, `email`, `afm`, `address`, `notes` | Optional. Stored as NULL when empty, never `""` |
| `created_at`, `updated_at` | Server-generated ISO-8601 UTC strings              |

`afm` (ΑΦΜ) is TEXT, not INTEGER — it can have leading zeros and is never used
in arithmetic.

There is one free-text name field, not separate first/last/father's-name
fields: the firm's existing records are inconsistent (sometimes only a
surname, sometimes a full name with πατρώνυμο, sometimes a company). A hint
under the name input asks staff for *surname, name, then other names*, and
the alphabetical order follows however each name was entered.

## Name search

Greek names vary in three independent ways that all break exact matching:

- **Case** — SQLite's `LIKE` and default sort handle ASCII only, not Greek
- **Accents** — `Παπαδόπουλος` vs `Παπαδοπουλος`
- **Unicode form** — `ό` may be stored as one character or as `ο` plus a
  combining accent. Visually identical, different bytes.

So each name is stored twice: the original in `full_name` for display, and a
normalized copy in `full_name_normalized` for matching and sorting. Search
terms go through the same normalizer, so normalized is compared with
normalized.

`text_normalizer.py`: NFC → NFD → strip combining marks → casefold (which
also turns final `ς` into `σ`) → replace punctuation with spaces → collapse
whitespace.

The normalized copy is derived data and is recomputed wherever the name
changes — in POST and PATCH. Missing one would leave a client searchable only
under their old name.

`%` and `_` typed into the search box are escaped, so they match literally
rather than acting as SQL wildcards. A search that normalizes to nothing
(e.g. only punctuation) returns no results.

## Design decisions

- **Hard delete only.** No soft delete, no recycle bin, no audit trail. The
  two-step confirmation in the panel (*Διαγραφή …;* → ΝΑΙ / ΟΧΙ) is the only
  safeguard.
- **PATCH sends only what changed.** The edit form compares each field with
  the loaded client. The backend uses `model_dump(exclude_unset=True)`, so an
  omitted field is left alone, while an explicit `null` clears it. The
  favorite star uses the same endpoint with a one-field body.
- **React Router in data mode** (`createBrowserRouter`), not framework mode —
  framework mode's main feature is server rendering, which would mean a Node
  server in front of FastAPI for no benefit on an internal tool.
- **The open client is loaded by a route loader**, which cancels stale
  requests itself and sends errors to `ClientError`. The list still uses an
  effect with an `AbortController`, because it depends on search text held in
  component state; moving search into the URL would let it become a loader
  too (see TODO).
- **Enter does not submit forms outright.** In the add and edit forms, Enter
  moves focus to the save button and a second Enter saves (`useEnterArming`).
  Enter inside the notes field adds a new line.
- **CORS** allows only `http://localhost:5173`, without credentials.
- **The font is self-hosted** so the app works offline and sends no visitor
  data to Google.

## Database and personal data

`LegalArchive.db` is created automatically on first run, in `server/`.

It is **gitignored and must stay that way**, along with SQLite's side files
(`*.db-*`). It holds client names, addresses and ΑΦΜ — personal data under
GDPR. The GitHub repository is private for the same reason.

Schema changes: `CREATE TABLE IF NOT EXISTS` does nothing to an existing
table. While there is only test data, delete the `.db` file and restart. Once
real data exists, changes need `ALTER TABLE` plus a migration script.

## Deployment notes

Not packaged for installation yet (see TODO). When it is:

- The API address `http://localhost:8000` is written into the frontend source
  and has to become configurable.
- The CORS origin in `main.py` must match wherever the frontend is served from.
- The server serving `client/dist` must answer every unknown path with
  `index.html`, or opening `/clients/4` directly returns 404. Vite's dev and
  preview servers already do this.

## Git workflow

GitHub Flow. `main` always works; each version is built on its own branch,
merged with `--no-ff` so the branch stays visible in history, and tagged.

```powershell
git switch -c feat/some-name
# work, commit
git switch main
git merge --no-ff feat/some-name
git branch -d feat/some-name
git tag -a v1.1.0 -m "Short description"
git push origin main
git push origin v1.1.0
```

A normal push sends commits only; tags are pushed separately. Feature
branches stay local.
