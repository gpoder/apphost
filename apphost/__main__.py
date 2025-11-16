from . import create_dispatcher
from werkzeug.serving import run_simple

if __name__ == "__main__":
    app = create_dispatcher()
    run_simple("0.0.0.0", 5000, app, use_reloader=True)
