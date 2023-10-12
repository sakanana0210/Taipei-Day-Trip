import jwt
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv
load_dotenv()

secret_key = os.getenv("SECRET_KEY")

def create_jwt(user_id, user_name, user_email):
	payload = {"id": user_id,
		"name": user_name,
		"email": user_email,
		"exp": datetime.utcnow() + timedelta(days=7)
		}
	token = jwt.encode(payload, secret_key, algorithm = "HS256")
	return token

def verify_jwt(token):
	try:
		payload = jwt.decode(token, secret_key, algorithms=["HS256"])
		new_data = {
		"data": {
			"id": payload["id"],
			"name": payload["name"],
			"email": payload["email"]
		}
		}
		json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
		return json_data
	except jwt.ExpiredSignatureError:
		new_data = {
		"data": None
		}
		json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
		return json_data
	except jwt.InvalidTokenError:
		new_data = {
		"data": None
		}
		json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
		return json_data