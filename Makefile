SHELL := /bin/bash
dev:
	( \
		source env/bin/activate; \
		python server/run.py; \
	)
dev-install:
	( \
		source env/bin/activate; \
		sudo apt-get install mysql-server; \
		sudo apt-get install python3-dev; \
		sudo apt-get install libmysqlclient-dev; \
		pip install -r requirements.txt; \
	)
prod-install:
	( \
		sudo apt-get install mysql-server; \
		sudo apt-get install python3-dev; \
		sudo apt-get install libmysqlclient-dev; \
		sudo apt-get install libapache2-mod-wsgi-py3; \
		sudo apt-get install python3-pip; \
		sudo python3 -m pip install -r requirements.txt; \
		mysql -u root -p < create_table.sql; \
		mysql -u root -p < create_test.sql; \
	)
test:
	( \
		source env/bin/activate; \
		nosetests server --with-xunit --traverse-namespace --with-xcoverage --cover-package=app; \
	)
freeze:
	( \
		source env/bin/activate; \
		pip freeze > requirements.txt; \
	)
deploy:
	sudo cp saving-nemo.conf /etc/apache2/sites-available/saving-nemo.conf
	cd /etc/apache2/sites-available && sudo a2ensite saving-nemo.conf
	sudo service apache2 restart
	sudo /etc/init.d/apache2 reload
deploy-dev:
	sudo cp saving-nemo.conf /etc/apache2/sites-available/saving-nemo-dev.conf
	cd /etc/apache2/sites-available && sudo a2ensite saving-nemo-dev.conf
	sudo service apache2 restart
	sudo /etc/init.d/apache2 reload
