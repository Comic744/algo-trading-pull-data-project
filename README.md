# Stock Pull

A small project to practice skills relevant to algo trading and DevOps. Every weekday after the US market closes, it downloads daily prices from Yahoo Finance and stores them in a local SQLite database. The script runs inside a Docker container, started by a systemd timer.

## How it works

```
 systemd timer (Mon-Fri 17:00)
        |
        v
 systemd service
        |  docker run --rm ...
        v
 +---------------------------+
 | container (image:         |        Yahoo Finance
 | stock-pull)               |  --->  (via yfinance)
 |   stock-pull.py           |  <---  daily prices
 |        |                  |
 +--------|------------------+
          | bind mount: ./data  ->  /app/data
          v
     data/stocks.db  (SQLite, on the host)
```

1. The timer fires at 17:00 on weekdays. If the laptop was off, `Persistent=true` runs the missed job at the next start.
2. The service runs `docker run`, mounting the host's `data/` folder into the container.
3. For each symbol, the script reads the last stored date, downloads everything from that date to today, and writes it to the database.
4. If any symbol fails, the script exits with code 1, so systemd marks the run as failed.

## Design decisions

- **Composite primary key `(Symbol, Date)` with `INSERT OR REPLACE`:** running the script twice never duplicates data, and the latest (possibly unfinished) day gets refreshed on the next run.
- **Catch-up from the last stored date, per symbol:** if the machine was off for days or weeks, one run fills the whole gap. A new symbol gets its first month of history.
- **Non-zero exit code on failure:** a failed download shows up as a failed service in `systemctl status`, not just a line buried in the logs. Symbols are processed independently, so one failure doesn't block the others.
- **`DB_PATH` environment variable:** the same script runs on the laptop (default `stocks.db`) and in the container (`/app/data/stocks.db`) without code changes.
- **Bind-mounted data folder, non-root user:** the database outlives the container (which is deleted after every run), and the file stays owned by the host user.
- **Named columns in the `INSERT` and a single `STOCKS` table:** adding symbols needs no schema change.

## Run it

### Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python stock-pull.py
```

The database is created as `stocks.db` in the current folder. Edit the `symbols` list in `stock-pull.py` to change what is tracked.

### With Docker

```bash
docker build -t stock-pull .
mkdir -p data
docker run --rm \
  -v "$(pwd)/data:/app/data" \
  --user "$(id -u):$(id -g)" \
  stock-pull
```

Run it from the project folder. The data ends up in `data/stocks.db`.

### On a schedule (systemd, user units)

Edit the paths in `systemd/stock-pull.service` to match your project location, then:

```bash
systemctl --user link "$(pwd)/systemd/stock-pull.service"
systemctl --user link "$(pwd)/systemd/stock-pull.timer"
systemctl --user daemon-reload
systemctl --user enable --now stock-pull.timer
systemctl --user list-timers          # check the next run
journalctl --user -u stock-pull.service   # logs of past runs
```

## Limitations

- yfinance is an unofficial wrapper around Yahoo Finance, so it can break or be rate-limited without notice.
- An empty download is treated as a failure. After a holiday this could be a false alarm, because the script can't tell it apart from a real error.
- Missing days in the middle of the data are not detected. Catch-up only looks at the most recent stored date.
- Prices are rounded to 2 decimals, which is fine for large US stocks but too coarse for penny stocks or crypto.
- SQLite allows one writer at a time, which is fine for a single scheduled job.
- A user timer only runs while the user session is active (unless lingering is enabled). Missed runs are caught up at the next start.
- yfinance prints pandas deprecation warnings, which make the logs noisy.

## Roadmap

Planned, not done yet:

- Run the job as a Kubernetes CronJob with a persistent volume
- Move from SQLite to PostgreSQL
- Monitoring and alerting (Prometheus, Grafana, Alertmanager)
- CI with GitHub Actions