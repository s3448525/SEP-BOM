'''
A script to fetch forecasts and load them into the database.

Usage:
python -m model.load_forecast [debug]
'''
import model.forecast
import logging
import sys


if __name__ == '__main__':
    # Connect to the db.
    from feva import db

    # Optionally output debug messages.
    if 'debug' in sys.argv:
        log_handler = logging.StreamHandler(sys.stderr)
        log_handler.setLevel(logging.DEBUG)
        log_fmt = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        log_handler.setFormatter(log_fmt)
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger().addHandler(log_handler)

    # Load the forecasts.
    fc_manager = model.forecast.ForecastManager(db)
    fc_manager.load()
