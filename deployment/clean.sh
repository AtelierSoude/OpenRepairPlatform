#!/usr/bin/env bash

sudo docker stop openrepairplatform_nginx && sudo docker rm openrepairplatform_nginx
sudo docker stop openrepairplatform_python && sudo docker rm openrepairplatform_python
sudo docker stop postgres && sudo docker rm postgres

sudo docker network rm openrepairplatform

# return 0 even if previous commands failed (it means resources were already deleted)
exit 0
