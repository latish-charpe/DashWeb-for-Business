import os
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load .env file BEFORE importing the Flask app so environment variables
# are available when app.py reads them at module level.
# On Render, environment variables are set in the dashboard (no .env needed).
# ---------------------------------------------------------------------------
load_dotenv()

from app import app  # noqa: E402 — intentionally after load_dotenv

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
