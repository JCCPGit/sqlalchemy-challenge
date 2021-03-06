# Dependencies
import datetime as dt
import numpy as np
import pandas as pd

# SQLAlchemy
import sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

# Flask
from flask import Flask, jsonify

# Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session from python to the database
session = Session(engine)

# Flask setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start</br>"
        f"/api/v1.0/start-end</br>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_ago).all()
    
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    
    results = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()
    
    all_stations = []
    for station, name, latitude, longitude, elevation in results:
        all_stations_dict = {}
        all_stations_dict["Stations"] = station
        all_stations_dict["Name"] = name
        all_stations_dict["Latitude"] = latitude
        all_stations_dict["Longitude"] = longitude
        all_stations_dict["Elevation"] = elevation
        all_stations.append(all_stations_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def temp_monthly():
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    most_active_station = 'USC00519281'
    
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= year_ago).all()
    
    rows = [{"Date":r[0], "Temperature":r[1]} for r in results]
    
    return jsonify(rows)

@app.route("/api/v1.0/temp/start")
@app.route("/api/v1.0/start-end")
def stats(start=None, end=None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)
    
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

if __name__ == '__main__':
    app.run()