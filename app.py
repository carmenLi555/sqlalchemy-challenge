# 1. import Flask

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

measurement = Base.classes.measurement

station = Base.classes.station

# 2. Create an app, being sure to pass __name__
app = Flask(__name__)


#  Define what to do when a user hits the index route  
# List all routes that are available.
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Welcome to my 'Home' page!<br/>"
       
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/datesearch/startDate/endDate"
    )


#Convert the query results to a dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
     # Create our session (link) from Python to the DB
     session = Session(engine)

     #Convert the query results to a dictionary
     results = session.query(measurement.date, measurement.prcp).order_by(measurement.date)
     session.close()

     all_prcp =[]
     for each_row in results:
         prcp_dict = {}
         prcp_dict["date"] = each_row.date
         prcp_dict["precipitation"] = each_row.prcp
         all_prcp.append(prcp_dict)
     return jsonify(all_prcp)


#Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
     # Create our session (link) from Python to the DB  
     session = Session(engine)
     sta_results = session.query(station.name).all()
     session.close()
     
     all_names = list(np.ravel(sta_results))

     return jsonify(all_names)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    temp_station = session.query(measurement.date,measurement.station,measurement.tobs).filter(measurement.date >= '2016-08-23').filter(measurement.station == 'USC00519281').all()
    session.close()

    temp_tobs =[]
    for each_row in temp_station:
         tob_dict = {}
         tob_dict["date"] = each_row.date
         tob_dict["station"] = each_row.station
         tob_dict["precipitation"] = each_row.tobs 
         temp_tobs.append(tob_dict)
    return jsonify(temp_tobs)

#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.

@app.route("/api/v1.0/start") 
def start():
    session = Session(engine)

    sel = [measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]

    results = (session.query(*sel).filter(func.strftime("%Y-%m-%d", measurement.date) >= '2017-02-28').group_by(measurement.date).all())

    dates=[]
    for result in results:
        date_dict = {}
        date_dict["date"] = result[0]
        date_dict["minimum temp"] = result[1]
        date_dict["average temp"] = result[2]
        date_dict["maximum temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)


@app.route('/api/v1.0/datesearch/<startDate>/<endDate>')
def startEnd(startDate, endDate):
    session = Session(engine)
    sel = [measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]

    results =  (session.query(*sel).filter(func.strftime("%Y-%m-%d", measurement.date) >= startDate).filter(func.strftime("%Y-%m-%d", measurement.date) <= endDate).group_by(measurement.date).all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)



# Query the dates and temperature observations of the most active station for the last year of data.
#Return a JSON list of temperature observations (TOBS) for the previous year.
if __name__ == "__main__":
    app.run(debug=True)
