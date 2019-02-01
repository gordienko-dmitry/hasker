# HASKER
**Poor Man's Stackoverflow**  

Simple Q&A site.  
Available to use for link: http://hasker.site

Site have two apps: questions and users with own microclimate inside.
Available links:
```
/ - empty link - index page with all questions sorted by date publishing with pagination
/hot - list of questions sorted by rank with pagination
/rest/ - api functions (read for this in api folder)

/users/signup - sign up page
/users/login - log in page
/users/logout - log out
/users/profile - user's profile page

/questions/search?query={} - result of searching (you can search for tags, query=tag:{})
/questions/question/{} - question page with answers
/questions/ask - page for new question
/questions/vote - ajax query for vote question or answer
/questions/right_answer - ajax query for changing right answer for question

```

Done with CBV technology.


### Deploy site:  
In Docker:
```
docker run --rm -it -p 8000:80 ubuntu:latest /bin/bash
apt-get update && apt-get upgrade
apt-get -y install git
git clone https://github.com/NorthenFox/hasker.git
apt-get install make
cd hasker
make prod
```

Without docker
```
apt-get update && apt-get upgrade
apt-get -y install git
git clone https://github.com/NorthenFox/hasker.git
apt-get install make
cd hasker
make prod
```

Use Ubuntu version 18 & later.
Deploy settings store in dpl folder:
```
hasker.conf - config for supervisor with uwsgi settings
hasker.site.conf - settings for nginx
pg_hba - file with settings postgresql (file in settings postgresql folder will it replaced with that file)
uwsgi.ini - config for uwsgi
uwsgi_params - parameters of uwsgi
```

Also, in dpl directory situated sock file.
If you have errors with nginx and uwsgi, try give permissions on that directory.


## Also aviable rest api (directory "api")  
API url - rest/  
You can look at methods in swagger http://hasker.site/rest/swagger  
And read in api/readme.md


### SETTINGS
Settings of project store in hasker/settings.py, except local settings fot each server,
they store in file hasker/local_settings.py

*ATTENTION*: secret key taken from a file on disk - make sure you copy it to your server

**like an example of file hasker/local_settings.py**
```
# prod settings
DEBUG = False

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'hasker',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': '',
        'PORT': '5432'
    }
}

# SECRET_KEY
with open('/etc/secret_key.txt') as f:
    SECRET_KEY = f.read().strip()
```
