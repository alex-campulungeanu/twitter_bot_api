import os
import sys
from colorama import init
from termcolor import colored

init()

##The enviroments needs to be loaded first !!!
from pathlib import Path
from dotenv import load_dotenv
env_name = os.getenv('FLASK_ENV')
if env_name == 'production':
    env_path = Path('.') / '.env.production'
elif env_name == 'development':
    env_path = Path('.') / '.env'
else:
    sys.exit(colored('FLASK_ENV accepted values are: production / development', 'red'))

load_dotenv(dotenv_path=env_path, verbose=True)


from flask import Flask
from flask_cors import CORS

from app.config import app_config, setup_logger
from flask_migrate import Migrate
from flask_mail import Mail

migrate = Migrate()
mail = Mail()

# basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
CORS(app) ## enable CORS on all routes
app.config.from_object(app_config[env_name])

app.logger.info(f"\n \
######################################################### \n \
#   ENV:        {env_name}                                \n \
#   DB_HOST:    {app.config['DB_HOST']}                   \n \
#   ENV:        {env_name}                                \n \
######################################################### ")

# Set up extensions
from app.models import db, ma
db.init_app(app)
ma.init_app(app)
migrate.init_app(app, db)
mail.init_app(app)

# Set up logging
setup_logger(app)

from app.views import register_blueprint_view
register_blueprint_view(app)

from app.commands import register_commands
register_commands(app)