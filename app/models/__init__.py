import os

from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from app import app

db = SQLAlchemy()
ma = Marshmallow()
# cfg_db_schema = os.getenv('DB_SCHEMA')
cfg_db_schema = app.config['DB_SCHEMA']

##You can add here all the models and in View can use: from app.models. import UserModel  
from .UserModel import UserModel, user_role
from .UserTokenModel import UserTokenModel
from .PostModel import PostModel
from .PostPlatformModel import PostPlatformModel
from .RoleModel import RoleModel, role_permission
from .PermissionModel import PermissionModel
from .PostTypeModel import PostTypeModel
from .PlatformModel import PlatformModel
from .PlatformConfigModel import PlatformConfigModel
from .TwitterFollowersModel import TwitterFollowersModel
from .QuoteModel import QuoteModel
from .ApiLogModel import ApiLogModel

