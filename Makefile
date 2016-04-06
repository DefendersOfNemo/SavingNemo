deploy:
	sudo cp saving-nemo.conf /etc/apache2/sites-available/saving-nemo.conf
	cd /etc/apache2/sites-available && sudo a2ensite saving-nemo.conf
	sudo service apache2 restart
	sudo /etc/init.d/apache2 reload
