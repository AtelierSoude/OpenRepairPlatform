FROM python:3-stretch
ENV PYTHONUNBUFFERED 1
RUN mkdir /ateliersoude
ADD requirements.txt /ateliersoude/
# will disappear when the volume is mounted, but that's ok
RUN pip install -r /ateliersoude/requirements.txt
EXPOSE 8000
# for manual runserver and ipdb
EXPOSE 8001
CMD sh /ateliersoude/bootstrap.sh
