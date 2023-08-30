from flask import *
import mysql.connector
import mysql.connector.pooling
dbconfig = {
    "user": "root", 
    "password": "ABC123", 
    "host": "127.0.0.1", 
    "database": "taipei_day_trip",
    "charset": "utf8"
}
conn_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name = "mypool",
                            pool_size = 5,
                            **dbconfig)
app=Flask(__name__)
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True

# Pages
@app.route("/")
def index():
	return render_template("index.html")
@app.route("/attraction/<id>")
def attraction(id):
	return render_template("attraction.html")
@app.route("/booking")
def booking():
	return render_template("booking.html")
@app.route("/thankyou")
def thankyou():
	return render_template("thankyou.html")

# Api
@app.route("/api/attractions", methods=["GET"])
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
			query = f"SELECT * FROM attractions WHERE mrt = '{keyword}' OR name LIKE '%{keyword}%' LIMIT {start_index}, 12;"
			cursor.execute(query)
			results = cursor.fetchall()
			query_next = f"SELECT id FROM attractions WHERE mrt = '{keyword}' OR name LIKE '%{keyword}%' LIMIT {start_index + 12}, 1;"
			cursor.execute(query_next)
			ifNext = cursor.fetchall()
			if not results:
				message = "超出查詢範圍，請重新查詢"
				raise Exception
			elif not ifNext:
				nextpage = None
		else:
			query = f"SELECT * from attractions LIMIT {start_index}, 12;"
			cursor.execute(query)
			results = cursor.fetchall()
			query_next = f"SELECT id FROM attractions LIMIT {start_index + 12}, 1;"
			cursor.execute(query_next)
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

@app.route("/api/attraction/<int:attractionId>", methods=["GET"])
def attractions_id(attractionId):
	try:
		message = "查詢錯誤，請重新查詢"
		cnx = conn_pool.get_connection()
		cursor = cnx.cursor()
		query = f"SELECT * from attractions WHERE id = {attractionId};"
		cursor.execute(query)
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

@app.route("/api/mrts", methods=["GET"])
def mrts():
	try:
		message = "查詢錯誤，請重新查詢"
		cnx = conn_pool.get_connection()
		cursor = cnx.cursor()
		query = f"SELECT mrt, COUNT(*) as count FROM attractions GROUP BY mrt ORDER BY count DESC LIMIT 40"
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

app.run(host="0.0.0.0", port=3000)