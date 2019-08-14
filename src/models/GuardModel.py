from flask import request, json, Response, Blueprint, g
from marshmallow import fields, Schema
from . import db, bcrypt

class GuardModel(db.Model):
  """
  Guard Model
  """

  # table name
  __tablename__ = 'guards'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  # security guard national id number
  guardId = db.Column(db.Integer, unique=True, nullable=False)
  guard_name = db.Column(db.String(128), nullable=False)
  phone_no = db.Column(db.BigInteger, unique=True, nullable=True)
  password = db.Column(db.String(128), nullable=False)
  security_company = db.Column(db.String(128), nullable=False)
  building_id = db.Column(db.Integer, db.ForeignKey('buildings.id'), nullable=False)



  # class constructor
  def __init__(self, data):
    """
    Class constructor
    """
    self.guardId = data.get('guardId')
    self.guard_name = data.get('guard_name')
    self.phone_no = data.get('phone_no')
    self.password = self.__generate_hash(data.get('password'))
    self.security_company = data.get('security_company')
    self.building_id = data.get('building_id')

  def save(self):
    db.session.add(self)
    db.session.commit()

  def update(self, data):
    for key, item in data.items():
      if key == 'password':
        self.password = self.__generate_hash(value) 
      setattr(self, key, item)
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  @staticmethod
  def get_all_guards():
    return GuardModel.query.all()

  @staticmethod
  def get_one_guard(id):
    return GuardModel.query.get(id)

  @staticmethod
  def get_guard_by_guardId(value):
    return GuardModel.query.filter_by(guardId=value).first()

  def __generate_hash(self, password):
    return bcrypt.generate_password_hash(password, rounds=10).decode("utf-8")
  
  # add this new method
  def check_hash(self, password):
    return bcrypt.check_password_hash(self.password, password)
  
  def __repr(self):
    return '<id {}>'.format(self.id)

class GuardSchema(Schema):
  """
  Guard Schema for serialization
  """
  id = fields.Int(dump_only=True)
  # security guard national id number
  guardId = fields.Int(required=True)
  guard_name = fields.Str(required=True)
  phone_no = fields.Int(required=True)
  password = fields.Str(required=True)
  security_company = fields.Str(required=True)
  building_id = fields.Int(required=True)