## Django-AtelierSoude

OpenRepairPlatform is a Django based application designed to organize collaborative repair structures, features provides organization managment, event publishing, community members managment, repair tracking and sharing.

The plateform is created by Atelier Soudé, an organization which repair everyday's people electric and electronic obejects in Lyon, France.

### Move to the deployment directory

```bash
cd [git checkout directory]/deployment
```

### Update bootstrap data (optional)

Only if a change is needed in the initial content. It is possible to dump the
data that was manually created and make it a fixture. This involves opening a
shell in the running container (`docker exec -ti deployment_django_1 bash`), cd'ing
to the `/ateliersoude` directory and running `./manage.py`. Look at the
`quotation/fixtures/quotation/README.txt` file for more.

### Running the application

After cd'ing to the main directory (and having docker-compose installed), do this only once
```bash
./start.sh create_env
```

(later: fill in the environment variables like passwords in here)
Then to run the application:

```bash
./start.sh dev
```

### Logs

Having the logs displayed to STDOUT is done with `docker logs -f ateliersoude-django`
except for the dev server where they're displayed by default (container isn't detached)

### Get into the containers

- Application:  `docker exec -ti deployment_django_1 bash`
- Database: ` docker exec -ti deployement_ateliersoude-postgres_1 bash`

### Fixture data

You can find some already implemented [users fixtures](users/fixtures/users/001_users.json) such as :

login: `admin@example.com`
passwd: `foobar`

### Unit Tests

To run unit tests:

`docker-compose -f deployment/docker-compose.yml run --rm django python ateliersoude/manage.py test plateformeweb.tests --settings=ateliersoude.settings.test`

### Debugger

Need a debugger ? in your view file :

```
from ipdb import set_trace

set_trace()
```

to make it interactive run thet test with external ports, add `--service-ports` to the test command.

`docker-compose -f deployment/docker-compose.yml run --service-ports --rm django python ateliersoude/manage.py test plateformeweb.tests --settings=ateliersoude.settings.test`



