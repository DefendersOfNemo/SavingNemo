#!usr/bin/python

from app import app
import os  
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)

#import sys
#sys.path.insert(0, '/home/abhijeet/GitRepos/SavingNemo/server')

from app import app as app
#app.run()
