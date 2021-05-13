from datetime import datetime

from app.models import db, cfg_db_schema

# post_platform = db.Table('post_platform',
#     db.Column('post_id', db.Integer, db.ForeignKey(cfg_db_schema + '.post.id'), primary_key=True),
#     db.Column('platform_id', db.Integer, db.ForeignKey(cfg_db_schema + '.platform.id'), primary_key=True),
#     db.Column('created_at', db.DateTime, default=datetime.utcnow),
#     ## or for multiple PK db.PrimaryKeyConstraint('post_id', 'platform_id')
#     schema=cfg_db_schema
# )

class PostPlatformModel(db.Model):
    __tablename__ = 'post_platform'
    __table_args__ =  {'schema': cfg_db_schema}
    post_id = db.Column(db.Integer, db.ForeignKey(cfg_db_schema + '.post.id'), primary_key=True)
    platform_id = db.Column(db.Integer, db.ForeignKey(cfg_db_schema + '.platform.id'), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    error = db.Column(db.Integer, default=0)
    error_msg = db.Column(db.Text, default='')
    post = db.relationship("PostModel", back_populates="platform")
    platform = db.relationship("PlatformModel", back_populates="posts")