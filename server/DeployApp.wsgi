import sys
import logging
logging.basicConfig(stream=sys.stderr)

sys.path.insert(0,"/var/www/DeployApp/SavingNemo/server/")
from app.views import app as application