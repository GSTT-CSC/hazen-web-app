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
*Confirm PostgreSQL is running before moving onto the next step.* You can do this by opening the Postgres.app, 
or if you prefer to use Terminal you can start it following the instructions [here](https://sourabhbajaj.com/mac-setup/PostgreSQL/).

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

## Setup on Windows 

### Postgres

Official Postgres instalation instructions for Windows can be found here:  [https://www.enterprisedb.com/downloads/postgres-postgresql-downloads](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads)

Unfortunately Postico doesn't work for Windows. An alternative is **DBeaver** [https://alternativeto.net/software/dbeaver/about/](https://alternativeto.net/software/dbeaver/about/)  although it is not essential for working with the app.

Open pgAdmin and create a database called hazen, ensure it is on port 5432. You may be asked to create a password. 

#### Troubleshooting tips:
The username and password for the Postgres user created at installation may need to be added to the `config.py` on L33 in the following format: `postgresql://username:password@localhost:5432/hazen`

### RabbitMQ

For windows, ERLANG must be downloaded before RabbitMQ, this can be done using the following link: [https://www.erlang.org/downloads](https://www.erlang.org/downloads).

RabbitMQ can then be installed using this link: [https://www.rabbitmq.com/docs/install-windows](https://www.rabbitmq.com/docs/install-windows)

Using powershell with admin privileges go to path where RabbitMQ is installed ( example C:\Program Files\RabbitMQ Server\rabbitmq_server-3.12.12\sbin). 

```Shell
#example:
cd\
cd 'Program Files'
cd 'RabbitMQ Server'
cd  rabbitmq_server-3.12.12\sbin 
```
Make sure that RabbitMQ is running Type in Task Manager, if it is not then run the following

```shell 
 .\rabbitmq-server start
```

Open the browser and navigate to [http://localhost:15672](http://localhost:15672).
Use the standard user and password:
- Username = guest
- Password = guest

#### Troubleshooting:

If the following message: `ERLANG_HOME not set correctly` is displayed when trying to enable RabbitMQ Management Plugins please type following on powershell:

```shell
$env:ERLANG_HOME = "$env:ProgramFiles\Erlang OTP"
$env:ERTS_HOME = "$env:ProgramFiles\Erlang OTP\erts-13.2.2"
$env:RABBITMQ_HOME = "$env:Program Files\RabbitMQ Server\rabbitmq_server-3.12.12"
$env:PATH += ";$env:ERLANG_HOME\bin;$env:ERTS_HOME\bin;$env:RABBITMQ_HOME\sbin"
```

Open another terminal and navigate to the RabbitMQ location. Run the following code to restart RabbitMQ:

```shell
.\rabbitmq-service stop 
.\rabbitmq-service remove
.\rabbitmq-plugins enable rabbitmq_management --offline
.\rabbitmq-service install
.\rabbitmq-service start
```

**Make sure to replace the file locations with the ones matching your ones.**

Further guidance can be found here: [https://gateway.sdl.com/apex/communityknowledge?articleName=000019802](https://gateway.sdl.com/apex/communityknowledge?articleName=000019802).

### Clone and Run hazen-web-app
Clone this repository, create new venv and install:

Suggestion: For simplicuty and the following code to work without modifying paths:
1. Create a folder called Hazen-app 
2. Run the following. The following code creates a folder called `hazen-web-app` with the cloned repository and another folder called `hazen-web-app-venv` with the virtual environment.

**You might need to create a copy of `requirements.txt` in the virtual environment folder (in this case `hazen-web-app-venv`) depending on how your paths are defined.**

```shell
cd Hazen-app
git clone https://github.com/GSTT-CSC/hazen-web-app.git 

# create new venv

python -m venv hazen-web-app-venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\hazen-web-app-venv\Scripts\Activate

# install hazen-web-app requirements 
cd hazen-web-app-venv #must dowload the packages in the virtual environment
pip install -r requirements.txt
```

*Note: For troubleshooting look here: [https://github.com/GSTT-CSC/hazen/blob/main/CONTRIBUTING.md](https://github.com/GSTT-CSC/hazen/blob/main/CONTRIBUTING.md).* 


## Run app on Windows

1. Ensure **RabbitMQ** is running. To check:

- Open the browser and navigate to [http://localhost:15672]
- Open Task Manager and check

2. Open a terminal, **run the hazen-app**, make sure the virtual environment is active

```shell 
#you should be in Hazen-app folder
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\hazen-web-app-venv\Scripts\Activate
cd hazen-web-app
python hazen.py

```

Open a web browser and use the hazen-web-app at the provided address, typically: [http://localhost:5000].
You can now create new log-in/ registration details.

Note: This code assummes that you have created the folders as reccomended below. If this is not the case instead use:
```shell

 Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
 .\full_path_to_vitual_environment_folder\Scripts\Activate
 cd full_path_to_cloned_repository_folder
 python hazen.py
 ```

3. Open another terminal - keep the python one open - and run Celery 

```Shell
#you should be in Hazen-app folder
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\hazen-web-app-venv\Scripts\Activate
cd hazen-web-app
celery -A hazen.worker worker -l INFO -P solo
 ```

Note: This code assummes that you have created the folders as reccomended below. If this is not the case instead use:
```shell

 Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
 .\full_path_to_vitual_environment_folder\Scripts\Activate
 cd full_path_to_cloned_repository_folder
 celery -A hazen.worker worker -l INFO -P solo
 
 ```
 #### Celery Troubleshooting:

 Sometimes the celery logging will get confused with the hazen log and won't allow tasks to be performed in the app `Logging error` due to `Permission errors`.
 One way arround this is to remove celery logging by deletting L92-97 in `init.py`.