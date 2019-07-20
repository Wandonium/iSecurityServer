from flask import Flask
from .config import app_config
from .models import db, bcrypt
# import guard_api blueprint
from .views.GuardView import guard_api as guard_blueprint
# import building_api blueprint
from .views.BuildingView import building_api as building_blueprint
# import company_api blueprint
from .views.CompanyView import company_api as company_blueprint
# import employee_api blueprint
from .views.EmployeeView import employee_api as employee_blueprint
# import guest_api blueprint
from .views.GuestView import guest_api as guest_blueprint
# import img_proc_api blueprint
from .img_proc.script import img_proc_api as img_proc_blueprint
# import app_log_api blueprint
from .views.AppLogsView import app_log_api as app_log_blueprint


def create_app(env_name):
  """
  Create app
  """

  # app initialization
  app = Flask(__name__)

  app.config.from_object(app_config[env_name])

  # initializing bcrypt
  bcrypt.init_app(app)

  # initializing db
  db.init_app(app)

  app.register_blueprint(guard_blueprint, url_prefix='/api/v1/guards')
  app.register_blueprint(building_blueprint, url_prefix='/api/v1/buildings')
  app.register_blueprint(company_blueprint, url_prefix='/api/v1/companies')
  app.register_blueprint(employee_blueprint, url_prefix='/api/v1/employees')
  app.register_blueprint(guest_blueprint, url_prefix='/api/v1/guests')
  app.register_blueprint(img_proc_blueprint, url_prefix='/api/v1/img_proc')
  app.register_blueprint(app_log_blueprint, url_prefix='/api/v1/app_logs')

  @app.route('/', methods=['GET'])
  def index():
    """
    example endpoint
    """
    return 'Congratulations! Your first endpoint is workin'

  return app