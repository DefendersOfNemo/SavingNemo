import sys
import logging
logging.basicConfig(stream=sys.stderr)

sys.path.insert(0,"/var/www/DeployApp/SavingNemo/server/app/")
from views import app as application