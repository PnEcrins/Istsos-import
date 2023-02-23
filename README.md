# Project presentation

This python Flask application allows you to import raw data files into a procedure with mapping source file columns to istSOS values.

**1.** Upload a data file:

![image](https://user-images.githubusercontent.com/4418840/199719515-eb2274c3-a60b-4a1e-938e-5fd257c9cb55.png)

**2.** Map columns:

![image](https://user-images.githubusercontent.com/4418840/199719747-9dbd7a52-a4d6-42d3-b411-3d762925108b.png)

**3.** Email import report:

After uploading data into istSOS database, an email will be sent with import report, including eventual errors and data quality values.

## About data import

### Float conversion

The float representation change between countries:  
In UK `'123,6'` means `1236.0` whereas in France its float representation is `123.6`.  
The application takes the current server locale to determine how to cast string to float.  
You can override this behaviour with the parameter `LOCALE`.

### Null and Nan values

If the values of an observed properties is missing, you must fill it with the "Nan" values.  
An empty value "NULL", or any other values not convertible to float will cause an error for all the corresponding eventimes.

### Data quality

The data quality is calculated during the data importat folowing this steps :

- check if a quality constraint exist at observed propery or at procedure level
  - If no quality constraint: set `DEFAULT_QI` and stop
  - Else
    - check the observed property constraint :
      - if the value match the constraint: set `VALID_PROPERTY_QI`
      - if not : set `INVALID_QI`
    - check the procedure (or station) constraint
      - if the value match the constraint: set `VALID_STATION_QI`
      - if not : set `INVALID_QI`

The qualities values are configurable is the config file and the default values are :

    INVALID_QI = 0
    DEFAULT_QI = 100
    VALID_PROPERTY_QI = 200
    VALID_STATION_QI = 210

# Installation

### Download source code

- With git:

      git clone https://github.com/PnEcrins/istSOS-import.git

- Or with wget:

      wget https://github.com/PnEcrins/istSOS-import/archive/refs/heads/main.zip
      unzip main.zip
      rm main.zip
      mv istSOS-import-main istSOS-import

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
    # add uuid extension
    sudo -n -u postgres -s psql -d <DB_NAME> -c 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'

The database is install with a 'admin' user which has 'ADMIN' role. If you accidentaly delete this user 


### Authentication

IstSOS provide its own authentication/authorization and user management system. 
In the backoffice you can create users and assign them to two type of roles (ADMIN an USER)
User with ADMIN role can create/edit imports and create/edit user.
User with USER role can only create/edit imports

You can also plug IstSOS with an external authentication backend which implement OpenID Connect protocol (like KeyCloak). To enable this, pass the parameter `OIDC_AUTHENT` to true, unsample the file `src/istsosimport/client_secret.example.json` to `src/istsosimport/client_secret.json` and fill it. With this authentication method, all the users you have in your external user database will be able to connect to the app. You can filter the users which can access to the app with the parameter `OIDC_GROUP_AUTHORIZE` and fill it with the name of the external group you want to authorize. By default the users will be set with "USER" role. You can set them to "ADMIN" role with the command `flask auth set-admin <user-uuid>`
To use the command, activate the virtualenv : 

    source venv/bin/activate
    cd src/istsosimport
    flask auth set-admin <user-uuid>

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
