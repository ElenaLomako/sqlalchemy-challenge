# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
        f"To access values between a start and end date enter both dates using format: YYYY-mm-dd/YYYY-mm-dd"
    )

# Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Define variable
    last_data_point = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_ago_data_point = dt.date(2017,8,23) - dt.timedelta(days= 365)

    # Query
    year_prcp = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago_data_point, Measurement.prcp != None).order_by(Measurement.date).all()
    return jsonify(dict(year_prcp))

# Station route
@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    #Return a JSON list of stations from the dataset.
    return jsonify(dict(stations))

# Tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    last_data_point = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
  
   # Find the date that was a year ago
    year_ago_data_point = dt.date(2017,8,23) - dt.timedelta(days= 365)
   

    # Create query
    active_station = session.query(Measurement.station, func.count(Measurement.station)).\
        order_by(func.count(Measurement.station).desc()).\
        group_by(Measurement.station).first()
    most_active_station = active_station[0] 
    print(most_active_station)
    

    dates_tobs_last_year_query_results = session.query(Measurement.date, Measurement.tobs, Measurement.station).\
        filter(Measurement.date >= year_ago_data_point).\
        filter(Measurement.station == most_active_station) 
    

    # Create a list of dates,tobs,and stations that will be appended with dictionary values for date, tobs, and station number queried above
    dates_tobs_last_year_query = []
    for date, tobs, station in dates_tobs_last_year_query_results:
        dates_tobs_dict = {}
        dates_tobs_dict["date"] = date
        dates_tobs_dict["tobs"] = tobs
        dates_tobs_last_year_query.append(dates_tobs_dict)
        
    return jsonify(dates_tobs_last_year_query) 

  

# Start route
@app.route("/api/v1.0/<start>")
def start_date(start):
    # Create query for minimum, average, and max tobs
    start_date_tobs_results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    start_date_tobs =[]
    for min, avg, max in start_date_tobs_results:
        start_date_tobs_dict = {}
        start_date_tobs_dict["min"] = min
        start_date_tobs_dict["average"] = avg
        start_date_tobs_dict["max"] = max
        start_date_tobs.append(start_date_tobs_dict)
    
    return jsonify(start_date_tobs)

# Start/End route
@app.route("/api/v1.0/<start>/<end>")
def Start_end_date(start, end):
    # Create query for minimum, average, and max tobs 
    start_end_date_tobs_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
 
    start_end_tobs_date =[]
    for min, avg, max in start_end_date_tobs_results:
        start_end_tobs_date_dict = {}
        start_end_tobs_date_dict["min_temp"] = min
        start_end_tobs_date_dict["avg_temp"] = avg
        start_end_tobs_date_dict["max_temp"] = max
        start_end_tobs_date.append(start_end_tobs_date_dict) 
    

    return jsonify(start_end_tobs_date)
    

if __name__ == '__main__':
    app.run(debug=True)

session.close()