Pyramid Quick Tutorial
======================

This tutorial is intended to give you a quick overview of the Pyramid Web 
Application Framework. Because Pyramid has few opinions on how to 
organize and develop your application, this tutorial focus on a minimal 
approach with common idioms to get a feel of basic Pyramid patterns. While 
those idioms and patterns are common, it is not suited to use this minimal 
approach to create a full fledged application, read more advanced tutorials 
for this purpose.

Here's what you'll get at the end of the tutorial, a minimal application to 
view, insert and close tasks, backed by an SQLite database for storing your 
data, presented by mako to render your views and using the routes pattern to 
match your URLs to code functions.

.. image:: pyramid_quick_tutorial.png

Organizing The Project
----------------------

Before getting started, create the directory hierarchy needed for the 
application layout:

.. code-block:: text

    /tasks
        /static
        /templates

The tasks directory created will not be used as a python package, it'll just 
serves as a container to put and organize our project files.

Database And Schema
-------------------

To make things simple and straightforward we'll use the widely installed 
SQLite database for our project. The schema for our tasks is also simple, 
an id to uniquely identify the task, a name not longer than 100 characters 
and a closed boolean to indicate if the task is closed or not.

Add to the tasks directory a file named schema.sql with the following content:

.. code-block:: sql

    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name CHAR(100) NOT NULL,
        closed BOOL NOT NULL
    );
    
    INSERT OR IGNORE INTO tasks (id, name, closed) VALUES (1, 'Start learning Pyramid', 0);
    INSERT OR IGNORE INTO tasks (id, name, closed) VALUES (2, 'Do quick tutorial', 0);
    INSERT OR IGNORE INTO tasks (id, name, closed) VALUES (3, 'Have some beer!', 0);

Application Setup
-----------------

text

Creating The Database
---------------------

text

Making The Database Available
-----------------------------

text

Routes And Views Functions
--------------------------

text

View Templates
--------------

text

Styling Your Templates
----------------------

text

