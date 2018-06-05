## Django-AtelierSoude

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

After cd'ing to the deployment directory (and having docker-compose installed)
```bash
docker-compose up --build --force-recreate
```
(omitting --build --force-recreate ? seems buggy for me)

### Logs

Having the logs displayed to STDOUT is done with `docker logs -f ateliersoude-django`
except for the dev server where they're displayed by default (container isn't detached)

### Get into the containers

- Application:  `docker exec -ti deployment_django_1 bash`
- Database: ` docker exec -ti deployement_ateliersoude-postgres_1 bash`

### Fixture data

You can find some already implemented [users fixtures](users/fixtures/users/001_users.json) such as :

`login: admin@example.com
passwd: foobar`
