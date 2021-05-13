from app.models import db, cfg_db_schema
from datetime import datetime

class ApiLogModel(db.Model):
    __tablename__ = 'api_log'
    __table_args__ =  {'schema': cfg_db_schema}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(cfg_db_schema + '.users.id'), nullable=False)
    location = db.Column(db.String(500), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    modified_at = db.Column(db.DateTime, default=datetime.utcnow)

    def  __repr__(self):
        return "<ApiLog %r>" % (self.id)