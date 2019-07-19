from marshmallow import fields, Schema
from . import db
import datetime
import sqlalchemy

class AppLogsModel(db.Model):
  """
  AppLogs Model. Table for tracking the logins and logouts of security guards and receptionists
  """

  # table name
  __tablename__ = "app_logs"

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  user_id = db.Column(db.Integer, nullable=False)
  login_time = db.Column(db.DateTime)
  logout_time = db.Column(db.DateTime)



  # class constructor
  def __init__(self, data):
    """
    Class constructor
    """
    self.user_id = data.get('user_id')
    self.login_time = datetime.datetime.utcnow()
    self.logout_time = sqlalchemy.sql.null()

  def save(self):
    db.session.add(self)
    db.session.commit()

  def update(self, data):
    for key, item in data.items():
      setattr(self, key, item)
    self.logout_time = datetime.datetime.utcnow()
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  @staticmethod
  def get_all_app_logs():
    return AppLogsModel.query.all()

  @staticmethod
  def get_one_app_log(id):
    return AppLogsModel.query.get(id)
  
  def __repr(self):
    return '<id {}>'.format(self.id)

class AppLogsSchema(Schema):
  """
  AppLogs Schema for serialization
  """
  id = fields.Int(dump_only=True)
  user_id = fields.Int(required=True)
  login_time = fields.DateTime(dump_only=True)
  logout_time = fields.DateTime(dump_only=True)
  