from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


# initialize our db
db = SQLAlchemy()

# initialilze bcrypt 
bcrypt = Bcrypt()
