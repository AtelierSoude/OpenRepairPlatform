#!/usr/bin/env bash

sudo docker stop ateliersoude_nginx && sudo docker rm ateliersoude_nginx
sudo docker stop ateliersoude_python && sudo docker rm ateliersoude_python
sudo docker stop postgres && sudo docker rm postgres

sudo docker network rm ateliersoude

# return 0 even if previous commands failed (it means resources were already deleted)
exit 0
