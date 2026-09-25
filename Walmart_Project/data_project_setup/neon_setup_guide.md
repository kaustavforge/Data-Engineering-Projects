# Neon Setup Guide (Windows / PowerShell + VS Code)

A complete step-by-step record of setting up Neon Postgres for a local project and connecting it to VS Code via MCP — based on the actual commands run in this session, corrected against Neon's current docs.

> **Note on the CLI name:** `neonctl` was renamed to `neon` in a recent release. Both names work — `neonctl` still works with no migration or re-auth needed, so everything below using `neonctl` is still valid. If you install fresh, you can use either `npx neon@latest ...` or `npx neonctl@latest ...` interchangeably.

---

## 1. Install the Neon CLI

No global install needed — `npx` downloads and runs it on demand.

```powershell
npx neonctl@latest --version
```

> To install globally (so you can just type `neonctl` or `neon` instead of `npx ...` every time):
> ```powershell
> npm i -g neonctl
> ```

---

## 2. Set up your Python project with `uv`

```powershell
uv init
uv sync
```

This creates `.venv`, `pyproject.toml`, and `uv.lock`.

Activate the virtual environment:
```powershell
.venv\Scripts\activate
```

### Pinning a specific Python version
If `.python-version` doesn't match what's installed, install the version you need:
```powershell
uv python install 3.11
```
Then delete and recreate the venv (make sure VS Code is fully closed first, or it may lock the files):
```powershell
Remove-Item -Recurse -Force .venv
uv sync
```
Verify:
```powershell
uv run python --version
```

---

## 3. Initialize and link a Neon project

```powershell
npx neonctl@latest init
```

Prompts you'll see, in order:

| Prompt | What to choose |
|---|---|
| How would you like to set up your coding agents? | "Neon plugin (recommended)" — or "Skip agent setup" if you're only using VS Code (see Step 4) |
| Which coding agents should get the plugin? | Only select if you use Claude Code / Cursor / Codex / Claude Desktop. **VS Code is not in this list** — set it up separately (Step 4). |
| Install the Neon plugin into these agents? | `n` if you don't use those tools |
| Link this project to a Neon project now? | `y` |
| Which project would you like to link? | "➕ Create new project…" (or pick an existing one) |
| Name for the new project | e.g. `walmart-project` |
| Region | Pick the one closest to you |
| Create `neon.ts` to manage setup as code? | `n` (optional — skip unless you want declarative infra-as-code) |

This will:
- Authenticate via OAuth (opens your browser)
- Create the project
- Write a `.neon` link file
- Pull connection variables into `.env.local`

### Rename `.env.local` → `.env`
Python tooling (e.g. `python-dotenv`) expects `.env` by default:
```powershell
Rename-Item .env.local .env
```
Make sure `.env` is listed in `.gitignore`.

Your `.env` should look like:
```dotenv
DATABASE_URL="postgresql://neondb_owner:<password>@<host>-pooler.<region>.aws.neon.tech/<database>?channel_binding=require&sslmode=require"
DATABASE_URL_UNPOOLED="postgresql://neondb_owner:<password>@<host>.<region>.aws.neon.tech/<database>?channel_binding=require&sslmode=require"
NEON_BRANCH=main
```

- **`DATABASE_URL`** (pooler): use for normal app code / frequent short connections.
- **`DATABASE_URL_UNPOOLED`**: use for migrations or long-running sessions.

---

## 4. Connect Neon to VS Code via MCP

`neonctl init` does **not** configure VS Code automatically — do this manually through VS Code's own MCP panel.

### Recommended: OAuth via the VS Code marketplace (this is what worked)

1. Open **Agent Customizations** in VS Code (Copilot / Chat settings → MCP Servers).
2. Search **"neon"** in the marketplace search box.
3. Click **Install** next to the "Neon" result.
4. A browser window opens: **"Connect Visual Studio Code to Neon"**.
   - Project access: "All projects you can access" (or scope to one project)
   - Leave **"Allow writes"** checked if you want the agent to create/modify things
