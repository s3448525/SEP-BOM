from model.helpers.distance import GISPoint
import model.fetch_forecast
from model.schema import Forecast
from model.schema import ForecastValue


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
                    forecast_date=raw_fc['time'])
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
                    i += 1

if __name__ == '__main__':
    '''
    Fetch forecasts and load them into the database.

    Usage:
    python -m model.load_forecast db_host db_port db_user db_password

    Example:
    python -m model.load_forecast 127.0.0.1 5432 myname mypassword
    '''
    import sys
    from model.orm import ORM
    # Print usage if needed.
    if len(sys.argv) != 5:
        sys.exit('Usage: python -m model.load_forecast host port username password')
    # Connect to the db.
    db = ORM(sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4])
    # Load the forecasts.
    fc_loader = ForecastLoader(db)
    fc_loader.load()
