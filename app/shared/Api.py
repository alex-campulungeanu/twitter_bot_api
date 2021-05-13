from flask import g, current_app
from app import app

from app.models import db, ApiLogModel

class Api():
    @staticmethod
    def log_db(location, message):
        new_log = ApiLogModel(location=location, message=message, user_id=g.user.id)
        try:
            db.session.add(new_log)
            db.session.commit()
        except Exception as e:
            current_app.logger.info('Something wrong where log api')
            db.session.rollback() 
            # return api_response({'status': 'notok', 'error:': 'Post already added in DB'})

