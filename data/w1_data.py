import json
import mysql.connector

cnx = mysql.connector.connect(user="root", password="ji3cl31;4", host="127.0.0.1", database="taipei_day_trip")
cursor = cnx.cursor()

try:
    sql_1 = """CREATE TABLE attractions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(255),
    description TEXT,
    address VARCHAR(255) NOT NULL,
    transport TEXT,
    mrt VARCHAR(255),
    lat DOUBLE NOT NULL,
    lng DOUBLE NOT NULL,
    images JSON
    );
    """
    cursor.execute(sql_1)
    src="./data/taipei-attractions.json"
    with open(src, "r", encoding="utf-8") as file:
        data = json.load(file)
        for i in range(len(data["result"]["results"])):
            name = data["result"]["results"][i]["name"]
            category = data["result"]["results"][i]["CAT"]
            description = data["result"]["results"][i]["description"]
            address = data["result"]["results"][i]["address"]
            transport = data["result"]["results"][i]["direction"]
            mrt = data["result"]["results"][i]["MRT"]
            if(mrt == None):
                mrt = ""
            lat = data["result"]["results"][i]["latitude"]
            lng = data["result"]["results"][i]["longitude"]
            images = []
            file = data["result"]["results"][i]["file"]
            files = file.split("https://")
            for i in files:
                i = "https://" + i
                if i.lower().endswith((".jpg", ".png")):
                    images.append(i)
            images_json = json.dumps(images)
            sql_2 = "INSERT INTO attractions (name, category, description, address, transport, mrt, lat, lng, images) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"
            cursor.execute(sql_2, (name, category, description, address, transport, mrt, lat, lng, images_json))
finally:
    cnx.commit()
    cursor.close()
    cnx.close()