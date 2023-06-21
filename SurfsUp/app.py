 # Import the dependencies.
from flask import Flask, jsonify

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
#################################################
# Database Setup
#################################################
# reflect an existing database into a new model
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# reflect the tables
Measurement = Base.classes.Measurement
Station = Base.classes.station
session = Session(engine)

#################################################
# Flask Setup
#################################################
# Create a Flask app instance
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# Define the home page route and list of available routes:
@app.route("/")
def home():
    return (
        f"Welcome to the Climate App!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

# Define the /api/v1.0/precipitation route to return the last 12 months of precipitation data as a dictionary:
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date 1 year ago from the last date in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    one_year_ago = last_date - dt.timedelta(days=365)

    # Query the last 12 months of precipitation data
    prcp_results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a dictionary using date as the key and prcp as the value.
    prcp_dict = {}
    for result in prcp_results:
        prcp_dict[result[0]] = result[1]

    # Return the JSON representation of your dictionary.
    return jsonify(prcp_dict)

# Define the /api/v1.0/stations route to return a list of stations:
@app.route("/api/v1.0/stations")
def stations():
    # Query the stations
    station_results = session.query(Station.station, Station.name).all()

    # Convert the query results to a list of dictionaries
    station_list = []
    for result in station_results:
        station_dict = {}
        station_dict["station"] = result[0]
        station_dict["name"] = result[1]
        station_list.append(station_dict)

    # Return the JSON representation of your list.
    return jsonify(station_list)

# Define the /api/v1.0/tobs route to return temperature observations for the most active station for the last 12 months:
@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date 1 year ago from the last date in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    one_year_ago = last_date - dt.timedelta(days=365)

    # Query the temperature observations of the most-active station for the previous year of data.
    station_query = session.query(Measurement.station, func.count(Measurement.station)).\
        group


# Define the /api/v1.0/<start> and /api/v1.0/<start>/<end> routes to return temperature statistics for a specified start date or date range:
@app.route("/api/v1.0/<start>")
def temp_stats_start(start):
    # Convert the start date to datetime object
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')

    # Query the temperature statistics
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    # Convert the query results to a list of dictionaries
    temp_list = []
    for result in results:
        temp_dict = {}
        temp_dict["TMIN"] = result[0]
        temp_dict["TAVG"] = result[1]
        temp_dict["TMAX"] = result[2]
        temp_list.append(temp_dict)

    # Return the JSON representation of your list.
    return jsonify(temp_list)


@app.route("/api/v1.0/<start>/<end>")
def temp_stats_start_end(start, end):
    # Convert the start and end dates to datetime objects
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')

    # Query the temperature statistics
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    # Convert the query results to a list of dictionaries
    temp_list = []
    for result in results:
        temp_dict = {}
        temp_dict["TMIN"] = result[0]
        temp_dict["TAVG"] = result[1]
        temp_dict["TMAX"] = result[2]
        temp_list.append(temp_dict)

    # Return the JSON representation of your list.
    return jsonify(temp_list)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)