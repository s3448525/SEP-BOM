
class ObservationManager(object):

    def __init__(self, db):
        self.db = db

    def api_get_observations_near(self, params):
        return self.get_observations_near(None, None, None)

    def get_observations_near(self, latitude, longitude, time):
        pass

    def add_observation(self, latitude, longitude, time, value, source):
        pass
