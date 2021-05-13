from datetime import datetime

from app.models import db, ma, cfg_db_schema

class TwitterFollowersModel(db.Model):
    __tablename__ = 'twitter_followers'
    __table_args__ =  {'schema': cfg_db_schema}
    id = db.Column(db.Integer, primary_key=True)
    id_follower = db.Column(db.String(256), nullable=False, unique=True)
    screen_name = db.Column(db.String(256), nullable=False)
    active = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    modified_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=db.func.current_timestamp())

    def  __repr__(self):
        return "<TwitterFollowers %r>" % (self.id)

class PostSchema(ma.SQLAlchemySchema):
    class Meta:
        model = TwitterFollowersModel
        fields = ("id", "user")
    # id = ma.auto_field()
    # user = ma.auto_field()