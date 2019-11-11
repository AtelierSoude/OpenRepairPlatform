# Atelier Soudé

OpenRepairPlatform is a Django based application designed to organize collaborative repair structures, features provides organization managment, event publishing, community members managment, repair tracking and sharing.

The plateform is created by Atelier Soudé, an organization which repair everyday's people electric and electronic objects in Lyon, France.


## Develop with Docker

Run the following command:

```
docker-compose up
```

You can then access `http://127.0.0.1:8000/` with the admin user `admin@example.com` // `adminpass`

### Debug with Visual Studio Code

If you open the main folder with vs code, you will be able to use the configuration present in `.vscode`.

This will allow you to connect to the container in debug mode and to stop at breakpoints in the code, which is quite confortable to inspect the variables and test new code in the required state of the program (typically before a failure).

For this, just click on `Debug`, and `Start Debugging`: you will run the `Python: Run in Docker` configuration. 
A small additional bar will appear with useful commands for the debug: go to next breakpoint, stop debugging, etc

Create a breakpoint in the code, for example in a view, and go to the corresponding page from your browser.
The browser will freeze and vs code will stop at the breakpoint.

In the lower part of vs code, in the `DEBUG CONSOLE`, you can test code.

In the debug section, in the left vertical bar, you can see all the breakpoints, all the variables and their content, and the call stack.
You can click on any step of the call stack, and browser the variables, test some code, etc, at this step.

### Coding "live"

The local code is mounted in a Docker volume, so if you change the code locally and refresh your browser, you will immediatly see the changes.

### Run integration tests

Integration tests are run using a Docker image containing a chrome Selenium installation and a VNC server.
It is possible to debug the tests using a local VNC client that connects to the VNC server in the Docker container, that allows to graphically see what the selenium test is doing on the site.

`sudo apt-get install krdc`

Start KRDC, and connect to `localhost:5900`

To see the running chrome sessions:
`http://localhost:4444/wd/hub/static/resource/hub.html`

To launch the tests :
`python3 -m pytest /tests/integration_tests.py`