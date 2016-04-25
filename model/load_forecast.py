'''
Fetch forecasts and load them into the database.

Can be used as a script.
Usage:
python -m model.load_forecast db_host db_port db_user db_password
Example:
python -m model.load_forecast 127.0.0.1 5432 myname mypassword
'''
from model.helpers.distance import GISPoint, Distance, Within, AsLatLon, decode_point
import model.fetch_forecast
from model.schema import Forecast
from model.schema import ForecastValue
from psycopg2.extras import DateTimeRange
import datetime


class ForecastLoader(object):

    def __init__(self, db):
        self.db = db

    def load(self):
        '''
        Fetch forecasts and load them into the DB.
        '''
        # Fetch each forecast.
        for raw_fc in model.fetch_forecast.fetch_forecast():
            with self.db.session_scope() as session:
                # Create the forecast description.
                fc = Forecast(
                    name=raw_fc['name'],
                    creation_date=raw_fc['creation_time'],
                    date_range=DateTimeRange(raw_fc['time'], raw_fc['time']+datetime.timedelta(days=1)))  # TODO: set up the date_range

                #TODO ensure the forecast description ID is ready for the ForecastValues to reference.
                # Save the forecast description.
                session.add(fc)
                session.commit()
                # Convert the raw forecast values into objects.
                i = 0
                while i < len(raw_fc['lat_list']):
                    j = 0
                    while j < len(raw_fc['lon_list']):
                        # Create forecast value object.
                        # Note: Values from the lat/lon_list and values arrays
                        # are cast to type float from numpy.float32/64 so that
                        # other modules such as sqlalchemy/psycopg2 know how
                        # handle them.
                        fc_val = ForecastValue(
                            id_forecast=fc.id,
                            location=GISPoint(float(raw_fc['lon_list'][j]), float(raw_fc['lat_list'][i])),
                            value=float(raw_fc['values'][i][j]))
                        # Prepare to save the value.
                        session.add(fc_val)
                        j += 1
                    # Try flushing the values into the DB to reduce ram usage.
                    session.commit()
                    i += 1

    def forecasts_near(self, longitude, latitude, forecast_date=None, distance=1000, limit=5):
        """
        :param longitude:
        :param latitude:
        :param distance: The distance (in meters) of the bounds
        :param limit: How many records to return (sorted by distance)
        :return: A list of locations (as a dict) near a given coordinate.
        """
        if forecast_date is None:
            forecast_date = datetime.datetime.utcnow()

        point = GISPoint(longitude, latitude)
        forecasts = []
        with self.db.session_scope() as session:
            results = session.query(AsLatLon(ForecastValue.location), Forecast.name)\
                .filter(Within(ForecastValue.location, point, distance),
                        Forecast.date_range.contains(forecast_date))\
                .order_by(Distance(ForecastValue.location, point)).limit(limit)\
                .all()

            for result in results:
                longitude, latitude = decode_point(str(result[0]))
                forecasts.append(dict(Name=result[1], Latitude=latitude, Longitude=longitude))

        return forecasts

if __name__ == '__main__':
    # Connect to the db.
    from feva import db

    # Load the forecasts.
    fc_loader = ForecastLoader(db)

    fc_loader.load()

    # example
    print(fc_loader.forecasts_near(150.9519958, -45.8919983))
