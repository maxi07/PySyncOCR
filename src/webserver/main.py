from flask import Blueprint, render_template, redirect, url_for
bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return redirect(url_for('main.dashboard'))

@bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
