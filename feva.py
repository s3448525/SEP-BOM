from flask import Flask
from handlers.ui import ui_bp
from handlers.comparisons import api_comparisons_bp
from core.orm import ORM

# create a new wsgi application
app = Flask('feva', instance_relative_config=True, static_folder='assets/static', template_folder='assets/templates')

# load configurations
app.config.from_pyfile('config.py')
app.config.from_pyfile('feva.cfg')

# start the db connection
db = ORM(app.config['DB_HOST'], app.config['DB_PORT'], app.config['DB_USERNAME'], app.config['DB_PASSWORD'])

# register the endpoints
app.register_blueprint(ui_bp)
app.register_blueprint(api_comparisons_bp)

# debugging only
if __name__ == '__main__':
    app.run(port=8080, debug=True)
