# hazen-web-app

The hazen-web-app is an interactive web-based implementation of the [hazen](https://github.com/GSTT-CSC/hazen) Python package, available as a command line tool on [pip](https://pypi.org/project/hazen/).

**These guidelines are written for developers to install hazen-web-app on MacOS or Ubuntu and are a work in progress!**

The hazen-web-app **requires** manual installation of the following software:
- Postgres: database software for storing user data, acquisition data, etc.
  - Postico (MacOS) or Beekeeper Studio (Linux) recommended for viewing databases
- RabbitMQ: message broker used in conjunction with Celery to communicate between the app and web browser
- hazen-web-app (i.e.: this repo) - requires Python3.8 or above and `pip`


## Table of Contents
- Setting up for the first time
  - [on MacOs](#setup-on-macos)
  - [on Linux](#setup-on-linux-ubuntu)
- Running locally
  - [how to make and test code changes](#how-to-make-and-test-code-changes)
  - [using docker compose](#setup-using-docker-compose)
- Contributing to development and documentation
  - [process for contributing](#process-for-contributing)
  - [update documentation](#update-documentation)
  - Release Process - to be devised


## Setup on MacOS

### Database - Postgres & Postico

1. Installation via Homebrew is recommended, instructions at [Postgres wiki](https://wiki.postgresql.org/wiki/Homebrew),
or see the official [Postgres.app](https://postgresapp.com/) installation instructions.

In Terminal:
```shell
brew update
# Install postgresql
brew install postgresql
brew services start postgresql

# you can also stop and restart the postgres service
brew services stop postgresql
brew services restart postgresql
```

2. Create a new database with the following details:
*Confirm PostgreSQL is running before moving onto the next step.*
You can do this by opening the Postgres.app, or if you prefer to use Terminal you can start it following the instructions [here](https://sourabhbajaj.com/mac-setup/PostgreSQL/).
Download [Postico](https://eggerapps.at/postico/) or any other graphical interface compatible with databases.

- Create a **New Favourite** with:
  - Nickname = hazen
  - Host = localhost
  - Port = 5432
- Press **Connect**
- Create a new database called `hazen`

### Message broker - RabbitMQ
Official MacOS installation instructions using Homebrew can be found [here](https://www.rabbitmq.com/install-homebrew.html).

In Terminal:
```shell
# Install rabbitmq
brew install rabbitmq

brew services start rabbitmq

# you can also stop and restart the rabbitmq service
brew services stop rabbitmq
brew services restart rabbitmq
```

ONLY if you don't want the RabbitMQ service to be running in the background at all times, you may start and stop it manually each time before using it:
For this, you need to add the RabbitMQ binary files to the system PATH. The location of these files varies depending on your system, so we need to find them first.
```shell
# Find RabbitMQ binary files if installed via Homebrew
brew info rabbitmq

# The output will have a line like
# CONF_ENV_FILE="/opt/homebrew/etc/rabbitmq/rabbitmq-env.conf" /opt/homebrew/opt/rabbitmq/sbin/rabbitmq-server

# Update either your .bashrc or .zshrc to include the RabbitMQ binary files:
# .zshrc
export PATH=$PATH:/usr/local/sbin
source ~/.zshrc

# .bashrc
export PATH=$PATH:/usr/local/sbin
source ~/.bashrc
```

### hazen-web-app

Clone this repository, create new virtual environment and install dependencies:
```shell
# clone repo
git clone https://github.com/GSTT-CSC/hazen-web-app.git

# create new venv
# you may choose any folder to store files for the virtual environment
python -m venv hazen-web-app
source hazen-web-app/bin/activate

# install dependencies
cd hazen-web-app
pip install -r requirements.txt
```

## Setup on Linux (Ubuntu)

### Database - Postgres & Beekeeper Studio

Official PostgreSQL installation instructions for Ubuntu-based Linux distros: [PostgreSQL installation](https://www.postgresql.org/download/linux/ubuntu/).
A default superuser is created during the installation. To create and access databases, additional users can be created by following the steps outlined [here](https://kb.objectrocket.com/postgresql/how-to-create-a-role-in-postgres-1454).
Create a new database called `hazen`.

Official Beekeeper Studio installation instructions for Ubuntu-based Linux distros: [Beekeeper Studio installation](https://docs.beekeeperstudio.io/installation/#linux-installation)

### Message broker - RabbitMQ

Official RabbitMQ installation instructions for Ubuntu-based Linux distros: [RabbitMQ installation](https://www.rabbitmq.com/install-debian.html)
Essentially the following command is sufficient:
`sudo apt-get install rabbitmq-server`

### hazen-web-app

Follow instructions above to clone the hazen-web-app repo and install the required Python packages.

#### Troubleshooting tips
On Linux, the `psycopg2` package should be renamed to `psycopg2-binary` to be installed.
If any of the required packages error out, try installing the problematic packages one by one.
The username and password for the Postgres user created at installation may need to be added to the config.py on L7 in the following format: `postgresql://username:password@localhost:5432/hazen`


## Setup using docker compose
Make sure that Docker and `docker compose` are installed and set up correctly.

Clone the repo, create an .env file with config variables and start the web-app:
1. Create .env file and read variables. Can reuse default.env for testing or recommend creating your own in production.
```shell
# clone repo
git clone https://github.com/GSTT-CSC/hazen-web-app.git

mv default.env .env
source .env

docker compose up -d --build
```

The hazen web app is then accessible on port 8080.

## How to make and test code changes

The following instructions explain how to run hazen-web-app locally for development and testing purposes.

Running hazen-web-app requires multiple Terminal windows.

### Open Postgres database & view using Postico
In the Applications folder on MacOS:
- Open Postgres.app
- Open Postico

You should be able to use Postico to view a PostgresSQL database called `hazen`.

### Start RabbitMQ
Open a new terminal window and run:

```shell
# start RabbitMQ:
rabbitmq-server start
```

Check RabbitMQ is running in your web browser: [http://localhost:15672/](http://localhost:15672/). Default RabbitMQ credentials should be:
- Username = guest
- Password = guest

### Start Celery
Open a new terminal window and run:

```shell
# start Celery:
celery -A hazen.worker worker
```

### Run hazen-web-app
Open a new terminal window. Ensure you are running your `hazen-web-app` venv and run:
```shell 
python hazen.py
```

Open a web browser and use the hazen-web-app at the provided address, typically: [http://localhost:5000](http://localhost:5000).

## Process for contributing

Follow these steps to make a contribution to the hazen web-app:

1. Check the current [Issues](https://github.com/GSTT-CSC/hazen-web-app/issues) to see if an Issue already exists for your 
contribution.
2. If there is no existing Issue, create a new Issue for your contribution:
   - Select the `Bug report` or `Feature request` template
   - Fill in the Issue according to the template
   - Add relevant Labels to the issue: eg `Enhancement`, `Bug`, `frontend`, `database`, etc
3. Create a new branch from `main`
   - Name the branch with the issue number and a short description, e.g.: `123-snr-bugfix`
4. Make and test your code changes (see guidance above)
5. Perform unit tests on your machine: `pytest tests/`
6. Create a [Pull Request](https://github.com/GSTT-CSC/hazen-web-app/pulls) (PR)
   - Describe your changes
   - Describe why you coded your change this way
   - Describe any shortcomings or work still to do
   - Cross-reference any relevant Issues
7. One of the development team members will review your PR and then:
   - Ask questions
   - Request any changes
   - Once all of the above is resolved, MERGE into `main` – *thank you and congratulations on contributing to hazen web-app!*

## Update Documentation

Create rst files describing the structure of the hazen Python Package
```
# in an active hazen virtual environment in the root of the project
# the command below specifies that sphinx should look for scripts in the hazenlib folder
# and output rst files into the docs/source folder
sphinx-apidoc -o docs/source hazenlib

# next, from within the docs/ folder
cd docs/
# create/update the html files for the documentation
make html  -f Makefile
# opening the docs/source/index.html in a web browser allows a preview of the generated docs
```


*Note: [If you are using macOS Monterey](https://progressstory.com/tech/port-5000-already-in-use-macos-monterey-issue/), you will need go to **System Preferences > Sharing** and untick **AirPlay Receiver** in order to use port 5000.*

<p align="center" width="100%">
     <img width="663" alt="image" src="https://user-images.githubusercontent.com/67117138/167840022-25d838b9-950d-44cd-a30b-a916bd3c7eb0.png">
</p>


## Deployment on Heroku

- Instructions TBC
