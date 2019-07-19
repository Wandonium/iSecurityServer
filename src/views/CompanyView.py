from flask import request, json, Response, Blueprint, g
from ..models.CompanyModel import CompanyModel, CompanySchema
from ..shared.Authentication import Auth

company_api = Blueprint('companies', __name__)
company_schema = CompanySchema()

@company_api.route('/', methods=['POST'])
@Auth.auth_required
def create():
  """
  Create Company Function
  """
  req_data = request.get_json()
  data, error = company_schema.load(req_data)

  if error:
    return custom_response(error, 400)
  
  # check if company already exist in the db
  company_in_db = CompanyModel.get_company_by_email(data.get('email'))
  if company_in_db:
    message = {'error': 'Company already exist, please supply another company email'}
    return custom_response(message, 400)
  
  company = CompanyModel(data)
  company.save()

  ser_data = company_schema.dump(company).data
  return custom_response(ser_data, 201)

@company_api.route('/<int:company_id>', methods=['GET'])
@Auth.auth_required
def get_a_company(company_id):
  """
  Get a single company
  """
  company = CompanyModel.get_one_company(company_id)
  if not company:
    return custom_response({'error':'company not found'}, 404)
  ser_company = company_schema.dump(company).data
  return custom_response(ser_company, 200)

@company_api.route('/<int:company_id>', methods=['PUT'])
@Auth.auth_required
def update(company_id):
  """
  Update this
  """
  req_data = request.get_json()
  data, error = company_schema.load(req_data, partial=True)
  if error:
    return custom_response(error, 400)

  company = CompanyModel.get_one_company(company_id)
  company.update(data)
  ser_company = company_schema.dump(company).data
  return custom_response(ser_company, 200)

@company_api.route('/<int:company_id>', methods=['DELETE'])
@Auth.auth_required
def delete(company_id):
  """
  Delete a company
  """
  company = CompanyModel.get_one_company(company_id)
  company.delete()
  return custom_response({'message': 'deleted'}, 204)

@company_api.route('/', methods=['GET'])
@Auth.auth_required
def get_all():
  companies = CompanyModel.get_all_companies()
  ser_companies= company_schema.dump(companies, many=True).data
  return custom_response(ser_companies, 200)
  

def custom_response(res, status_code):
  """
  Custom Response Function
  """
  return Response(
    mimetype="application/json",
    response=json.dumps(res),
    status=status_code
  )

