
from . import create_dispatcher
from werkzeug.serving import run_simple

if __name__ == "__main__":
    run_simple("0.0.0.0",5000,create_dispatcher(),use_reloader=True)
