"""
Utils Module Routes
Utility routes for the Utils module (currently minimal)
"""

from flask import Blueprint, jsonify
from modules.core.security_enforcement import secure_banking_route

# Create utils blueprint
utils_bp = Blueprint('utils', __name__, url_prefix='/utils')

# API endpoints moved to centralized /api/v1/utils/ structure