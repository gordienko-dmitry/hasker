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
	@cp ./dpl/pg_hba.conf /etc/postgresql/10/main/hb_hba.conf
	@service postgresql restart
	@apt-get install -y sudo
	@sudo -u postgres createdb hasker
	@sudo -u postgres psql --command "ALTER USER postgres WITH superuser password 'postgres';"
	@echo done

	@echo "Configure app..."
	@python3 manage.py makemigrations
	@python3 manage.py migrate
	@echo done

	@echo "Installing & configure uwsgi..."
	@sudo apt-get install libpcre3 libpcre3-dev
	@pip3 install uwsgi -I

	@echo "Deploy things"
	@sudo apt-get install -y supervisor
	@cp ./dpl/hasker.conf /etc/supervisor/conf.d
	@sudo supervisorctl update
	@sudo supervisorctl restart hasker

    @-mkdir /var/log/hasker
    @echo "Installing & configure nginx..."
    @apt-get install -y nginx
    @cp ./dpl/hasker.site.conf /etc/nginx/site-available/
    @ln -s /etc/nginx/sites-available/hasker.site.conf  /etc/nginx/sites-enabled/hasker.site.conf
	@service nginx start

