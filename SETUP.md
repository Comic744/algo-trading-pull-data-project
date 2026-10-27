# Python venv + requirements cheat sheet

Project folder: ~/Documents/dev/algo-trading-pull-data-project

## What a venv is
A private copy of Python for this project only. Packages installed
inside it don't touch the rest of the system. The folder is `.venv/`.

## 1. Create it (once per project, or on a new machine)
    cd ~/Documents/dev/algo-trading-pull-data-project
    python3 -m venv .venv

## 2. Activate it (every new terminal)
    source .venv/bin/activate

The prompt now starts with (.venv). That means it's active.

## 3. Deactivate
    deactivate

## 4. Install packages (only while activated)
    pip install requests yfinance

## 5. Save the package list (after installing anything new)
    pip freeze > requirements.txt

`>` means "write the output into this file", replacing what was there.
Always re-run it after installing a package, then commit the file.

## 6. Recreate the environment from the list (new machine / fresh clone)
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

## 7. Run a script without activating
    .venv/bin/python myscript.py

This is what cron and systemd timers do later (full path to the
venv's python).

## Check what's going on
    echo $VIRTUAL_ENV     # path of the active venv (empty = none active)
    which python          # should point inside .venv
    pip list              # packages installed in the active venv

## Find all venvs on the machine
    find ~ -name pyvenv.cfg -printf '%h\n' 2>/dev/null

## Windows (untested)
    py -m venv .venv
    .venv\Scripts\activate.bat        (cmd)
    .venv\Scripts\Activate.ps1        (PowerShell)

If PowerShell blocks the script, run once:
    Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

## Git rules
- NEVER commit `.venv/`
- DO commit `requirements.txt`
- .gitignore should contain:
      .venv/
      __pycache__/
      *.db
      .env
      data/
- Test it: `touch test.db` then `git status`. test.db must not appear.

## Common mistakes
- "ModuleNotFoundError": the venv isn't activated, or the package
  isn't installed in it. Check for (.venv) in the prompt.
- pip freeze with nothing activated lists system packages. Activate first.
- Moved or renamed the project folder? The venv breaks. Delete `.venv/`
  and redo step 6.