"""This script runs the Flask application in development environment"""

import os
from app.views import create_app

#pylint: disable=invalid-name
port = int(os.environ.get('PORT', 5000))
app = create_app('app.config')
app.run(host='0.0.0.0', port=port)
