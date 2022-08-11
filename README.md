# Instalation

Install system requirements:

    apt install python3-pip redis

Create a python virtualenv and install dependencies

    sudo pip3 install virtualenv
    virtualenv -p /usr/bin/python3 venv
    source venv/bin/activate
    pip install requirements.txt

Run flask app and celery app in two separate terminal

    flask run
    celery -A istsosimport.celery_app worker -l INFO
