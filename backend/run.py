"""Local development entrypoint.

`python run.py` starts Flask's built-in dev server. Production
deployments should run Gunicorn against the `app` object this module
exposes instead, e.g.:

    gunicorn run:app --bind 0.0.0.0:8000 --workers 4
"""
import os

from app import create_app

# Delay importing the scheduler module until runtime to avoid importing
# scheduler (and its job modules) when Flask CLI imports this module
# for commands like `flask db migrate` / `flask db upgrade`.
app = create_app(os.environ.get("FLASK_ENV", "development"))

if __name__ == "__main__":
    # Import scheduler here so merely importing `run` (e.g. by the
    # Flask CLI) does not pull in scheduler.jobs/ingestors at import time.
    from scheduler.scheduler import init_scheduler

    if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not app.debug:
        init_scheduler(app)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=app.config.get("DEBUG", False))
