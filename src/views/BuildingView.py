from flask import request, g, Blueprint, json, Response
from ..shared.Authentication import Auth
from ..models.BuildingModel import BuildingModel, BuildingSchema

building_api = Blueprint('building_api', __name__)
building_schema = BuildingSchema()

@building_api.route('/', methods=['POST'])
def create():
  """
  Create Building Function
  """
  req_data = request.get_json()
  data, error = building_schema.load(req_data)
  if error:
    return custom_response("Error! Check if json object contains all the required attributes", 400)
  
  # check if building already exist in db
  buildings = BuildingModel.get_all_buildings()
  for building in buildings:
    if building.latitude == data.get('latitude') and building.longitude == data.get('longitude'):
      message = {'error': 'Building already exist, please supply different latitude and longitude'}
      return custom_response(message, 400)
  building = BuildingModel(data)
  building.save()
  data = building_schema.dump(building).data
  return custom_response(data, 201)

@building_api.route('/<int:building_id>', methods=['GET'])
def get_one(building_id):
  """
  Get a Building
  """
  building = BuildingModel.get_one_building(building_id)
  if not building:
    return custom_response({'error':'building not found'}, 404)
  data = building_schema.dump(building).data
  return custom_response(data, 200)

@building_api.route('/<int:building_id>', methods=['PUT'])
def update(building_id):
  """
  Update a Building
  """
  req_data = request.get_json()
  building = BuildingModel.get_one_building(building_id)
  if not building:
    return custom_response({'error':'building not found'}, 404)
  data, error = building_schema.load(req_data, partial=True)
  if error:
    return custom_response(error, 400)
  building.update(data)
  data = building_schema.dump(building).data
  return custom_response(data, 200)

@building_api.route('/', methods=['GET'])
def get_all():
  """
  Get all Buildings
  """
  buildings = BuildingModel.get_all_buildings()
  data = building_schema.dump(buildings, many=True).data
  return custom_response(data, 200)

@building_api.route('/<int:building_id>', methods=['DELETE'])
def delete(building_id):
  """
  Delete a Building
  """
  building = BuildingModel.get_one_building(building_id)
  if not building:
    return custom_response({'error':'building not found'}, 404)
  building.delete()
  return custom_response({'message':'deleted'}, 204)

def custom_response(res, status_code):
  """
  Custom Response Function
  """
  return Response(
    mimetype="application/json",
    response=json.dumps(res),
    status=status_code
  )