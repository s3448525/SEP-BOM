'''
A script that runs the evaluator for the specified location.

Usage:
    python3 -m model.evaluate latitude longitude
    e.g. python3 -m model.evaluate -37.8099 144.9643
'''
import datetime
from model.evaluator import  Evaluator
import logging
import sys
import argparse


if __name__ == '__main__':
    # Connect to the db.
    from feva import db

    # Send debug logging to stderr.
    log_handler = logging.StreamHandler(sys.stderr)
    log_handler.setLevel(logging.DEBUG)
    log_fmt = logging.Formatter(
	'%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_handler.setFormatter(log_fmt)
    logging.getLogger().setLevel(logging.DEBUG)
    logging.getLogger().addHandler(log_handler)

    # Parse CLI parameters.
    parser = argparse.ArgumentParser()
    parser.add_argument('lat', type=float)
    parser.add_argument('lon', type=float)
    args = parser.parse_args()
    print('Location: {}, {}'.format(args.lat, args.lon))

    # Evaluate and print result.
    eva = Evaluator(db)
    print(eva.evaluate_lat_lon(
        args.lon,
        args.lat,
        time=datetime.datetime.utcnow(),
        max_distance=10000))
