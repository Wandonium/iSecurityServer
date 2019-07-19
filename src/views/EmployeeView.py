from flask import request, json, Response, Blueprint, g
from ..models.EmployeeModel import EmployeeModel, EmployeeSchema
from ..models.GuardModel import GuardModel, GuardSchema
from ..shared.Authentication import Auth
import sqlalchemy

employee_api = Blueprint('employees', __name__)
employee_schema = EmployeeSchema()

@employee_api.route('/', methods=['POST'])
def create():
  """
  Create Employee Function
  """
  req_data = request.get_json()
  data, error = employee_schema.load(req_data)

  if error:
    return custom_response(error, 400)
  
  # check if employee already exist in the db
  employee_in_db = EmployeeModel.get_employee_by_time_in(data.get('time_in'))
  if employee_in_db:
    message = {'error': 'Employee already exist, please supply another employee time_in'}
    return custom_response(message, 400)

  # check if guard already exist in the db
  guard_in_db = GuardModel.get_guard_by_guardId(data.get('guard_id'))
  if not guard_in_db:
    message = {'error': 'Guard does not exist, please supply another guard id'}
    return custom_response(message, 400)
  
  # check if all employee sign_ins have a sign_out
  employees = EmployeeModel.get_employees_by_id(data.get('employeeId'))
  for emp in employees:
    if emp.time_out == None:
      message = {'error': 'Trying to sign in employee without first signing out'}
      return custom_response(message, 400)

  employee = EmployeeModel(data)
  employee.save(guard_in_db)
  ser_data = employee_schema.dump(employee).data
  return custom_response(ser_data, 201)

@employee_api.route('/<int:employee_id>', methods=['GET'])
@Auth.auth_required
def get_an_employee(employee_id):
  """
  Get a single employee
  """
  employee = EmployeeModel.get_one_employee(employee_id)
  if not employee:
    return custom_response({'error':'employee not found'}, 404)
  ser_employee = employee_schema.dump(employee).data
  return custom_response(ser_employee, 200)

@employee_api.route('/<int:emp_id>', methods=['PUT'])
@Auth.auth_required
def update(emp_id):
  """
  Update this
  """
  req_data = request.get_json()
  employee = EmployeeModel.get_one_employee(emp_id)
  if not employee:
    return custom_response({'error':'Employee not found'}, 404)
  data, error = employee_schema.load(req_data, partial=True)
  if error:
    return custom_response(error, 400)

  if employee.time_in > data.get('time_out'):
    message = {'error': 'time_out is ealier than time_in'}
    return custom_response(message, 400)

  employee.update(data)
  ser_employee = employee_schema.dump(employee).data
  return custom_response(ser_employee, 200)

@employee_api.route('/<int:emp_id>', methods=['DELETE'])
@Auth.auth_required
def delete(emp_id):
  """
  Delete an employee
  """
  employee = EmployeeModel.get_one_employee(emp_id)
  employee.delete()
  return custom_response({'message': 'deleted'}, 204)

@employee_api.route('/', methods=['GET'])
@Auth.auth_required
def get_all():
  employees = EmployeeModel.get_all_employees()
  ser_employees = employee_schema.dump(employees, many=True).data
  return custom_response(ser_employees, 200)


@employee_api.route('/login', methods=['POST'])
def login():
  req_data = request.get_json()
  data, error = employee_schema.load(req_data, partial=True)

  if error:
    return custom_response(error, 400)

  if not data.get('employeeId') or not data.get('password'):
    return custom_response({'error': 'you need an employee ID and password to login'}, 400)
  
  employee = EmployeeModel.get_receptionist(data.get('employeeId'))
  if not employee:
    return custom_response({'error':'invalid credentials'}, 400)

  if employee.role != 'Receptionist':
     return custom_response({'error':'invalid employee type'}, 400)

  if not employee.check_hash(data.get('password')):
    return custom_response({'error': 'invalid credentials'}, 400)

  ser_emp =  employee_schema.dump(employee).data
  return custom_response(ser_emp, 200)

@employee_api.route("/sign_out", methods=['GET'])
def sign_out():
  emps = EmployeeModel.get_employee_by_time_out()
  if emps:
    ser_data = employee_schema.dump(emps, many=True).data
    return custom_response(ser_data, 200)
  else:
    message = {'error':'No employees to sign out found. Sign In an employee first.'}
    return custom_response(message, 400)
  

def custom_response(res, status_code):
  """
  Custom Response Function
  """
  return Response(
    mimetype="application/json",
    response=json.dumps(res),
    status=status_code
  )

