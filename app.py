# -----------------------------------------
# importing all dependencies/library/classes
# ------------------------------------------

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.sql import exists  
import numpy as np
import pandas as pd
import datetime as dt

import re
from flask import Flask, jsonify
#---------------------------------
# Setting up database : 
#---------------------------------

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect = True)

Measurement = Base.classes.measurement
Station = Base.classes.station

#****** Flask set up ***********

app = Flask(__name__) 


@app.route("/")
def welcome():
    print("This home/need to list all routes available.")
    return (f" These are available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start (enter as YYYY-MM-DD)<br/>"
        f"/api/v1.0/start/end (enter as YYYY-MM-DD/YYYY-MM-DD)")

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    results = session.query(Measurement.date,func.avg(Measurement.prcp)).\
        filter(Measurement.date >= '2016-08-23').\
        filter(func.strftime("%d", Measurement.date)).\
        group_by(Measurement.date).\
        order_by(Measurement.date).all()

    date_prcp = []
    for row in results:
        dt_dict = {}
        dt_dict[row[0]] = row[1]
        date_prcp.append(dt_dict)
    session.close()
    return jsonify(date_prcp)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations = session.query(Station).all()
    stations_list = []
    for station in stations:
        station_dict = {}
        station_dict["id"] = station.id
        station_dict["station"] = station.station
        station_dict["name"] = station.name
        station_dict["latitude"] = station.latitude
        station_dict["longitude"] = station.longitude
        station_dict["elevation"] = station.elevation
        stations_list.append(station_dict)
    
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    year_temp_obs=(session.query(Measurement.date,(Measurement.tobs))
                  .filter(func.strftime(Measurement.date) >= year_ago)
                  .filter(Measurement.station=='USC00519281')
                  .all())
    temp_obs_l = []
    for row in year_temp_obs:
        tobs_dict = {}
        tobs_dict["date"] = row[0]
        tobs_dict["tobs"] = row[1]
        temp_obs_l.append(tobs_dict)
    session.close()
    return jsonify(temp_obs_l) 

def calc_temps(start_date, end_date):
    session = Session(engine)
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    start = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    final_date_query = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    max_date = final_date_query[0][0]

    temps = calc_temps(start, max_date)

    return_list = []
    return_list.append({'Observation': 'TMIN', 'Temperature': temps[0][1]})
    return_list.append({'Observation': 'TAVG', 'Temperature': temps[0][1]})
    return_list.append({'Observation': 'TMAX', 'Temperature': temps[0][0]})
    session.close()
    return jsonify(return_list) 

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = Session(engine)
    start = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    recent_d = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    return_list = []
    return_list.append({'Observation': 'TMIN', 'Temperature': temps[0][0]})
    return_list.append({'Observation': 'TAVG', 'Temperature': temps[0][1]})
    return_list.append({'Observation': 'TMAX', 'Temperature': temps[0][2]})

    return jsonify(return_list)

if __name__ == "__main__":
    app.run(debug=True)
