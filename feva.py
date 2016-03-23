from flask import Flask
from handlers.ui import ui_bp
from handlers.comparisons import api_comparisons_bp

# create a new wsgi application
app = Flask('feva', static_folder='assets/static', template_folder='assets/templates')

# register the endpoints
app.register_blueprint(ui_bp)
app.register_blueprint(api_comparisons_bp)

# debugging only
if __name__ == '__main__':
    app.run(port=8080, debug=True)
