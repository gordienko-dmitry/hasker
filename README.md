# HASKER
**Poor Man's Stackoverflow**  

Simple Q&A site.  
Available to use for link: http://hasker.site

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


## Also aviable rest api (directory "api")  
API url - rest/  
You can look at methods in swagger http://hasker.site/rest/swagger  
And read in api/readme.md
