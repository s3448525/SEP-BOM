#!/usr/bin/env python3

from flask import Flask
import ssl

from controller.data_api import api_data_bp
from controller.ui import ui_bp
from model.orm import ORM

# create a new wsgi application
app = Flask('feva', static_folder='view/static', template_folder='view/templates')

# load configurations
app.config.from_pyfile('config.py')
app.config.from_pyfile('feva.cfg')

# start the db connection
db = ORM(app.config['DB_HOST'], app.config['DB_PORT'], app.config['DB_USERNAME'], app.config['DB_PASSWORD'])

# Close the DB session at the end of each request.
@app.teardown_appcontext
def shutdown_session(exception=None):
    db.shutdown_session()

# register the endpoints
app.register_blueprint(ui_bp)
app.register_blueprint(api_data_bp)

# Create SSL context
context = (app.config['SSL_CRT'], app.config['SSL_KEY'])

# debugging only
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True, ssl_context='adhoc', threaded=True)
