# Import the dependencies.
from flask import Flask, jsonify
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base


#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# reflect the tables
Measurement = Base.classes.measurement
Station = Base.classes.station


# Create our session (link) from Python to the DB
session = Session(engine)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


@app.route("/")
def home():
    """Homepage and list of available routes."""
    return (
        f"Welcome to the Climate App!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date  (e.g., /api/v1.0/2016-08-23) <br/>"
        f"/api/v1.0/start_date/end_date (e.g., /api/v1.0/2016-08-23/2017-08-23) <br/>"
    )


#################################################
# Flask Routes
#################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the last 12 months of precipitation data as JSON."""
    # Calculate the date one year from the last date in the data set
    lastdate = session.query(func.max(Measurement.date)).scalar()
    years = dt.datetime.strptime(lastdate, '%Y-%m-%d')
    one_year_ago = years - dt.timedelta(days=365)

    # Query to retrieve precipitation data for the last 12 months
    pre_score = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a dictionary
    precipitation_dict = {date: prcp for date, prcp in pre_score}

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    # Query to retrieve all stations
    stations = session.query(Station.station).all()

    # Convert the query results to a list
    station_list = [station[0] for station in stations]

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return temperature observations for the previous year of the most-active station."""
    # Get the most active station ID
    most_active_station = session.query(Measurement.station)\
        .group_by(Measurement.station)\
        .order_by(func.count(Measurement.station).desc())\
        .first()[0]

    # Calculate the date one year from the last date in the data set
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    # Query to retrieve temperature observations for the last 12 months for the most active station
    temperature_data = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.station == most_active_station)\
        .filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a list of dictionaries
    temperature_list = [{"date": date, "tobs": tobs} for date, tobs in temperature_data]

    return jsonify(temperature_list)

@app.route("/api/v1.0/<start>")
def temperature_start(start):
    """Return MIN, AVG, and MAX for all dates greater than or equal to the start date."""
    # Query to calculate MIN, AVG, and MAX for dates greater than or equal to the start date
    temperature_stats = session.query(func.min(Measurement.tobs).label('min_temp'),
                                     func.avg(Measurement.tobs).label('avg_temp'),
                                     func.max(Measurement.tobs).label('max_temp'))\
        .filter(Measurement.date >= start).all()

    # Convert the query results to a list of dictionaries
    temperature_stats_list = [{"Min Temperature": stat.min_temp,
                               "Avg Temperature": stat.avg_temp,
                               "Max Temperature": stat.max_temp} for stat in temperature_stats]

    return jsonify(temperature_stats_list)

@app.route("/api/v1.0/<start>/<end>")
def temperature_range(start, end):
    """Return MIN, AVG, and MAX for the specified start and end date range."""
    # Query to calculate MIN, AVG, and MAX for the specified date range
    temperature_stats = session.query(func.min(Measurement.tobs).label('min_temp'),
                                     func.avg(Measurement.tobs).label('avg_temp'),
                                     func.max(Measurement.tobs).label('max_temp'))\
        .filter(Measurement.date >= start)\
        .filter(Measurement.date <= end).all()

    # Convert the query results to a list of dictionaries
    temperature_stats_list = [{"Min Temperature": stat.min_temp,
                               "Avg Temperature": stat.avg_temp,
                               "Max Temperature": stat.max_temp} for stat in temperature_stats]

    return jsonify(temperature_stats_list)

if __name__ == "__main__":
    app.run(debug=True)