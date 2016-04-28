import datetime
from model.evaluator import  Evaluator


if __name__ == '__main__':
    # Connect to the db.
    from feva import db

    eva = Evaluator(db)
    print(eva.evaluate_lat_lon(144.9643, -37.8099, time=datetime.datetime.utcnow(), max_distance=10000))
