from flask import request, json, Response, Blueprint, g
from ..models.GuardModel import GuardSchema, GuardModel
from ..models.AppLogs import AppLogsSchema, AppLogsModel
from ..shared.Authentication import Auth

guard_api = Blueprint('guards', __name__)
guard_schema = GuardSchema()

@guard_api.route('/', methods=['POST'])
def create():
  """
  Create Guard Function
  """
  req_data = request.get_json()
  data, error = guard_schema.load(req_data)

  if error:
    return custom_response(error, 400)
  
  # check if guard already exist in the db
  guard_in_db = GuardModel.get_guard_by_guardId(data.get('guardId'))
  if guard_in_db:
    message = {'error': 'Guard already exist, please supply another guard ID'}
    return custom_response(message, 400)

  # check for unique phone number
  guards = GuardModel.get_all_guards()
  for guard in guards:
    if guard.phone_no == data.get('phone_no'):
      message = {'error':'Guard must have a unique phone number'}
      return custom_response(message, 400)
  
  guard = GuardModel(data)
  guard.save()

  ser_data = guard_schema.dump(guard).data
  token = Auth.generate_token(ser_data.get('id'))

  return custom_response({'jwt_token': token, 'guard': ser_data}, 201)

@guard_api.route('/<int:guard_id>', methods=['GET'])
@Auth.auth_required
def get_a_guard(guard_id):
  """
  Get a single guard
  """
  guard = GuardModel.get_one_guard(guard_id)
  if not guard:
    return custom_response({'error':'guard not found'}, 404)
  ser_guard = guard_schema.dump(guard).data
  return custom_response(ser_guard, 200)

@guard_api.route('/this', methods=['PUT'])
@Auth.auth_required
def update():
  """
  Update this
  """
  req_data = request.get_json()
  data, error = guard_schema.load(req_data, partial=True)
  if error:
    return custom_response(error, 400)

  guard = GuardModel.get_one_guard(g.guard.get('id'))
  guard.update(data)
  ser_guard = guard_schema.dump(guard).data
  return custom_response(ser_guard, 200)

@guard_api.route('/this', methods=['DELETE'])
@Auth.auth_required
def delete():
  """
  Delete a guard
  """
  guard = GuardModel.get_one_guard(g.guard.get('id'))
  guard.delete()
  return custom_response({'message': 'deleted'}, 204)

@guard_api.route('/this', methods=['GET'])
@Auth.auth_required
def get_this():
  """
  Get this guard
  """
  guard = GuardModel.get_one_guard(g.guard.get('id'))
  ser_guard = guard_schema.dump(guard).data
  return custom_response(ser_guard, 200)

@guard_api.route('/', methods=['GET'])
@Auth.auth_required
def get_all():
  guards = GuardModel.get_all_guards()
  ser_guards = guard_schema.dump(guards, many=True).data
  return custom_response(ser_guards, 200)


@guard_api.route('/login', methods=['POST'])
def login():
  req_data = request.get_json()
  data, error = guard_schema.load(req_data, partial=True)

  if error:
    return custom_response(error, 400)

  if not data.get('guardId') or not data.get('password'):
    return custom_response({'error': 'you need a guard ID and password to login'}, 400)
  
  guard = GuardModel.get_guard_by_guardId(data.get('guardId'))
  if not guard:
    return custom_response({'error':'invalid credentials'}, 400)

  if not guard.check_hash(data.get('password')):
    return custom_response({'error': 'invalid credentials'}, 400)

  ser_data = guard_schema.dump(guard).data
  token = Auth.generate_token(ser_data.get('id'))

  # generate app log
  app_log = {"user_id": data.get('guardId')}
  app_data, error = AppLogsSchema().load(app_log)

  if error:
    return custom_response(error, 400)

  theAppLog = AppLogsModel(app_data)
  theAppLog.save()
  
  return custom_response({'jwt_token':token, "guard": ser_data}, 200)

@guard_api.route("/logout", methods=['POST'])
@Auth.auth_required
def logout():
  req_data = request.get_json()
  data, error = AppLogsSchema().load(req_data)
  if error:
    return custom_response(error, 400)

  app_log = AppLogsModel.get_app_log_by_user_id(data.get('user_id'))
  if not app_log:
    message = {'error':'This guard has never logged in'}
    return custom_response(message, 400)
  if app_log.logout_time != None:
    message = {'error':'Logging out without first logging in'}
    return custom_response(message, 400)
  app_log.update(data)
  ser_data = AppLogsSchema().dump(app_log).data
  return custom_response(ser_data, 200)
  

def custom_response(res, status_code):
  """
  Custom Response Function
  """
  return Response(
    mimetype="application/json",
    response=json.dumps(res),
    status=status_code
  )

