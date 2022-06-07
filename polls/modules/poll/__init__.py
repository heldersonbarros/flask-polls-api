from flask import Blueprint

poll = Blueprint('poll', __name__, url_prefix='/polls')

from . import controller