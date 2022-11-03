# Project presentation

This python Flask application allows you to import raw data files into a procedure with mapping source file columns to istSOS values.

**1.** Upload a data file:

![image](https://user-images.githubusercontent.com/4418840/199719515-eb2274c3-a60b-4a1e-938e-5fd257c9cb55.png)

**2.** Map columns:

![image](https://user-images.githubusercontent.com/4418840/199719747-9dbd7a52-a4d6-42d3-b411-3d762925108b.png)

**3.** Email import report:

After uploading data into istSOS database, an email will be sent with import report, including eventual errors and data quality values.

# Download source code

- With git:

      git clone https://github.com/PnEcrins/istSOS-import.git

- Or with wget:

      wget https://github.com/PnEcrins/istSOS-import/archive/refs/heads/main.zip
      unzip main.zip
      rm main.zip
      mv istSOS-import-main istSOS-import

# Installation

### Install system requirements:

    apt install python3-pip redis libpq-dev

### Create a python virtualenv and install dependencies

    cd istSOS-import
    sudo pip3 install virtualenv
    virtualenv -p /usr/bin/python3 venv
    source venv/bin/activate
    pip install .

### Configuration file

Copy and edit the configuration file

    cp config.toml.example config.toml
    nano config.toml

### Install database

Do not do this command if you already have an istSOS-import instance for another service

    cd src/istsosimport
    flask db upgrade

### Production deployment

##### Create a systemd service for the Flask application

    sudo cp istsosimport.service /etc/systemd/system
    # Replace <APP_DIRECTORY> by the directory where the app is located (/opt/istsos-import for example) and $USER by your current linux user
    sudo mkdir /var/log/istsosimport
    sudo chown $USER: /var/log/istsosimport/
    sudo systemctl daemon-reload
    sudo systemctl enable istsosimport
    sudo systemctl start istsosimport

##### Create a systemd service for the Celery worker

    sudo cp istsosimport-worker.service /etc/systemd/system
    # Replace <BASE_DIR> by the directory where the app is located (/opt/istsos-import for example) and $USER by your current linux user
    sudo systemctl daemon-reload
    sudo systemctl enable istsosimport-worker
    sudo systemctl start istsosimport-worker

##### Make an Apache configuration

    sudo cp istsosimport.conf /etc/apache2/sites-available/
    sudo a2enmod proxy
    sudo a2ensite istsosimport.conf
    sudo systemctl reload apache2

# Run in dev

In order to send mail, Flask has to know the "SERVER_NAME". In dev we use IP but we don't have a domain. Add these line in your `/etc/hosts`:

    127.0.0.1 istsosimport.local

In `config.toml`, set the `URL_APPLICATION` like this: `URL_APPLICATION = "http://istsosimport.local:<PORT>/"` where the port is the port on which Flask runs.

Run Flask app and Celery app in two separate terminals:

    flask run
    celery -A istsosimport.celery_app worker -l INFO

The application is available at `http://istsosimport.local:<PORT>`.

# Configuration

The main configuration file is `config.toml`. By default it contains only mandatory parameters.  
Advanced parameters variable can be found in the `config.toml.example` file.  
At any change in the configuration file, run this commands:

    sudo systemctl reload istsosimport.service

### Float conversion

The float representation change between countries:  
In UK `'123,6'` means `1236.0` whereas in France its float representation is `123.6`.  
The application takes the current server locale to determine how to cast string to float.  
You can override this behaviour with the parameter `LOCALE`.

### Null and Nan values

If the values of an observed properties is missing, you must fill it with the "Nan" values.  
An empty value "NULL", or any other values not convertible to float will cause an error for all the corresponding eventimes.
