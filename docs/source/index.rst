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

The |hazen-web-app|_ is an interactive web-based implementation of |hazen|_.

.. _hazen: https://github.com/GSTT-CSC/hazen/

.. |hazen| replace:: *hazen*

.. _hazen-web-app: https://github.com/GSTT-CSC/hazen-web-app

.. |hazen-web-app| replace:: *hazen-web-app*

Currently, the |hazen-web-app|_ requires manual installation of the following software:

- `PostgreSQL <https://www.postgresql.org/download/>`_
- `Postico <https://eggerapps.at/postico/>`_ (MacOS) or  `Beekeeper Studio <https://www.beekeeperstudio.io/>`_ (Linux)
- `RabbitMQ <https://www.rabbitmq.com/>`_
- `hazen-web-app <https://github.com/GSTT-CSC/hazen-web-app>`_

We use PostgreSQL as the underlying database software, RabbitMQ as the message broker (used in conjunction with `Celery <https://docs.celeryq.dev/en/stable/>`_ for communication between the app and browser), and Postico/Beekeeper Studio for easy viewing of the databases. For a step-by-step guide, please refer to the Install page.

We are currently working on migrating the |hazen-web-app|_ to be hosted on `Heroku <https://www.heroku.com/>`_, which will remove the need for users to install the application on their local machines.

Table of Contents
=================

.. toctree::
   :maxdepth: 1
   :caption: Getting Started

   install
   tasks

.. toctree::
   :maxdepth: 1
   :caption: Modules

   web/modules.rst
   library/modules.rst

.. toctree::
   :maxdepth: 1
   :caption: Get Involved

   contributors