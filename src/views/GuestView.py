from flask import request, g, Blueprint, json, Response
import sqlalchemy
from ..shared.Authentication import Auth
from ..models.GuestModel import GuestModel, GuestSchema
from ..models.GuardModel import GuardModel, GuardSchema
from ..models.BuildingModel import BuildingModel, BuildingSchema
from ..models.CompanyModel import CompanyModel, CompanySchema

guest_api = Blueprint('guests', __name__)
guest_schema = GuestSchema()

# used to both create a guest record in the db and sign them in by a guard
@guest_api.route('/', methods=['POST'])
@Auth.auth_required
def create():
  """
  Create Guest Function
  """
  req_data = request.get_json()
  data, error = guest_schema.load(req_data)
  if error:
    return custom_response(error, 400)
  
  # check if guest already exist in db
  guest_in_db = GuestModel.get_guest_by_time_in(data.get('time_in'))
  if guest_in_db:
    message = {'error': 'This guest already exists, please supply a different guest time in!'}
    return custom_response(message, 400)

  # check if guard already exist in db
  guard_in_db = GuardModel.get_guard_by_guardId(data.get('guard_id'))
  # ser_guard = GuardSchema().dump(guard_in_db).data
  # return custom_response(ser_guard, 200)
  if not guard_in_db:
    message = {'error': 'Guard does not exists, please supply a different guard id!'}
    return custom_response(message, 400)

  # check if company already exist in db
  company_in_db = CompanyModel.get_one_company(data.get('company_id'))
  # ser_company = CompanySchema().dump(company_in_db).data
  # return custom_response(ser_company, 200)
  if not company_in_db:
    message = {'error': 'Company does not exists, please supply a different company id!'}
    return custom_response(message, 400)

  if company_in_db.building_id != guard_in_db.building_id:
    message = {'error': 'Company and Guard provided do not belong to the same building.'}
    return custom_response(message, 400)
  
  building_in_db = BuildingModel.get_one_building(company_in_db.building_id)

  # check if all guest sign_ins have a sign_out
  guests = GuestModel.get_guests_by_id(data.get('guestId'))
  for guest in guests:
    if guest.time_out == None:
      message = {'error': 'Trying to sign in guest without first signing out'}
      return custom_response(message, 400)

  guest = GuestModel(data)
  guest.save(guard_in_db, building_in_db, company_in_db)
  data = guest_schema.dump(guest).data
  return custom_response(data, 201)

# returns a guest record given the db id
@guest_api.route('/<int:guest_id>', methods=['GET'])
@Auth.auth_required
def get_one(guest_id):
  """
  Get a Guest
  """
  guest = GuestModel.get_one_guest(guest_id)
  if not guest:
    return custom_response({'error':'guest not found'}, 404)
  data = guest_schema.dump(guest).data
  return custom_response(data, 200)

# used to update a guest record as well as sign out a guest by a guard
@guest_api.route('/<int:guest_id>', methods=['PUT'])
@Auth.auth_required
def update(guest_id):
  """
  Update a Guest
  """
  req_data = request.get_json()
  guest = GuestModel.get_one_guest(guest_id)
  if not guest:
    return custom_response({'error':'Guest not found'}, 404)

  data, error = guest_schema.load(req_data, partial=True)
  if error:
    return custom_response(error, 400)

  localGuestTime = guest.time_in.replace(tzinfo=None)
  localTimeOut = data.get('time_out').replace(tzinfo=None)
  if localGuestTime >= localTimeOut:
    message = {'error': 'time_out is ealier than time_in'}
    return custom_response(message, 400)

  guest.update(data)
  data = guest_schema.dump(guest).data
  return custom_response(data, 200)

# returns all the guest records in the db
@guest_api.route('/', methods=['GET'])
@Auth.auth_required
def get_all():
  """
  Get all Guests
  """
  guests = GuestModel.get_all_guests()
  data = guest_schema.dump(guests, many=True).data
  return custom_response(data, 200)

@guest_api.route('/<int:guest_id>', methods=['DELETE'])
@Auth.auth_required
def delete(guest_id):
  """
  Delete a Guest
  """
  guest = GuestModel.get_one_guest(guest_id)
  if not guest:
    return custom_response({'error':'guest not found'}, 404)
  guest.delete()
  return custom_response({'message':'deleted'}, 204)

# returns all the guests who have not been signed out by a guard
@guest_api.route("/sign_out", methods=['GET'])
@Auth.auth_required
def sign_out():
  guests = GuestModel.get_guests_by_time_out()
  if guests:
    ser_data = guest_schema.dump(guests, many=True).data
    return custom_response(ser_data, 200)
  else:
    message = {'error':'No guests to sign out found. Sign In a guest first.'}
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