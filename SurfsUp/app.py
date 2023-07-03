# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
# reflect an existing database into a new model
engine = create_engine("sqlite:///SurfsUp/Resources/hawaii.sqlite")
#engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(autoload_with=engine)

# reflect the tables
Measurement = Base.classes.measurement
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
    session = Session(engine)

    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    year_ago = last_date - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_ago).\
        order_by(Measurement.date).all()

    session.close()

    precipitation = {date: prcp for date, prcp in results}

    return jsonify(precipitation)

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
    #session = Session(engine)

    #results = session.query(Station.station).all()

    #session.close()

    #stations = list(np.ravel(results))

    #return jsonify(stations)

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
    #session = Session(engine)

    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    year_ago = last_date - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= year_ago).\
        filter(Measurement.station == 'USC00519281').\
        order_by(Measurement.date).all()

    session.close()

    temps = list(np.ravel(results))

    return jsonify(temps)


# Define the /api/v1.0/<start> and /api/v1.0/<start>/<end> routes to return temperature statistics for a specified start date or date range:
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start=None, end=None):
    #session = Session(engine)

    if end:
        # If an end date is provided, calculate the temperature statistics for the specified date range
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
        session.close()

        # Convert the results to a list of dictionaries
        stats = []
        for min_temp, avg_temp, max_temp in results:
            stat_dict = {}
            stat_dict["Minimum Temperature"] = min_temp
            stat_dict["Average Temperature"] = avg_temp
            stat_dict["Maximum Temperature"] = max_temp
            stats.append(stat_dict)

    else:
        # If only a start date is provided, calculate the temperature statistics from the start date to the last available date
        last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= last_date).all()
        session.close()

        # Convert the results to a list of dictionaries
        stats = []
        for min_temp, avg_temp, max_temp in results:
            stat_dict = {}
            stat_dict["Minimum Temperature"] = min_temp
            stat_dict["Average Temperature"] = avg_temp
            stat_dict["Maximum Temperature"] = max_temp
            stats.append(stat_dict)

    return jsonify(stats)

if __name__ == '__main__':
    app.run()