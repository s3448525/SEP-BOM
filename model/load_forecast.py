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
        for raw_fc in fetch_forecast():
            # Create the forecast description.
            fc = Forecast(
                name=raw_fc['name'],
                creation_date=raw_fc['created_time'],
                forecast_date=raw_fc['forecast_time'])
            #TODO ensure the forecast description ID is ready for the ForecastValues to reference.
            # Save the forecast description.
            with self.db.session_scope() as session:
                session.add(Forecast)
            with self.db.session_scope() as session:
                session.commit()
            # Convert the raw forecast values into objects.
            i, j = 0
            while i < len(raw_fc['lat_list']):
                j = 0
                while j < len(raw_fc['lon_list']):
                    # Create forecast value object.
                    fc_val = ForecastValue(
                        id_forecast=fc.id,
                        location=GISPoint(raw_fc['lon_list'][j], raw_fc['lat_list'][i]),
                        value=raw_fc['values'][i][j])
                    # Prepare to save the value.
                    with self.db.session_scope() as session:
                        session.add(ForecastValue)
                    j++
                # Save pending values.
                with self.db.session_scope() as session:
                    session.commit()
                i++

if __name__ == '__main__':
    fc_loader = ForecastLoader(TODO_get_DB) #TODO
    fc_loader.load()
