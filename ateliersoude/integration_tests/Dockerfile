FROM selenium/standalone-chrome-debug:3.141.59-xenon
USER root
RUN apt-get update && sudo apt-get install python3-pip -y
USER seluser
RUN pip3 install pytest selenium
