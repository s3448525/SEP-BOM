'''
A script to delete old forecasts from the database.
By default old forecastss are those made more than 8 days ago.

Usage:
python -m model.delete_old_forecast [date-time] [debug]
'''
import model.forecast
import logging
import sys
import datetime


if __name__ == '__main__':
    # Connect to the db.
    from feva import db

    # Set the default time threshold.
    threshold_time = datetime.datetime.utcnow() - datetime.timedelta(days=8)

    # Optionally output debug messages.
    if 'debug' in sys.argv:
        log_handler = logging.StreamHandler(sys.stderr)
        log_handler.setLevel(logging.DEBUG)
        log_fmt = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        log_handler.setFormatter(log_fmt)
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger().addHandler(log_handler)

    # If a datetime CLI parameter is given use it to define the threshold time.
    # TODO

    # Delete old forecastss.
    fc_manager = model.forecast.ForecastManager(db)
    fc_manager.delete_old(threshold_time)
