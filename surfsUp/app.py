# 1. Import Flask
import flask
from flask import Flask, jsonify
# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import numpy as np
import pandas as pd
import datetime as dt

# 2. Create an app
app = Flask(__name__)


# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
measurement

station = Base.classes.station
station

session = Session(engine)

app = Flask(__name__)

# 3. Define static routes

# /
    # Homepage.
    # List all available routes.
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/YYYY-MM-DD to see temperature data from given date<br/>"
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD to see temperature data between given dates"
    )

# /api/v1.0/precipitation
# Convert the query results to a dictionary using date as the key and prcp as the value
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    precip = session.query(measurement.date, measurement.prcp)
    session.close()

    #using a dict in this way is problematic - there will be multiple instances of the same date. no clue as to what the instructions require for this problem.
    all_rain = {}
    for date,prcp in precip:
        all_rain[date] = prcp

    return jsonify(all_rain)


# /api/v1.0/stations
    # Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all station names"""
    # Query all stations
    stations = session.query(station.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(stations))

    return jsonify(all_names)

# /api/v1.0/tobs
    # Query the dates and temperature observations of the most active station for the previous year of data.
    # Return a JSON list of temperature observations (TOBS) for the previous year.   
@app.route("/api/v1.0/tobs")
def names():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #find the id and name of the most active station
    activity_df = pd.DataFrame(session.query(measurement.station, measurement.date), columns=['station', 'frequency'])
    activity_df = activity_df.groupby(['station']).count().sort_values('frequency', ascending=False )
    most_active_station = activity_df.index[0]  


    # Find the most recent date in the data set.
    #read dates into a list
    most_recent = session.query(func.max(measurement.date)).first()[0]

    # Calculate the date one year from the last date in data set.
    mos_rec = dt.datetime.strptime(most_recent, '%Y-%m-%d') - dt.timedelta(days=365)
    
    #put the station id and date needed into a query
    temp_data_of_most_active_station_for_the_most_recent_year = session.query(measurement.date, measurement.tobs).filter(measurement.station == most_active_station).filter(measurement.date > mos_rec)
    session.close()


    temp_dict = {}
    for date,tobs in temp_data_of_most_active_station_for_the_most_recent_year:
        temp_dict[date] = tobs

    # Convert list of tuples into normal list
    temp_return = list(np.ravel(temp_dict))

    return jsonify(temp_return)    




# define dynamic route
# /api/v1.0/<start> and /api/v1.0/<start>/<end>
    # Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a given start or start-end range.


    # When given the start and the end date, calculate the TMIN, TAVG, 
    # and TMAX for dates from the start date through the end date (inclusive).
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def betwixt(start, end = None):
    # Create our session (link) from Python to the DB
    session = Session(engine)   

    # if they didn't supply an end date, instantiate it as the most recent date in the dataset.
    if end is None:
        end = session.query(func.max(measurement.date)).first()[0]
    
    # calculate TMIN, TAVG, and TMAX for all dates greater than or equal to the start date .
    temp_query = session.query(measurement.date, measurement.tobs).filter(measurement.date >= start).filter(measurement.date <= end)

    tempDF = pd.DataFrame(temp_query, columns=['date', 'tobs'])
    return f"The temperature between the dates {start} and {end} the can be summarised as follows: minimum {tempDF['tobs'].min()}, maximum {tempDF['tobs'].max()}, and average {tempDF['tobs'].mean()}."
# 4. Define main behavior
if __name__ == "__main__":
    app.run(debug=True)
