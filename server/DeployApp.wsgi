import sys
import logging
logging.basicConfig(stream=sys.stderr)

sys.path.insert(0,"/var/www/DeployApp/SavingNemo/server/")
from app.views import create_app
application = create_app('app.config')
