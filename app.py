import os
import psycopg2
from dotenv import load_dotenv #reading the .env
from flask import Flask,request
from datetime import datetime,timezone

#create SQL DB
CREATE_ROOMS_TABLE = (
    "CREATE TABLE IF NOT EXISTS rooms (id SERIAL PRIMARY KEY, name TEXT);"
)
CREATE_TEMPS_TABLE = """CREATE TABLE IF NOT EXISTS temperatures (room_id INTEGER, temperature REAL, 
                        date TIMESTAMP, FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE);"""

INSERT_ROOM_RETURN_ID = "INSERT INTO rooms (name) VALUES (%s) RETURNING id;"
INSERT_TEMP = (
    "INSERT INTO temperatures (room_id, temperature, date) VALUES (%s, %s, %s);"
)

GLOBAL_NUMBERS_OF_DAYS = ("""SELECT COUNT(DISTINCT DATE(date)) AS DAYS FROM temperatures;""")
GLOBAL_AVG = """SELECT AVG(temperature) as averages FROM temperatures;"""

load_dotenv()
app = Flask(__name__)
url=os.getenv("DATABASE_URL") #get url from .env
connetion= psycopg2.connect(url) #to connect DBs to read or control DBs

@app.route("/api/room",methods=["POST"]) #post is a HTTP method to send us data
def create_room():
    data = request.get_json()
    name = data["name"]
    with connetion:
        with connetion.cursor() as cursor: 
            #corsor is a object that allows us to insert data into the DB or iterate over rows if we query
            cursor.execute(CREATE_ROOMS_TABLE)
            cursor.execute(INSERT_ROOM_RETURN_ID,(name,)) #there's a %s so we are sending a tuple value
            room_id= cursor.fetchone()[0]# only fetch one and return
        
    return{"id":room_id,"message":f"Room{name} created."},201

@app.route("/api/temp",methods=["POST"])
def add_temp():
    data = request.get_json()
    temperature = data["temperature"]
    room_id = data["room"]
    try:
        date = datetime.strptime(data["date"],"%m-%d-%Y %H:%M:%S")
    except KeyError:
        date = datetime.now(timezone.utc)

    with connetion:
        with connetion.cursor() as cursor:
            cursor.execute(CREATE_TEMPS_TABLE)
            cursor.execute(INSERT_TEMP,(room_id,temperature,date,))
    return{"message":"Temperature added"},201


@app.route("/api/average",methods=["GET"])
def get_avg():
    with connetion:
        with connetion.cursor() as cursor:
            cursor.execute(GLOBAL_AVG)
            average = cursor.fetchone()[0]
            cursor.execute(GLOBAL_NUMBERS_OF_DAYS)
            days = cursor.fetchone()[0]
    return{"average":round(average,2),"days":days}
# if __name__ == "__main__":
    # app.run(debug=True)