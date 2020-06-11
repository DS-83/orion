from flask import Blueprint, render_template
from app.auth import login_required, user_role

# # set optional bootswatch theme
# app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

bp = Blueprint('admin', __name__, url_prefix='/admin')

# Add administrative views here
@bp.route('/')
@login_required
@user_role
def index():
    return render_template('admin/admin.html')
