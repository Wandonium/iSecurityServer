from marshmallow import fields, Schema
from . import db
import datetime
import sqlalchemy
from .GuardModel import GuardSchema
from .BuildingModel import BuildingSchema
from .CompanyModel import CompanySchema

sign_in_guests = db.Table('sign_in_guests',
db.Column('id', db.Integer, primary_key=True),
db.Column('guard_id', db.Integer, db.ForeignKey('guards.id')),
db.Column('building_id', db.Integer, db.ForeignKey('buildings.id')),
db.Column('company_id', db.Integer, db.ForeignKey('companies.id')),
db.Column('guest_id', db.Integer, db.ForeignKey('guests.id'))
)


class GuestModel(db.Model):
  """
  Guest Model
  """

  # table name
  __tablename__ = 'guests'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  # guest's national id number
  guestId = db.Column(db.Integer, nullable=False)
  full_names = db.Column(db.String(128), nullable=False)
  phone_no = db.Column(db.BigInteger, nullable=True)
  gender = db.Column(db.String(10), nullable=False)
  reason_for_visit = db.Column(db.String(128), nullable=False)
  time_in = db.Column(db.DateTime)
  time_out = db.Column(db.DateTime)
  guards = db.relationship('GuardModel', secondary='sign_in_guests', lazy='subquery', backref=db.backref('guests', lazy=True))
  buildings = db.relationship('BuildingModel', secondary='sign_in_guests', lazy='subquery', backref=db.backref('guests', lazy=True))
  companies = db.relationship('CompanyModel', secondary='sign_in_guests', lazy='subquery', backref= db.backref('guests', lazy=True))


  # class constructor
  def __init__(self, data):
    """
    Class constructor
    """
    self.guestId = data.get('guestId')
    self.full_names = data.get('full_names')
    self.phone_no = data.get('phone_no')
    self.gender = data.get('gender')
    self.reason_for_visit = data.get('reason_for_visit')
    self.time_in = data.get('time_in')
    self.time_out = sqlalchemy.sql.null()

  def save(self, guard, building, company):
    self.guards.append(guard)
    self.buildings.append(building)
    self.companies.append(company)
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
  def get_all_guests():
    return GuestModel.query.all()

  @staticmethod
  def get_one_guest(id):
    return GuestModel.query.get(id)

  @staticmethod
  def get_guests_by_id(value):
    return GuestModel.query.filter_by(guestId=value)

  @staticmethod
  def get_guest_by_time_in(value):
    return GuestModel.query.filter_by(time_in=value).first()

  @staticmethod
  def get_guests_by_time_out():
    return GuestModel.query.filter_by(time_out=None)
  
  def __repr(self):
    return '<id {}>'.format(self.id)

class GuestSchema(Schema):
  """
  Guest Schema for serialization
  """
  id = fields.Int(dump_only=True)
  # security guard national id number
  guestId = fields.Int(required=True)
  full_names = fields.Str(required=True)
  phone_no = fields.Int(required=True)
  gender = fields.Str(required=True)
  reason_for_visit = fields.Str(required=True)
  time_in = fields.DateTime(required=True)
  time_out = fields.DateTime(required=True)
  guard_id = fields.Int(required=True)
  building_id = fields.Int(required=True)
  company_id = fields.Int(required=True)
  guards = fields.Nested(GuardSchema, many=True)
  buildings = fields.Nested(BuildingSchema, many=True)
  companies = fields.Nested(CompanySchema, many=True)