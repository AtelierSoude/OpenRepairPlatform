## Django-AtelierSoude

### Move to the base directory

```bash
cd [git checkout directory]
```

### Update bootstrap data (optional)
 
Only if a change is needed in the initial content. It is possible to dump the 
data that was manually created and make it a fixture. This involves opening a 
shell in the running container (`docker exec -ti ateliersoude-django bash`), cd'ing
to the `/ateliersoude` directory and running `./manage.py`. Look at the
`quotation/fixtures/quotation/README.txt` file for more.
 
### Build the application and run it

- Before the initial build, run a full db rebuild (drops all DB content), also use this
to wipe out the DB when needed: 

  `./start.sh rebuild_db`
  
- Rebuild application, collect static files, and start the gunicorn (production) 
server, keeping the DB intact: 
  
  `./start.sh rebuild`

- Reload the application (for gunicorn, in cases of minor code changes, faster): 

  `./start.sh reload`

- Start the auto-reloading development server (preferred way for development, all 
changed files are taken into account instantly):

  `./start.sh dev`

Note the build + run command will create docker containers and launch them, so a
running docker daemon is needed.

### Ports

- For the dev server, the default is 8001 on all interfaces
- For the gunicorn server, the default is 8000 on all interfaces

The exposed port is configurable as the 2nd argument to the command, example:

`./start.sh dev 127.0.0.1:8000` will start the dev server on port 8000, accessible only on localhost. Same thing for gunicorn

### Logs

Having the logs displayed to STDOUT is done with `docker logs -f ateliersoude-django`
except for the dev server where they're displayed by default (container isn't detached)

### Get into the containers

- Application:  `docker exec -ti ateliersoude-django bash`
- Database: ` docker exec -ti ateliersoude-postgres bash`

