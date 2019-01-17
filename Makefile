prod:
	@echo "Installing python & requirments..."
	@apt-get install -y build-essential \
		python3 \
		python3-dev \
		python3-pip
	@pip3 install --upgrade pip

	@pip3 install -r  requirments.txt
	@echo done

	@echo "Installing database..."
	@apt-get install -y postgresql-10 postgresql-contrib-10
	@service postgresql start
	@apt-get install -y sudo
	@-sudo -u postgres createdb hasker owner postgres
	@sudo -u postgres psql --command "ALTER USER postgres WITH superuser password 'postgres';"
	@echo done

	@-mkdir /var/log/hasker
	@echo "Installing & configure nginx..."
	@apt-get install -y nginx
	@cp nginx.conf /etc/nginx/conf.d/
	@service nginx start

	@echo "Configure app..."
	@python3 manage.py makemigrations \
	@python3 manage.py migrate
	@echo done

	@echo "Installing & configure uwsgi..."
	@pip3 install uwsgi
	uwsgi --ini uwsgi.ini
