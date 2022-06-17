.. hazen documentation master file, created by
   sphinx-quickstart on Fri Jun 17 11:24:37 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to hazen's documentation!
=================================
*hazen* is a software framework for performing automated analysis of magnetic resonance imaging (MRI) Quality Assurance data.

It provides automatic quantitative analysis for the following measurements of MRI phantom data:

- Signal-to-noise ratio (SNR)
- Spatial resolution
- Slice position and width
- Uniformity
- Ghosting
- MR Relaxometry

The hazen-web-app is an interactive web-based implementation of `hazen <https://github.com/GSTT-CSC/hazen/>`_.

.. attention:: These guidelines are written for developers to install hazen-web-app on MacOS and are a work in progress!

Install
~~~~~~~~~~~~
The hazen-web-app requires manual installation of the following software:

- `PostgreSQL <https://www.postgresql.org/download/>`_
- `Postico <https://eggerapps.at/postico/>`_
- `RabbitMQ <https://www.rabbitmq.com/>`_
- `hazen-web-app <https://github.com/GSTT-CSC/hazen-web-app>`_

We use PostgreSQL as the underlying database software, RabbitMQ as the message broker (used in conjunction with `Celery <https://docs.celeryq.dev/en/stable/>`_ for communication between the app and browser), and Postico for easy viewing of the databases.


Getting Started
~~~~~~~~~~~~~~~~

Roadmap
~~~~~~~~~~~~

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
