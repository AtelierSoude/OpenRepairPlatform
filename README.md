----- FR -----

# OpenRepairPlatform

Ce projet cherche à faciliter l’accessibilité de la réparation par le plus grand nombre. Par une interface simple et claire, l'application web invite participants et organisations à collaborer autours de l’auto-réparation et de la réparation participative.

OpenRepairPlateform est une application basée sur Django, pensée pour organiser les structures de réparations participatives.
Elle intègre principalement des fonctionnalités de gestion d'organisation, de membres, de comptabilité, la publication d'événements, d'inventaire et de suivi/partage de réparations.

Cette application est développée et notamment utilisée par [l'Atelier Soudé](https://atelier-soude.fr).
La procedure d'installation et la documentation est disponible [ici](https://openrepairplatform.readthedocs.io/en/latest/)

## Envie de contribuer ?

OpenRepairPlateform se veut être un commun et accessible à tout.es.
Si vous souhaitez nous aider ou bien utiliser le commun, vous pouvez rejoindre notre équipe de dév, via notre (Forum)[https://forum.atelier-soude.fr/c/reparons/101] ou en nous envoyant un message sur le (formulaire contact)[https://atelier-soude.fr/contact/]. Il est aussi possible de contribuer financièrement via (ce site)[https://lescommuns.tiers-lieux.org/#detail-un-commun.communId.672ba674b778d86e155788be].


- (Forum du projet)[https://forum.atelier-soude.fr/c/reparons/101]
- Github, outil de dev -> normalement tu es dessus :)
- Discord, messagerie directe : Sur demande !
- (Plateforme vitrine de collaboration)[https://openrepairplateform.tibillet.coop/ 1]
- (Tableau des fonctionnalité à dev)[https://github.com/orgs/AtelierSoude/projects/1/views/7?groupedBy%5BcolumnId%5D=Status&visibleFields=%5B%22Title%22%2C%22Assignees%22%2C%22Status%22%2C%22Linked+pull+requests%22%2C%22Milestone%22%2C240118894%5D&sortedBy%5Bdirection%5D=asc&sortedBy%5BcolumnId%5D=Status]
- (Vitrine du projet pour des contributions)[https://lescommuns.tiers-lieux.org/#detail-un-commun.communId.672ba674b778d86e155788be]


----- ENG -----

This application is still in developpment.
Any contributes are welcome. Please contact us if you want to contribute and we tell you how to.

OpenRepairPlatform is a Django based application designed to organize collaborative repair structures, features provides organization managment, event publishing, community members managment, repair tracking and sharing.

The plateform is created by Atelier Soudé, an organization which repair everyday's people electric and electronic objects in Lyon, France.

Full installation and user documentation are avalaible [here](https://openrepairplatform.readthedocs.io/en/latest/). (sorry, only in French at this point !)

For basic develop installation, follow those steps:

## Interested in contributing?

OpenRepairPlatform aims to be a shared resource accessible to everyone.
If you would like to assist us or utilize the shared resource, you can join our development team via our (Forum)[https://forum.atelier-soude.fr/c/reparons/101]  or by sending us a message on the (contact form)[https://atelier-soude.fr/contact/].  It is also possible to contribute financially via (this website)[https://lescommuns.tiers-lieux.org/#detail-un-commun.communId.672ba674b778d86e155788be].


- (Project forum)[https://forum.atelier-soude.fr/c/reparons/101]
- Github, outil de dev -> normalement tu es dessus :)
- Discord, messagerie directe : Sur demande !
- (Collaboration showcase platform)[https://openrepairplateform.tibillet.coop/ 1]
- (Table of features to be developed)[https://github.com/orgs/AtelierSoude/projects/1/views/7?groupedBy%5BcolumnId%5D=Status&visibleFields=%5B%22Title%22%2C%22Assignees%22%2C%22Status%22%2C%22Linked+pull+requests%22%2C%22Milestone%22%2C240118894%5D&sortedBy%5Bdirection%5D=asc&sortedBy%5BcolumnId%5D=Status]
- (Project showcase for contributions)[https://lescommuns.tiers-lieux.org/#detail-un-commun.communId.672ba674b778d86e155788be]

## Run the application in production mode

1 - set up the environment

```bash
git clone https://github.com/AtelierSoude/OpenRepairPlatform.git
cd OpenRepairPlatform
touch .env
```

2 - Populate the envfile with the following content. Make sure to change the vars.

```bash
#default content of the configuration .env file
# Activate the location search on home page
LOCATION=1

#DJANGO settings for configuration dev or production
DJANGO_SETTINGS_MODULE=openrepairplatform.settings.dev
SECRET_KEY=CHANGE_ME

# To activate the debug mode, set the environment variable to True
DEBUG=true
PREPROD=True # !!! to keep robots from indexing preprod pages. Change to False on Production server

#Emailing settings only used in production mode
EMAIL_PASSWORD=CHANGE_ME
EMAIL_HOST_USER=CHANGE_ME
EMAIL_HOST=CHANGE_ME
DEFAULT_FROM_EMAIL=no-reply@reparons.org

#Let's encrypt and nginx settings
#The principal domain that django will use
DOMAINDNS=dev.reparons.org
#Some autorised hosts and vars are added for docker implementation
DOMAINS=localhost 127.0.0.1 [::1]
EMAIL=contact@atelier-soude.fr
SERVER_CONTAINER=openrepairplatform_nginx


# POSTGRES settings
POSTGRES_USER=openrepairplatform
POSTGRES_DBNAME=openrepairplatform
POSTGRES_PASSWORD=mangerdespommes
```

3 - launch the application in production mode

This script will stop all previous openrepairplatform services and start the application.
1 - obtaining the certificate for the domain by using certbot/nginx
2 - building the application
3 - starting the application
4 - running all the migrations
5 - starting the application

```bash
sh ./install.prod.sh
```

## Run the application (in Develop mode only)

1.Set django, postgres and nginx/domain variables in `openrepairplatform/.env`

```bash
#default content of the configuration .env file
# Activate the location search on home page
LOCATION=1

#DJANGO settings for configuration dev or production
DJANGO_SETTINGS_MODULE=openrepairplatform.settings.dev
SECRET_KEY=CHANGE_ME

# To activate the debug mode, set the environment variable to True
DEBUG=true
PREPROD=False # !!! to keep robots from indexing preprod pages. Change to False on Production server

#Emailing settings only used in production mode
EMAIL_PASSWORD=CHANGE_ME
EMAIL_HOST_USER=CHANGE_ME
EMAIL_HOST=CHANGE_ME
DEFAULT_FROM_EMAIL=no-reply@reparons.org

#Let's encrypt and nginx settings
#The principal domain that django will use
DOMAINDNS=dev.reparons.org
#Some autorised hosts and vars are added for docker implementation
DOMAINS=localhost 127.0.0.1 [::1]
EMAIL=contact@atelier-soude.fr
SERVER_CONTAINER=openrepairplatform_nginx


# POSTGRES settings
POSTGRES_USER=openrepairplatform
POSTGRES_DBNAME=openrepairplatform
POSTGRES_PASSWORD=mangerdespommes
# For PG admin loggin
PGADMIN_DEFAULT_EMAIL=admin@admin.com
PGADMIN_DEFAULT_PASSWORD=root
```

2.Add the DOMAINDNS value to your host configuration

3.Run the following command:

```bash
cd [git checkout directory]/
docker-compose up
```
Enter into the container: 

```bash
docker exec -ti openrepairplatform bash
```

lauch app: 

```bash
python3 ./manage.py runserver 0.0.0.0:8005
```

The website is now deployed and accessible on http://[DOMAINDNS]

Then in the docker terminal, run the following command for livereload.

By default the dev app will start with a livereload server, the auto watch for django files, and the automatic compilation of vue.js files.


3 - Create an organization within the `http://localhost:8000/admin` path and you can start everythings else (further documentation will come).

## Build the application from a branch to a docker image

### build dev app from github branch

You can directly build an image by running the following command. This command will build the image from the selected branch localy. That way you will not have to clone the project localy and just use the image builded from github.

```bash
# Replace the BRANCHNAME with the branch name you want to build
docker build --file /django/Dockerfile https://github.com/AtelierSoude/OpenRepairPlatform.git\#BRANCHNAME:deployment
```

### build from local repository

1 - First you have to clone the project inyour directory using the following commands depending on your configuration.

```bash
 git clone https://github.com/AtelierSoude/OpenRepairPlatform.git

 #OR if you have a ssh key on github.com

 git clone git@github.com:AtelierSoude/OpenRepairPlatform.git

```

2 - You can now build your image using the following command

```bash
# enter your cloned directory
cd OpenRepairPlatform

# Build the image
# The -t option allows you to specify the name of the container it has to match the name in your docker-compose file for production
 docker build --file deployment/django/Dockerfile -t openrepairplateform-prod .
 ```

 ### Acces to Database administration
 The dev env provide a postgresqlAdmin interface which allows you to connect to the database.

 You can access it from the following url :
 http://localhost:5050/

 With the identity in the .env file


### Dump the database & restore on local environment

After being connected to your server, you can dump the database with the following command

```bash
# This guide shows you how to use gzip when pulling down a production database to your local environment
#
# A production database dump can be very large, like 1.5GB
# But database dumps contains a lot of empty space
# Gzipping the database can take the size from 1.5GB down to as low as 50MB
# But you are left zipping and unzipping all the time
#
# Follow these steps to avoid ever creating a large .sql file in the first place
# exporting and importing directly with the gzipped version
# For this example, the production server is named "production"

# On the production server:
# Navigate to your home directory. 
# If this next command fails, it is because you don't have permission to switch to the postgres user
# If so, you will need to login as root before you can run this next command
docker exec -ti postgres pg_dump -U ateliersoude ateliersoude | gzip -9 > dump_reparons.sql.gz

# Log out of the production server and go back to your local machine
# Use scp to download (-C uses compression for faster downloads)
scp -C user@IP:./deployement/saves-bdd/dump_reparons.sql.gz ./deployment/saves-bdd/

# If you already have a local database, the .sql file might complain if you try to import it.
# This can be due to duplicate keys, or if the SQL import attempts to create the table that already exists, etc.
# Only delete the database i f you are sure, but I do this all the time
# On OSX, run these commands
docker exec -t postgres dropdb -U openrepairplatform openrepairplatform  
docker exec -t postgres createdb -U openrepairplatform openrepairplatform

# Now re-import the database directly from the gzipped file:
#loggin into the container
docker exec -ti postgres /bin/bash
#in container run
gunzip < /srv/saves-bdd/dump_reparons.sql.gz | psql -U openrepairplatform openrepairplatform
```

### Debug with Visual Studio Code

If you open the main folder with vs code, you will be able to use the configuration present in `.vscode`.

This will allow you to connect to the container in debug mode and to stop at breakpoints in the code, which is quite confortable to inspect the variables and test new code in the required state of the program (typically before a failure).
Before starting, you may have to install the Python extension.

For this, just click on `Debug`, and `Start Debugging`: you will run the `Debug Django app` configuration.
A small additional bar will appear with useful commands for the debug: go to next breakpoint, stop debugging, etc
More information on debugging with vs code: `https://code.visualstudio.com/Docs/editor/debugging`

Create a breakpoint in the code, for example in a view, and go to the corresponding page from your browser.
The browser will freeze and vs code will stop at the breakpoint.

In the lower part of vs code, in the `DEBUG CONSOLE`, you can test code.

In the debug section, in the left vertical bar, you can see all the breakpoints, all the variables and their content, and the call stack.
You can click on any step of the call stack, and browser the variables, test some code, etc, at this step.

### Run unit tests

First, start the containers with `docker-compose up`
Then, run the tests with `docker exec openrepairplatform pytest --disable-pytest-warnings --cov=openrepairplatform --cov-report term-missing`


### Run integration tests

Integration tests are run using a Docker image containing a chrome Selenium installation and a VNC server.
It is possible to debug the tests using a local VNC client that connects to the VNC server in the Docker container, that allows to graphically see what the selenium test is doing on the site.

To install the VNC client on your local computer:

`sudo apt-get install krdc`

To launch it:

`krdc`

Start KRDC, and connect to `localhost:5900`

To see the running chrome sessions:
`http://localhost:4444/wd/hub/static/resource/hub.html`

To launch the tests :

First, start the Docker containers with `docker-compose up`, and then:

`docker exec openrepairplatform_selenium_1 python3 -m pytest /tests/integration_tests.py -v`

If you uncomment the following lines, it will wait for a debugger to connect before running the tests

```bash
ptvsd.enable_attach()
ptvsd.wait_for_attach()
```
