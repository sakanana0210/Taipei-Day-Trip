from flask import *
from app import mysqlConfig,jwt
dbconfig = mysqlConfig.dbconfig
conn_pool = mysqlConfig.conn_pool
create_jwt = jwt.create_jwt
verify_jwt = jwt.verify_jwt
attractions_bp = Blueprint("attractions", __name__)


@attractions_bp.route("/attractions", methods=["GET"])
def attractions():
	try:
		message = "查詢錯誤，請重新查詢"
		page = int(request.args.get("page", 0))
		keyword = request.args.get("keyword", "")
		nextpage = page + 1
		start_index = 0
		start_index += page * 12
		cnx = conn_pool.get_connection()
		cursor = cnx.cursor()
		data = []
		if keyword:
			query = "SELECT * FROM attractions WHERE mrt = %s OR name LIKE %s LIMIT %s, 12;"
			cursor.execute(query,(keyword, "%" + keyword + "%", start_index))
			results = cursor.fetchall()
			query_next = "SELECT id FROM attractions WHERE mrt = %s OR name LIKE %s LIMIT %s, 1;"
			cursor.execute(query_next,(keyword, "%" + keyword + "%", start_index + 12))
			ifNext = cursor.fetchall()
			if not results:
				message = "超出查詢範圍，請重新查詢"
				raise Exception
			elif not ifNext:
				nextpage = None
		else:
			query = "SELECT * from attractions LIMIT %s, 12;"
			cursor.execute(query, (start_index,))
			results = cursor.fetchall()
			query_next = "SELECT id FROM attractions LIMIT  %s, 1;"
			cursor.execute(query_next, (start_index + 12,))
			ifNext = cursor.fetchall()
			if not results:
				message = "超出查詢範圍，請重新查詢"
				raise Exception
			elif not ifNext:
				nextpage = None

		for result in results:
			entry = {
				"id": result[0],
				"name": result[1],
				"category": result[2],
				"description": result[3],
				"address": result[4],
				"transport": result[5],
				"mrt": result[6],
				"lat": result[7],
				"lng": result[8],
				"images": json.loads(result[9])
			}
			data.append(entry)
		
		new_data = {"nextPage" : nextpage, "data" : data}
		json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
		response = Response(json_data, status=200, content_type="application/json; charset=utf-8")
		return response
	except Exception:
		new_data = {"error": True, "message": message}
		json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
		response = Response(json_data, status=500, content_type="application/json; charset=utf-8")
		return response
	finally:
		if cursor:
			cursor.close()
		if cnx:
			cnx.close()


@attractions_bp.route("/attraction/<int:attractionId>", methods=["GET"])
def attractions_id(attractionId):
	try:
		message = "查詢錯誤，請重新查詢"
		cnx = conn_pool.get_connection()
		cursor = cnx.cursor()
		query = "SELECT * from attractions WHERE id = %s;"
		cursor.execute(query, (attractionId,))
		result = cursor.fetchone()
		if not result:
			message = "景點編號不正確，請重新查詢"
			raise Exception
		data = {
			"id": result[0],
			"name": result[1],
			"category": result[2],
			"description": result[3],
			"address": result[4],
			"transport": result[5],
			"mrt": result[6],
			"lat": result[7],
			"lng": result[8],
			"images": json.loads(result[9])
		}
		new_data = { "data" : data}
		json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
		response = Response(json_data, status=200, content_type="application/json; charset=utf-8")
		return response
	except Exception:
		if(message == "景點編號不正確，請重新查詢"):
			new_data = {"error": True, "message": message}
			json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
			response = Response(json_data, status=400, content_type="application/json; charset=utf-8")
			return response
		else:
			new_data = {"error": True, "message": message}
			json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
			response = Response(json_data, status=500, content_type="application/json; charset=utf-8")
			return response
	finally:
		if cursor:
			cursor.close()
		if cnx:
			cnx.close()


@attractions_bp.route("/mrts", methods=["GET"])
def mrts():
	try:
		message = "查詢錯誤，請重新查詢"
		cnx = conn_pool.get_connection()
		cursor = cnx.cursor()
		query = "SELECT mrt, COUNT(*) as count FROM attractions GROUP BY mrt ORDER BY count DESC LIMIT 40"
		cursor.execute(query)
		results = cursor.fetchall()
		data = []
		if not results:
			raise Exception
		for result in results:
			data.append(result[0])
		new_data = {"data" : data}
		json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
		response = Response(json_data, status=200, content_type="application/json; charset=utf-8")
		return response
	except Exception:
		new_data = {"error": True, "message": message}
		json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
		response = Response(json_data, status=500, content_type="application/json; charset=utf-8")
		return response
	finally:
		if cursor:
			cursor.close()
		if cnx:
			cnx.close()
