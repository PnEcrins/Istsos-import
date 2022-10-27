# Project presentation

# Download

    git clone https://github.com/PnEcrins/Istsos-import.git

# Instalation

### Install system requirements:

    apt install python3-pip redis libpq-dev

### Create a python virtualenv and install dependencies

    cd Istsos-import
    sudo pip3 install virtualenv
    virtualenv -p /usr/bin/python3 venv
    source venv/bin/activate
    pip install .

### Config file

Copy and edit the config file

    cp config.toml.example config.toml
    nano config.toml

### Install database

Do not do this command if you already have a istosos-import instance for an other service

    cd src/istsosimport
    flask db upgrade

### Prod deployment

##### Create a systemd service for flask app

    sudo cp istsosimport.service /etc/systemd/system
    # Replace <APP_DIRECTORY> by the directory where the app is located (/opt/istsos-import for exemple) and $USER by your current linux user
    sudo mkdir /var/log/istsosimport
    sudo chown $USER: /var/log/istsosimport/
    sudo systemctl daemon-reload
    sudo systemctl enable istsosimport
    sudo systemctl start istsosimport

##### Create a systemd service for celery worker

    sudo cp istsosimport-worker.service /etc/systemd/system
    # Replace <BASE_DIR> by the directory where the app is located (/opt/istsos-import for exemple) and $USER by your current linux user
    sudo systemctl daemon-reload
    sudo systemctl enable istsosimport-worker
    sudo systemctl start istsosimport-worker

##### Make a apache conf

    sudo cp istsosimport.conf /etc/apache2/sites-available/
    sudo a2enmod proxy
    sudo a2ensite istsosimport.conf
    sudo systemctl reload apache2

# Run in dev

In order to send mail, Flask has to know the "SERVER_NAME". In dev we use IP but we don't have a domain. Add those line in your `/etc/hosts`

::
127.0.0.1 istsosimport.local

In config.toml set the `URL_APPLICATION` like this : `URL_APPLICATION = "http://istsosimport.local:<PORT>/"` where the port is the port on which Flask run

Run flask app and celery app in two separate terminals

    flask run
    celery -A istsosimport.celery_app worker -l INFO

The app is available on `http://istsosimport.local:<PORT>`

# Configuration

The main configuration file is `config.toml`. By default it contains only mandatory parameters. Advanced parameters variable can be found it the `config.toml.example`.
At any cha nge in the config file, run this commands:

::
sudo systemctl reload istsosimport.service

### Float conversion

The float representation change between countries :
In UK `'123,6'` mean `1236.0` whereas in France its float representation is `123.6`.
The app take the current server locale to determine how cast string to float. You can override this behaviour with the parameter `LOCALE`
