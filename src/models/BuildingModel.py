from marshmallow import fields, Schema
from . import db
from sqlalchemy import func
from .GuardModel import GuardSchema
from .CompanyModel import CompanySchema


class BuildingModel(db.Model):
  """
  Building Model
  """

  # table name
  __tablename__ = 'buildings'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.String(128), nullable=True)
  street = db.Column(db.String(128), nullable=True)
  city = db.Column(db.String(128), nullable=True)
  no_of_floors = db.Column(db.Integer, nullable=False)
  longitude = db.Column(db.Float, nullable=False)
  latitude = db.Column(db.Float, nullable=False)
  guards = db.relationship('GuardModel', backref='buildings', cascade="all, delete-orphan", lazy='dynamic')
  companies = db.relationship('CompanyModel', backref='buildings', cascade="all, delete-orphan", lazy='dynamic')


  # class constructor
  def __init__(self, data):
    """
    Class constructor
    """
    self.name = data.get('name')
    self.street = data.get('street')
    self.city = data.get('city')
    self.no_of_floors = data.get('no_of_floors')
    self.longitude = data.get('longitude')
    self.latitude = data.get('latitude')

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
  def get_all_buildings():
    return BuildingModel.query.all()

  @staticmethod
  def get_one_building(id):
    return BuildingModel.query.get(id)

  @staticmethod
  def check_geo(lat, long):
    buildings = BuildingModel.query.all()
    for building in buildings:
      if building.latitude == lat and building.longitude == long:
        return True
      else:
        return False
  
  def __repr(self):
    return '<id {}>'.format(self.id)

class BuildingSchema(Schema):
  """
  The building's schema for serialization
  """
  id = fields.Int(dump_only=True)
  name = fields.Str(required=True)
  street = fields.Str(required=True)
  city = fields.Str(required=True)
  no_of_floors = fields.Int(required=True)
  longitude = fields.Float(required=True)
  latitude = fields.Float(required=True)
  guards = fields.Nested(GuardSchema, many=True, required=False)
  companies = fields.Nested(CompanySchema, many=True, required=False)