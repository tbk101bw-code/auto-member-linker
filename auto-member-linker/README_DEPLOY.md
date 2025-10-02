# Auto Member Linker Bot – Deploy Notes

This bot listens for clan-role changes and auto-adds the umbrella role (e.g., Knight).

## Files
- auto_member_linker.py        # your bot code (place at project root)
- deploy/requirements.txt      # Python deps
- deploy/Procfile              # process type for Heroku/Render (worker)

## Railway (fastest)
1) Create a new project.
2) Add repo/files. Ensure `auto_member_linker.py` is at the repo root.
3) Set Environment Variable: DISCORD_TOKEN = <your token>
4) Set Start Command: `python auto_member_linker.py`
5) Deploy.

## Render (free worker)
1) New > Background Worker.
2) Link your repo.
3) Start Command: `python auto_member_linker.py`
4) Add Environment Variable: DISCORD_TOKEN
5) Deploy.

## Heroku (requires a Worker dyno)
1) Create app.
2) Push your code (root has auto_member_linker.py).
3) In Settings > Buildpacks: add Python.
4) Add Config Var: DISCORD_TOKEN
5) In Resources: enable the Worker dyno (Procfile provided in deploy/). If Heroku expects Procfile at root, move it to project root.
6) Scale worker to 1.

## Local quick run
python -m venv .venv && source .venv/bin/activate
pip install -r deploy/requirements.txt
export DISCORD_TOKEN=your_token_here
python auto_member_linker.py

## Notes
- Turn on "Server Members Intent" in the Discord Developer Portal for your bot.
- Bot role must be above Knight + clan roles to manage them.
- Edit MEMBER_ROLE_NAME and CLAN_ROLE_NAMES in the script to match your server.
