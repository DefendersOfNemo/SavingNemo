"""
    upload.py
    ~~~~~~~~~~~~~~

    This script includes the methods for creating the app and 
    registering the  blueprints.

    :copyright: (c) 2016 by Abhijeet Sharma.
    :license: The MIT License (MIT), see LICENSE for more details.
"""

from flask import Flask


def create_app(config_filename):
    app = Flask(__name__, template_folder="../../client/templates", static_folder="../../client/static")
    app.config.from_object(config_filename)

    from app.query import query_page
    from app.login import login_page
    from app.upload import upload_page

    app.register_blueprint(query_page)
    app.register_blueprint(login_page)
    app.register_blueprint(upload_page)
    return app

# This function makes sure the server only runs if the script is executed directly
# from the Python interpreter and not used as an imported module.
if __name__ == '__main__':
    app = create_app('app.config')
    app.run()
