from flask import request, json, Response, Blueprint, g
from ..models.AppLogs import AppLogsSchema, AppLogsModel
from ..shared.Authentication import Auth

app_log_api = Blueprint('app_logs', __name__)
app_log_schema = AppLogsSchema()

@app_log_api.route("/", methods=['GET'])
def get_all():
  app_logs = AppLogsModel.get_all_app_logs()
  ser_data = app_log_schema.dump(app_logs, many=True).data
  return custom_response(ser_data, 200)

@app_log_api.route("/<int:app_log_id>", methods=['DELETE'])
def delete(app_log_id):
  app_log = AppLogsModel.get_one_app_log(app_log_id)
  app_log.delete()
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