5. Click **"Approve and continue to Neon"**.
6. Back in VS Code, the server should show **Running** (check via the **"…"** menu → *Show Output* if it doesn't start — it can take up to ~60 seconds to fully connect the first time).
7. Open **Copilot Chat**, switch the mode dropdown to **Agent**, and confirm Neon's tools appear (🔧 icon).

You can now ask things like:
> "List my Neon projects and databases"
> "Create a table in walmart_db from this CSV"
> "Query the live database — don't read local files — and tell me the primary key of the stores table"

> **Tip:** Be explicit about wanting a **live query** vs. reading local project files — some models default to reading a local `.sql` schema file if one exists, instead of querying the actual database.

### Alternative: manual MCP config (only if the marketplace install fails)

⚠️ **Correction:** an earlier version of this guide pointed to `@neondatabase/mcp-server-neon`, a package Neon's docs now mark as **deprecated**. Use the hosted server instead via `mcp-remote`:

Create `.vscode/mcp.json` in your project root:

**OAuth (recommended, no API key needed):**
```json
{
  "mcpServers": {
    "Neon": {
      "command": "npx",
      "args": ["-y", "mcp-remote@latest", "https://mcp.neon.tech/mcp"]
    }
  }
}
```

**API key (only if OAuth isn't an option, e.g. CI environments):**
```json
{
  "mcpServers": {
    "Neon": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote@latest",
        "https://mcp.neon.tech/mcp",
        "--header",
        "Authorization:${NEON_AUTH_HEADER}"
      ],
      "env": {
        "NEON_AUTH_HEADER": "Bearer <YOUR_NEON_API_KEY>"
      }
    }
  }
}
```

Generate a key if you need one:
```powershell
npx neonctl@latest api-keys create --name vscode-mcp
```

After saving the config: reload VS Code (`Ctrl+Shift+P` → "Reload Window"), open Copilot Chat, switch to **Agent** mode, and confirm Neon's tools appear.

### Security notes for MCP

- Neon officially recommends MCP for **development/testing only** — never connect it to a production database.
- Always review and authorize each tool call the agent proposes before it runs.
- Avoid using MCP against databases containing real PII — use anonymized/sample data.

---

## 5. Manage projects and databases from the terminal

### List projects
```powershell
npx neonctl@latest projects list
```

### Create a database
```powershell
npx neonctl@latest databases create --name walmart_db --project-id <PROJECT_ID>
```

### List databases in a project
```powershell
npx neonctl@latest databases list --project-id <PROJECT_ID>
```

### Get a database's connection string
```powershell
npx neonctl@latest connection-string --database-name walmart_db --project-id <PROJECT_ID>
```

### Delete a database
```powershell
npx neonctl@latest databases delete --name <DATABASE_NAME> --project-id <PROJECT_ID>
```

---

## 6. API keys

### Create a key
```powershell
npx neonctl@latest api-keys create --name <KEY_NAME>
```
> Copy the key immediately — it's shown only once.

### List keys
```powershell
npx neonctl@latest api-keys list
```

### Revoke a key
```powershell
npx neonctl@latest api-keys revoke <KEY_ID>
```

> **Security note:** the recommended VS Code MCP connection uses OAuth (browser login), not an API key — so revoking a key you generated separately (e.g. for manual testing) won't break the MCP chat integration. Rotate/revoke any key you've shared or pasted anywhere outside your local `.env`.

---

## 7. Roles (owners)

Every new project gets a default role, `neondb_owner`, which owns every database created afterward unless you specify otherwise.

### Create a custom role
```powershell
npx neonctl@latest roles create --name <ROLE_NAME> --project-id <PROJECT_ID>
```

### Create a database owned by a specific role
```powershell
npx neonctl@latest databases create --name <DB_NAME> --owner-name <ROLE_NAME> --project-id <PROJECT_ID>
```

> Note: there's no direct "change owner" command — to switch an existing database's owner, create a new database with the desired role and migrate data over.

---

## 8. Quick reference: setting up a NEW project (after initial setup)

You do **not** need to repeat `uv init`, `neonctl init`, the API key, or the VS Code MCP setup for a new project — those were one-time steps. Only the actions below are needed.

### Option A — PowerShell

**1. Create the new project:**
```powershell
npx neonctl@latest projects create --name <new-project-name>
```
This returns a new `Project Id` — copy it, you'll need it below.

**2. Create a database inside it** (a project gets a default `neondb`, but you can add your own):
```powershell
npx neonctl@latest databases create --name <db_name> --project-id <NEW_PROJECT_ID>
```

**3. Only if your Python code needs to connect to it** — get the connection string and add it to `.env`:
```powershell
npx neonctl@latest connection-string --database-name <db_name> --project-id <NEW_PROJECT_ID>
```
```dotenv
DATABASE_URL="<paste the pooled connection string here>"
```

**4. Confirm it exists:**
```powershell
npx neonctl@latest projects list
npx neonctl@latest databases list --project-id <NEW_PROJECT_ID>
```

### Option B — VS Code Copilot Chat (Agent mode)

No new setup needed — your existing MCP connection already covers all projects in your account. Just ask, e.g.:

> "Create a new Neon project called retail-analytics"

> "Create a database called sales_db inside retail-analytics"

> "List all my Neon projects and databases"

The agent will create everything and can query it live immediately — you only need the PowerShell connection string (Option A, step 3) if you're writing your own Python/app code that needs to connect outside of chat.

---

## Quick reference: Ghost → Neon command mapping

| Ghost | Neon (`neonctl` / `neon`) |
|---|---|
| `ghost create --name X` | `npx neonctl@latest databases create --name X --project-id <ID>` |
| `ghost list` | `npx neonctl@latest databases list --project-id <ID>` + `npx neonctl@latest projects list` |
| `ghost connect X` | `npx neonctl@latest connection-string --database-name X --project-id <ID>` |
| `ghost init` (MCP setup) | `npx neonctl@latest init` (project setup) **+** VS Code's own MCP marketplace panel (chat setup) |