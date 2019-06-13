Atelier Soudé
=============

Le projet a été récupéré sur github : https://github.com/AtelierSoude/OpenRepairPlatform


remote origin : git@gitlab.com:hashbangfr/ateliersoude.git

remote github : git@github.com:AtelierSoude/OpenRepairPlatform.git

-------------

Dépendances :
-------------

- postgresql


---------------------------------

Lancer le projet en développement :
-----------------------------------

Par défault, en développement, l'application tente de se connecter à la BDD
"ateliersoude" en local en utilisant le compte de l'utilisateur courant, sans mot de passe

.. code-block:: bash
    
    createdb ateliersoude
    ./manage.py migrate
    ./manage.py createsuperuser
    ./manage.py runserver

Si vous préférez, vous pouvez également lancer le projet en développement en utilisant docker:

.. code-block:: bash

    sudo docker build -f deployment/docker-app/Dockerfile -t ateliersoude .
    sudo docker run -it --rm -p 8000:8000 ateliersoude

Vous pouvez ensuite accéder au site à l'addresse http://127.0.0.1:8000/ l'utilisateur admin étant: admin@example.com passwd: adminpass
