'''
A script to fetch forecasts and load them into the database.

Usage:
python -m model.load_forecast
'''
import model.forecast


if __name__ == '__main__':
    # Connect to the db.
    from feva import db

    # Load the forecasts.
    fc_manager = model.forecast.ForecastManager(db)

    fc_manager.load()

    # example
    print(fc_manager.get_forecasts_near(150.9519958, -45.8919983, max_distance=5000))
