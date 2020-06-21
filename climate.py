import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from datetime import datetime

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################


app = Flask(__name__)

hello_dict = {"Hello": "World!"}


@app.route("/")
def home():
    return (
		f"Hello! Do you have any plans to travel to Hawaii? <br/>"
		f"<br/>"
        f"Available Routes:<br/>"
		f"<br/>"
		f"Precipitation data of Hawaii:<br/>"
        f"/api/v1.0/precipitation<br/>"
		f"<br/>"
		f"Station dataset of Hawaii:<br/>"
        f"/api/v1.0/stations<br/>"
		f"<br/>"
		f" Dates and temperature observations of the most active station for the last year of data:<br/>"
        f"/api/v1.0/tobs<br/>"
		f"<br/>"
		f"Minimum temperature, the average temperature, and the max temperature for all dates greater than and equal to the start date.<br/>"
		f"Please enter the date (YYYY-MM-DD) you want instead of the start_date:<br/>"
		f"/api/v1.0/start_date<br/>"
		f"<br/>"
		f"Minimum temperature, the average temperature, and the max temperature for all dates between start date and end date inclusive.<br/>"
		f"Please enter the date (YYYY-MM-DD) you want  instead of the start_date and end_date:<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
		
    )

@app.route("/api/v1.0/precipitation")
def precipitations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    
    # Query all date and precipitations
    results = session.query(Measurement.date,Measurement.prcp).all()

    session.close()

    # Convert list of tuples into normal list
    all_prcp = list(np.ravel(results))

    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all passengers
    station_results = session.query(Measurement.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(station_results))

    return jsonify(all_stations)
    
@app.route("/api/v1.0/tobs")   
def tobs():
	session = Session(engine)
	# Design a query to retrieve the last 12 months of precipitation data and plot the results
	last_data_point = session.query(Measurement.date).order_by((Measurement.date).desc()).first()
	last_data_date = datetime.strptime(last_data_point[0], '%Y-%m-%d')

	# Calculate the date 1 year ago from the last data point in the database
	a_year_ago = last_data_date - dt.timedelta(days=365)
	
	most_active_station = session.query(Measurement.station,func.count(Measurement.tobs)).group_by (Measurement.station).order_by (func.count(Measurement.tobs).desc()).first()
	year_tobs = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date >= a_year_ago).filter(Measurement.station == most_active_station[0]).all()
	
	session.close()
	all_tobs = list(np.ravel(year_tobs))
	return jsonify(all_tobs)
                
@app.route("/api/v1.0/<start>")
def trip_start(start):
	# calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
	session = Session(engine)
	last_data_point = session.query(Measurement.date).order_by((Measurement.date).desc()).first()
	last_data_date = datetime.strptime(last_data_point[0], '%Y-%m-%d')
	start_date= dt.datetime.strptime(start,'%Y-%m-%d')
	trip_1 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
		filter(Measurement.date >= start_date).filter(Measurement.date <= last_data_date).all()
	session.close()
	trip_start_data = list(np.ravel(trip_1))
	return jsonify(trip_start_data)

@app.route("/api/v1.0/<start>/<end>")
def trip_end(start,end):
	#calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive
	session = Session(engine)
	start_date= dt.datetime.strptime(start,'%Y-%m-%d')
	end_date = datetime.strptime(end, '%Y-%m-%d')
	trip_2 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
		filter(Measurement.date >= start).filter(Measurement.date <= end).all()
	session.close()
	trip_end_data = list(np.ravel(trip_2))
	return jsonify(trip_end_data)

if __name__ == "__main__":
    app.run(debug=True)
