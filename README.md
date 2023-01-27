# hazen-web-app

The hazen-web-app is an interactive web-based implementation of [hazen](https://github.com/GSTT-CSC/hazen).

**These guidelines are written for developers to install hazen-web-app on MacOS or Ubuntu and are a work in progress!**

The hazen-web-app **requires** manual installation of the following software:
- Postgres: database software for storing user data, acquisition data, etc.
  - Postico (MacOS) or Beekeeper Studio (Linux) recommended for viewing databases
- RabbitMQ: message broker used in conjunction with Celery to communicate between the app and web browser
- hazen-web-app (i.e.: this repo) - requires Python3.8 or above and `pip`


## Setup using docker compose
To start the application:
1. Create .env file and read variables. Can reuse default.env for testing or recommend creating your own in production.
```
mv default.env .env
source .env
```

2. Start web app
```
docker compose up -d --build
```

The hazen web app is then accessible on port 8080

## Setup on MacOS

### Postgres & Postico

Official Postgres.app installation instructions: [Postgres.app](https://postgresapp.com/). Can also be installed using Homebrew.

In Terminal:
```shell
brew update
brew install postgresql
```
*Confirm PostgreSQL is running before moving onto the next step.*

Download [Postico](https://eggerapps.at/postico/).
- Create a **New Favourite** with:
  - Nickname = hazen
  - Host = localhost
  - Port = 5432
- Press **Connect**
- Create a new database called `hazen`

### RabbitMQ
Official MacOS installation instructions using Homebrew found [here](https://www.rabbitmq.com/install-homebrew.html).

In Terminal:
```shell
# Install rabbitmq
brew update
brew install rabbitmq
```

Next, we need to add the RabbitMQ binary files to our system PATH. The location of these files varies depending on your 
system, so we need to find them first.
```shell
# Find RabbitMQ binary files

```

Update **either** your .bashrc **or** .zshrc to include the RabbitMQ binary files:
```shell
# .zshrc
export PATH=$PATH:/usr/local/sbin
source ~/.zshrc

# .bashrc
export PATH=$PATH:/usr/local/sbin
source ~/.bashrc
```

### hazen-web-app

Clone this repository, create new venv and install:
```shell
# clone repo
git clone https://github.com/GSTT-CSC/hazen-web-app.git

# create new venv
python -m venv hazen-web-app
source hazen-web-app/bin/activate

# install hazen-web-app
cd hazen-web-app
pip install -r requirements.txt
```

## Setup on Linux (Ubuntu)

### Postgres & Beekeeper Studio

Official PostgreSQL installation instructions for Ubuntu-based Linux distros: [PostgreSQL installation](https://www.postgresql.org/download/linux/ubuntu/).
A default superuser is created during the installation. To create and access databases, additional users can be created by following the steps outlined [here](https://kb.objectrocket.com/postgresql/how-to-create-a-role-in-postgres-1454).
Create a new database called `hazen`.

Official Beekeeper Studio installation instructions for Ubuntu-based Linux distros: [Beekeeper Studio installation](https://docs.beekeeperstudio.io/installation/#linux-installation)

### RabbitMQ

Official RabbitMQ installation instructions for Ubuntu-based Linux distros: [RabbitMQ installation](https://www.rabbitmq.com/install-debian.html)
Essentially the following command is sufficient:
`sudo apt-get install rabbitmq-server`

### hazen-web-app

Follow instructions above to clone the hazen-web-app repo and install required Python packages.

#### Troubleshooting tips
On Linux, the `psycopg2` package should be renamed to `psycopg2-binary` to be installed.
If any of the required packages error out, try installing the problematic packages one by one.
The username and password for the Postgres user created at installation may need to be added to the config.py on L7 in the following format: `postgresql://username:password@localhost:5432/hazen`

## Run

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

*Note: [If you are using macOS Monterey](https://progressstory.com/tech/port-5000-already-in-use-macos-monterey-issue/), you will need go to **System Preferences > Sharing** and untick **AirPlay Receiver** in order to use port 5000.*

<p align="center" width="100%">
     <img width="663" alt="image" src="https://user-images.githubusercontent.com/67117138/167840022-25d838b9-950d-44cd-a30b-a916bd3c7eb0.png">
</p>


## Deployment on Heroku

- Instructions TBC
