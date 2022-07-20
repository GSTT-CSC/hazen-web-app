Installation
=============
.. attention:: These guidelines are written for developers to install *hazen-web-app* on MacOS or Linux and are a work in progress!

For both MacOS and Linux machines, installation of *hazen-web-app* requires Python 3.8 or above and `pip`.
The following steps will apply to both machines, with any differences noted in the steps themselves.

PostgreSQL
^^^^^^^^^^^^^^^^^^^^^^
For MacOS, install PostgreSQL either through the `Postgres.app website <https://postgresapp.com/>`_ or using Homebrew in the Terminal:

.. code-block:: bash
   :linenos:

   brew update
   brew install postgresql

For Ubuntu-based Linux distros, install PostgreSQL through the `PostgreSQL website <https://www.postgresql.org/download/linux/ubuntu/>`_.

During the installation, a default superuser will be created and so, to create and access databases, additional users can be created by following the steps outlined `here <https://kb.objectrocket.com/postgresql/how-to-create-a-role-in-postgres-1454>`_. At this stage, you can create a new database called **hazen** using PostgreSQL SQL commands or use Postico, if applicable (see below).


.. note::
   Confirm PostgreSQL is running before moving onto the next step.

Postico & Beekeeper Studio
^^^^^^^^^^^^^^^^^^^^^^^^^^
For MacOS, install Postico through the `official website <https://eggerapps.at/postico/>`_ and create a new connection (see **New Favourite**) with the following details:

.. list-table:: Title
   :widths: 25 25
   :header-rows: 1

   * - Detail
     - Value
   * - Nickname
     - hazen
   * - Host
     - localhost
   * - Port
     - 5432

For Linux, install Beekeeper Studio through the `office website <https://docs.beekeeperstudio.io/installation/#linux-installation>`_

.. note::
   If using Postico, ensure you have pressed **Connect** before moving onto the next step.

Lastly, if you haven't already, create a new database called **hazen**. The required tables will be created and written to the connection in later steps.

RabbitMQ
^^^^^^^^
Install RabbitMQ using `Homebrew <https://www.rabbitmq.com/install-homebrew.html>`_ in the Terminal:

.. code-block:: bash
   :linenos:

   brew update
   brew install rabbitmq

Next, add the RabbitMQ binary files to your system PATH.

.. note::
   The location of these files varies depending on your system, so you will need `identify where they are <https://www.rabbitmq.com/relocate.html>`_ before moving on to the next step.

Once you have confirmed their location, update **either** your .bashrc **or** .zshrc to include the RabbitMQ binary files:

.. code-block:: zsh
   :linenos:

   # .zshrc
   export PATH=$PATH:/usr/local/sbin
   source ~/.zshrc

.. code-block:: bash
   :linenos:

   # .bashrc
   export PATH=$PATH:/usr/local/sbin
   source ~/.bashrc

hazen-web-app
^^^^^^^^^^^^^
.. tip:: We recommend `creating and using a new virtual environment <https://docs.python.org/3/library/venv.html>`_ for your use of *hazen*.

Clone the `hazen-web-app <https://github.com/GSTT-CSC/hazen-web-app>`_ repository:

.. code-block:: bash
   :linenos:

   git clone https://github.com/GSTT-CSC/hazen-web-app.git

If you have not yet created a virtual environment, we recommend you do so now:

.. code-block:: bash
   :linenos:

   python -m venv hazen-web-app
   source hazen-web-app/bin/activate

.. note:: If you get an error when running the above command, you may need to use ``python3`` rather than ``python``.

Once you have activated your virtual environment, ``cd`` into the project folder and install the required packages:

.. code-block:: bash
   :linenos:

   pip install -r requirements.txt

This will create the tables required for the application in your *hazen* database, which you can view in either Postico or Beekeeper Studio.

.. note:: For MacOS, the next few steps are required to run *hazen-web-app* locally for development and testing purposes, specifically opening multiple Terminal windows.

          For Linux, only PostgreSQL and the ``hazen.py`` need to run. The username and password for the PostgreSQL user created at installation may be added to Line 7 in ``config.py`` in the following format: ``postgresql://username:password@localhost:5432/hazen``.


RabbitMQ
^^^^^^^^
Open a new Terminal window and run:

.. code-block:: bash
   :linenos:

   rabbitmq-server start

Check RabbitMQ is running in your `web browser <http://localhost:15672/>`_.

.. note:: Default RabbitMQ credentials should be ``guest`` for both the username and password.

Celery
^^^^^^
Open a new Terminal window and run:

.. code-block:: shell
   :linenos:

   celery -A hazen.worker worker

Run
^^^^
Open a new Terminal window and run:

.. code-block:: python
   :linenos:

   python hazen.py


Open a web browser and use the hazen-web-app at the provided address in the ``config.py``, such as that on `port 5432 <https://localhost:5432>`_.

.. warning:: If you are using port 5000 (see Line 7 in ``config.py``) on `macOS Monterey <https://progressstory.com/tech/port-5000-already-in-use-macos-monterey-issue/>`_, you will need to either:

             * Go to **System Preferences > Sharing** and untick **AirPlay Receiver**
             * Update the port being used in Line 7 in ``config.py``

Troubleshooting
^^^^^^^^^^^^^^^
.. tip:: If any of the required packages error out, try installing the problematic packages one by one.
         For example, on Linux, the ``psycopg2`` package should be renamed to ``psycopg2-binary`` to be installed.