# Project presentation

# Download

    git clone https://github.com/PnEcrins/Istsos-import.git

# Instalation

### Install system requirements:

    apt install python3-pip redis

### Create a python virtualenv and install dependencies

    sudo pip3 install virtualenv
    virtualenv -p /usr/bin/python3 venv
    source venv/bin/activate
    pip install .

### Config file

### Install database

Do not do this command if you already have a istosos-import instance for an other service

    cd src/istsosimport
    flask db upgrade

# Run in dev

Run flask app and celery app in two separate terminals

    flask run
    celery -A istsosimport.celery_app worker -l INFO
