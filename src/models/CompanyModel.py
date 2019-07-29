from marshmallow import fields, Schema
from . import db
from sqlalchemy import func
from .EmployeeModel import EmployeeSchema



class CompanyModel(db.Model):
  """
  Company Model
  """

  # table name
  __tablename__ = 'companies'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.String(128), nullable=False)
  email = db.Column(db.String(128), nullable=True)
  door_or_room = db.Column(db.String(128), nullable=True)
  floor_number = db.Column(db.Integer, nullable=False)
  phone_no = db.Column(db.BigInteger, unique=True, nullable=False)
  building_id = db.Column(db.Integer, db.ForeignKey('buildings.id'), nullable=False)
  employees = db.relationship('EmployeeModel', backref='companies', cascade="all, delete-orphan", lazy='dynamic')



  # class constructor
  def __init__(self, data):
    """
    Class constructor
    """
    self.name = data.get('name')
    self.email = data.get('email')
    self.door_or_room = data.get('door_or_room')
    self.floor_number = data.get('floor_number')
    self.phone_no = data.get('phone_no')
    self.building_id = data.get('building_id')

  def save(self):
    db.session.add(self)
    db.session.commit()

  def update(self, data):
    for key, item in data.items():
      setattr(self, key, item)
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  @staticmethod
  def get_all_companies():
    return CompanyModel.query.all()

  @staticmethod
  def get_one_company(id):
    return CompanyModel.query.get(id)

  @staticmethod
  def get_company_by_email(value):
    return CompanyModel.query.filter_by(email=value).first()
  
  def __repr(self):
    return '<id {}>'.format(self.id)

class CompanySchema(Schema):
  """
  The building's schema for serialization
  """
  id = fields.Int(dump_only=True)
  name = fields.Str(required=True)
  email = fields.Str(required=True)
  door_or_room = fields.Str(required=True)
  floor_number = fields.Int(required=True)
  phone_no = fields.Int(required=True)
  building_id = fields.Int(required=True)
  #employees = fields.Nested(EmployeeSchema, many=True, required=False)
