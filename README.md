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

- Initial build, full rebuild (drops all DB content): `./rebuild-and-start.sh rebuild_all`
- Rebuild application, keep DB intact: `./rebuild-and-start.sh rebuild`
- Reload application (in cases of minor code changes, faster): `./rebuild-and-start.sh reload`

Note the build + run command will create docker containers and launch them, so a
running docker daemon is needed.

### Logs

Having the logs displayed to STDOUT is done with `docker logs -f ateliersoude-django`

### Get into the containers

- Application:  `docker exec -ti ateliersoude-django bash`
- Database: ` docker exec -ti ateliersoude-postgres bash`

