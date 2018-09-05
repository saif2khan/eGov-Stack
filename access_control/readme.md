# What is access_control
This will module will handle:
* User account creation and management
* Role based access (READ, READ/WRITE, ADMIN)
* Scope based access (e.g. Geographical scope: country level, state level, city level, etc.) with support to add additional scopes in a hierarchy (e.g. Country --> State -> District ==> anyone with access to Country can view data right down to the District level)
* IP Whitelisting of trust applications (e.g. an app called BACKEND_MAPPER will be authenticated to perform all actions if the call originates from a trusted ip address)

# API:
https://app.swaggerhub.com/apis/Samagra-Governance/api/1.0.0#/

# App Setup Instructions for Deploying to Heroku
##### (See further down for generic Ubuntu instructions)

You will need the following ready in order to get this application running: 
* A Heroku Account (https://www.heroku.com)
* The Heroku CLI (command line interface) installed on your computer
* Python 3.6+ installed on your local computer. 
* Git installed on your local computer

To see the setup instructions for those first two items, please refer to the following link: https://devcenter.heroku.com/articles/getting-started-with-python#introduction

If you need instructions for installing python on your local machine, please see  the following guide: https://www.python.org/about/gettingstarted/

The following comments refer to the different steps located in the Heroku getting started guide. 

## Introduction Section on Heroku Getting Started
You will need to have python installed, and the `pipenv` installed locally for this to work. However there is no need for Postgres to be installed locally on your machine so you may skip that step. 

## Setup Section on Heroku Getting Started
Please follow this section as outlined. 

## Prepare the App Section on Heroku Getting Started
You will follow this section exactly, except that when you perform the `git clone` command make sure you clone the app from our git repository. This command would then become:

```git clone https://github.com/Samagra-Development/eGov-Stack.git```

## Deploy the App Section on Heroku Getting Started
After you have created the app, please complete the following before deploying the app. 

On heroku, install the following add-ons:
* Mailgun
* PostgresSQL

In you can install these add-ons easily by going to your heroku dashboard and clicking on "Configure Add Ons" in the overview section.

In your heroku dashboard, go to the settings section and click "Reveal Config Vars" Here you will add a new configuration variable called `AUTHENTICATE_SECRET` and the value should be a VERY long randomly generated password. This setting will keep encrypted parts of the application secure and should never be shared or publicly exposed. 

Once you have provisioned these add-ons and set your `AUTHENTICATE_SECRET` variable, you are almost ready to deploy your application. 

The next step is to initialize the database. To do this, create a new python virtual environment by running `pipenv shell` and the install the application dependencies with `pip install -r requirements.txt`

After those dependencies have been installed, you need to set a couple of environment variables. You can do that by running the following commands:

```export FLASK_APP=autoapp.py```

```export DATABASE_URL={use the database url in the heroku>settings>config vars section}```

*Caution, these commands can be platform dependent and could change if you are on Mac/Win/Linux*

Once these environment variables are set, you can initialize the database by running:

```flask db init```

```flask db migrate```

```flask db upgrade```

Run each command in order. This will create all the tables on the Heroku provided Postgres instance and allow the app to function properly. 

The next step is to setup the admin user. To do this, run the following command being sure to change the username, password, and email to the desired settings.

```flask initial_setup --username admin --password somepassword --email desired@email.com```

You are now ready to deploy the app, which can only be done via the command line using git. Use the following command:

```git push heroku master```

After you've confirmed that the build succeeded, you are all set

# App setup instructions for Ubuntu

#### You will need the following installed on your server

* Python 3.6+ with (Pipenv)
* NGINX
* Postgres (or other relational database) 
* **(Optional)** SQL lite is required in order to run the tests
* SMTP server **or** Mailgun service (first 10,000 emails are free https://www.mailgun.com/)
* Git

You will need to open the ports necessary for the webserver, SMTP server, and database.

It is recommended that a process monitoring service be utilized to make sure that the application is restarted automatically should it go down. As a recommendation, please see the docs for **Supervisor** (http://supervisord.org/)

## Clone the git repository to the target machine

You can do this by running the following command from whatever directory you would like to clone the application into.

```git clone https://github.com/Samagra-Development/eGov-Stack.git```

Next navigate to the folder that was just created with the new files.

```cd egov_stack/access_control```

Next, install the python required external libraries. To do this, create a new python virtual environment by running 

```pipenv shell```

and the install the application dependencies with 

```pip install -r requirements.txt```

## Set up your environment variables

There are several environment variables that need to be set before you can run the application. They are listed below:

* AUTHENTICATE_SECRET
* FLASK_APP
* DATABASE_URL
* **(If using mailgun for email)** MAILGUN_DOMAIN
* **(If using mailgun for email)** MAILGUN_API_KEY
* **(If using local SMTP server for email)** MAIL_SERVER
* **(If using local SMTP server for email)** MAIL_PORT
* **(If using local SMTP server for email)** MAIL_USERNAME
* **(If using local SMTP server for email)** MAIL_PASSWORD

You can set these variables by running the following commands:

```export AUTHENTICATE_SECRET={REALLY LONG AND RANDOM}```

This value should be a VERY long randomly generated password. This setting will keep encrypted parts of the application secure and should never be shared or publicly exposed. 

```export FLASK_APP=autoapp.py```

This environment variable tells flask where your application can be generated. 

```export DATABASE_URL={your connection URI}```

This variable will be different depending on what RDBMS you are using. Please see the documentation to configure this correctly (http://docs.sqlalchemy.org/en/latest/core/engines.html).


## Setting up the database

Once these environment variables are set, you can initialize the database by running:

```flask db init```

```flask db migrate```

```flask db upgrade```

This will create all the tables on the RDBMS you chose and allow the app to function properly. 

The next step is to setup the admin user. To do this, run the following command being sure to change the username, password, and email to the desired settings.

```flask initial_setup --username admin --password somepassword --email desired@email.com```

## Running the tests

At this point you can also run the tests to make sure everything is setup correctly. To do this, run:

````flask test````

## Deploying the app

To run the app in debug mode, you can simply run:

```flask run```

and the app will run on the debug server listening on port 5000 by default. You can test this by going to the IP address (or hostname) of your server or on localhost in your browser.

> Ex: http://localhost:5000

This is good for testing but not suitable for a production environment. The default flask server is only single threaded as well.

The authenticate app is configured to be run behind a webserver (such as NGINX) using WSGI as a bridge between the server and the app. To do this you will want to run the app using Gunicorn to be able to handle multiple requests and set it up behind your webserver.

Running the app with gunicorn is a different command. 

```gunicorn --pythonpath 'app' authenticate.app:create_app\(\) -b 0.0.0.0:$PORT -w 3 ```

The $PORT variable can either be set directly, or it can be setup as an environment variable as described above. The settings shown here will spawn 3 workers which is recommended for a 2-core CPU. 

It is also recommended that this command be spawned by a process monitoring service such as Supervisor which was mentioned earlier.

The next step is to configure NGINX to pass on requests to the app when necessary. 

For basic information on how to do this, please reference the following guide: https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-14-04


# Using the App

When using access_control for user authentication, please always be sure to verify with this service before modifying your data to make sure that the user in question has the appropriate permissions on the scope in question.
