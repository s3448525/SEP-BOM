from flask import Blueprint, render_template

ui_bp = Blueprint('ui', 'ui')


@ui_bp.route('/')
def home():
    return render_template('home.html')
