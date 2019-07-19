import jwt
import os
import datetime
from flask import json, Response, request, g
from functools import wraps
from ..models.GuardModel import GuardModel

class Auth():
  """
  Auth Class
  """
  
  @staticmethod
  def generate_token(guard_id):
    """
    Generate Token Method
    """
    try:
      payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'iat': datetime.datetime.utcnow(),
        'sub': guard_id
      }
      return jwt.encode(
        payload,
        os.getenv('JWT_SECRET_KEY'),
        'HS256'
      ).decode("utf-8")
    except Exception as e:
      print('Inside exception')
      return Response(
        mimetype="application/json",
        response = json.dumps({'error':'error in generating user token'}),
        status=400
      )

  @staticmethod
  def decode_token(token):
    """
    Decode Token Method
    """

    re = {'data': {}, 'error': {}}
    try:
      payload = jwt.decode(token, os.getenv('JWT_SECRET_KEY'))
      re['data']  = {'guard_id':payload['sub']}
      return re
    except jwt.ExpiredSignatureError as e1:
      re['error'] = {'message':'token expired, please login again'}
      return re
    except jwt.InvalidTokenError:
      re['error'] = {'message':'Invalid token, please try again with a new token'}
      return re

  @staticmethod
  def auth_required(func):
    """
    Auth decorator
    """

    @wraps(func)
    def decorated_auth(*args, **kwargs):
      if 'api-token' not in request.headers:
        return Response(
          mimetype="application/json",
          response=json.dumps({'error':'Authentication token is not available, please login to get one'}),
          status=400
        )
      token = request.headers.get('api-token')
      data = Auth.decode_token(token)
      if data['error']:
        return Response(
          mimetype="application/json",
          response=json.dumps(data['error']),
          status=400
        )
      guard_id = data['data']['guard_id']
      check_user = GuardModel.get_one_guard(guard_id)
      if not check_user:
        return Response(
          mimetype="application/json",
          response=json.dumps({'error': 'user does not exist, invalid token'}),
          status=400
        )
      g.guard = {'id': guard_id}
      return func(*args, **kwargs)
    
    return decorated_auth
      
        
