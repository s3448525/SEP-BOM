from model.helpers.distance import GISPoint, Distance, Within, AsLatLon, decode_point
import model.fetch_forecast
from model.schema import Forecast
from model.schema import ForecastValue
from psycopg2.extras import DateTimeRange
import datetime
from math import isnan
import logging


class ForecastManager(object):

    def __init__(self, db):
        self.db = db

    def load(self):
        '''
        Fetch forecasts and load them into the DB.
        '''
        # Fetch each forecast.
        for raw_fc in model.fetch_forecast.fetch_forecast():
            with self.db.transaction_session() as session:
                # Create the forecast description.
                fc = Forecast(
                    name=raw_fc['name'],
                    creation_date=raw_fc['creation_time'],
                    date_range=DateTimeRange(raw_fc['start_time'], raw_fc['end_time']))
                #TODO ensure the forecast description ID is ready for the ForecastValues to reference.
                # Save the forecast description.
                session.add(fc)
                session.commit()
                # Convert the raw forecast values into objects.
                i = 0
                while i < len(raw_fc['lat_list']):
                    j = 0
                    while j < len(raw_fc['lon_list']):
                        # Skip NaN values.
                        # TODO make detecting Nan/numpy-masked-values faster.
                        if not isnan(raw_fc['values'][i][j]):
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

    def get_forecasts_near(self, longitude, latitude, forecast_date=None, max_distance=1000, limit=5):
        """
        :param longitude:
        :param latitude:
        :param max_distance: The max_distance (in meters) of the bounds
        :param limit: How many records to return (sorted by max_distance)
        :return: A list of locations (as a dict) near a given coordinate.
        """
        if forecast_date is None:
            forecast_date = datetime.datetime.utcnow()

        point = GISPoint(longitude, latitude)
        results = self.db.session.query(ForecastValue, Forecast)\
            .filter(Within(ForecastValue.location, point, max_distance),
                    Forecast.date_range.contains(forecast_date))\
            .filter(ForecastValue.id_forecast == Forecast.id)\
            .order_by(Distance(ForecastValue.location, point))\
            .limit(limit)\
            .all()
        forecasts = []
        for result in results:
            forecasts.append((result[0], result[1]))
        return forecasts

    def delete_old(self, time):
        '''
        Delete forecasts older than the specified datetime.
        Returns the number of deleted forecasts.
        '''
        log = logging.getLogger(__name__)
        deleted_count = 0
        with self.db.transaction_session() as session:
            # Get a list of forecasts older than the threshold time.
            old_forecasts = session.query(Forecast)\
                .filter(Forecast.creation_date < time)\
                .all()
            # Delete each forecast.
            for fc in old_forecasts:
                # Delete the forecasts values.
                session.query(ForecastValue)\
                    .filter(ForecastValue.id_forecast == fc.id)\
                    .delete()
                # Delete the forecast.
                session.delete(fc)
                session.commit()
                deleted_count += 1
        log.debug('Deleted {} forecasts older than {}.'.format(str(deleted_count), str(time)))
