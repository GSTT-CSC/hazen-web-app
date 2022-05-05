# hazen-web-app

The hazen-web-app is an interactive web-based implementation of [hazen](https://github.com/GSTT-CSC/hazen).

**These guidelines are written for developers to install hazen-web-app on MacOS and are a work in progress!**


## Setup

The hazen-web-app **requires** manual installation of the following software:
- Postgres: database software for storing user data, acquisition data, etc.
  - Postico recommended for viewing databases
- RabbitMQ: message broker used in conjunction with Celery to communicate between the app and web browser
- hazen-web-app (i.e.: this repo)

### Postgres & Postico

Official Postgres.app installation instructions: [Postgres.app](https://postgresapp.com/). Can also be installed using Homebrew.

In Terminal:
```shell
brew update
brew install postgresql
```

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

## Deployment on Heroku

- Instructions TBC