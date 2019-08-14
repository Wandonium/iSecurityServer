from marshmallow import fields, Schema
from . import db, bcrypt
import datetime
import sqlalchemy
from .GuardModel import GuardSchema

sign_in_employees = db.Table('sign_in_employees',
db.Column('guard_id', db.Integer, db.ForeignKey('guards.id'), primary_key=True),
db.Column('employee_id', db.Integer, db.ForeignKey('employees.id'), primary_key=True)
)

class EmployeeModel(db.Model):
  """
  Employee Model
  """

  # table name
  __tablename__ = 'employees'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  # employee's national id number
  employeeId = db.Column(db.Integer, nullable=False)
  name = db.Column(db.String(128), nullable=False)
  phone_no = db.Column(db.BigInteger, nullable=True)
  password = db.Column(db.String(128), nullable=True)
  # receptionist or other employee
  role = db.Column(db.String(128), nullable=False)
  time_in = db.Column(db.DateTime)
  time_out = db.Column(db.DateTime)
  company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
  guards = db.relationship('GuardModel', secondary='sign_in_employees', lazy='subquery', backref=db.backref('employees', lazy=True))


  # class constructor
  def __init__(self, data):
    """
    Class constructor
    """
    self.employeeId = data.get('employeeId')
    self.name = data.get('name')
    self.phone_no = data.get('phone_no')
    self.password = self.__generate_hash(data.get('password'))
    self.role = data.get('role')
    self.time_in = data.get('time_in')
    self.time_out = sqlalchemy.sql.null()
    self.company_id = data.get('company_id')

  def save(self, guard):
    self.guards.append(guard)
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
  def get_all_employees():
    return EmployeeModel.query.all()

  @staticmethod
  def get_one_employee(id):
    return EmployeeModel.query.get(id)

  @staticmethod
  def get_employee_by_time_in(value):
    return EmployeeModel.query.filter_by(time_in=value).first()

  @staticmethod
  def get_employees_by_id(value):
    return EmployeeModel.query.filter_by(employeeId=value)

  @staticmethod
  def get_employee_by_time_out():
    return EmployeeModel.query.filter_by(time_out=None)

  @staticmethod
  def get_receptionist(empId):
    return EmployeeModel.query.filter_by(employeeId=empId).first()

  @staticmethod
  def get_all_receptionists():
    return EmployeeModel.query.filter_by(role="Receptionist")

  def __generate_hash(self, password):
    return bcrypt.generate_password_hash(password, rounds=10).decode("utf-8")
  
  # add this new method
  def check_hash(self, password):
    return bcrypt.check_password_hash(self.password, password)
  
  def __repr(self):
    return '<id {}>'.format(self.id)

class EmployeeSchema(Schema):
  """
  Employee Schema for serialization
  """
  id = fields.Int(dump_only=True)
  # security guard national id number
  employeeId = fields.Int(required=True)
  guard_id = fields.Int(required=True)
  name = fields.Str(required=True)
  phone_no = fields.Int(required=True)
  password = fields.Str(required=True)
  role = fields.Str(required=True)
  time_in = fields.DateTime(required=True)
  time_out = fields.DateTime(required=True)
  company_id = fields.Int(required=True)
  guards = fields.Nested(GuardSchema, many=True)