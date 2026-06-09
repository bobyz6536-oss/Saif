# CapCut MCP integration

CapCut does **not** provide an official public API. The integration here uses
the open-source **CapCutAPI** project (HTTP API + MCP protocol), which exposes
CapCut editing capabilities (adding media, text, effects, keyframe animations,
exporting drafts) to AI assistants.

- Project: https://github.com/sun-guannan/CapCutAPI (mirror: https://github.com/ashreo/CapCutAPI)
- MCP docs: https://github.com/sun-guannan/VectCutAPI/blob/main/MCP_Documentation_English.md

> Note: the previous config referenced `uvx capcut-ai-editor`, which does not
> work — `capcut-ai-editor` is a GitHub repo, not a PyPI package, so `uvx`
> cannot install it. That entry has been replaced.

## Setup

1. Run the setup script (clones the repo and installs MCP dependencies):

   ```bash
   ./scripts/setup-capcut-mcp.sh
   # or pick a custom location:
   CAPCUT_DIR=/path/to/CapCutAPI ./scripts/setup-capcut-mcp.sh
   ```

2. Edit `.claude/settings.json` and replace `REPLACE_WITH_CAPCUT_DIR` (in the
   `capcut` entry's `cwd` and `PYTHONPATH`) with the absolute path where the
   repo was cloned — by default `$HOME/CapCutAPI`.

   You should also point `command` at the venv interpreter created by the
   script for isolated dependencies, e.g.:

   ```json
   "capcut": {
     "command": "/home/you/CapCutAPI/venv-capcut/bin/python",
     "args": ["mcp_server.py"],
     "cwd": "/home/you/CapCutAPI",
     "env": { "PYTHONPATH": "/home/you/CapCutAPI", "DEBUG": "0" }
   }
   ```

3. Configure `config.json` inside the CapCutAPI directory (created from
   `config.json.example`) with your CapCut draft folder paths if needed.

4. Restart Claude Code so the `capcut` MCP server is picked up.

## Notes

- Requires Python 3.10+.
- The CapCut MCP server runs locally and operates on CapCut's local draft/
  project files; it works best on the machine where CapCut Desktop is installed.
