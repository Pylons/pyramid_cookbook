Logging Exceptions To Your SQLAlchemy Database
----------------------------------------------

So you'd like to log to your database, rather than a file. Well, here's
a brief rundown of exactly how you'd do that.

First we need to define a Log model for SQLAlchemy (do this in
``myapp.models``)::

   from sqlalchemy import Column
   from sqlalchemy.types import DateTime, Integer, String
   from sqlalchemy.sql import func
   from sqlalchemy.ext.declarative import declarative_base

   Base = declarative_base()
   
   class Log(Base):
       __tablename__ = 'logs'
       id = Column(Integer, primary_key=True) # auto incrementing
       logger = Column(String) # the name of the logger. (e.g. myapp.views)
       level = Column(String) # info, debug, or error?
       trace = Column(String) # the full traceback printout
       msg = Column(String) # any custom log you may have included
       created_at = Column(DateTime, default=func.now()) # the current timestamp

       def __init__(self, logger=None, level=None, trace=None, msg=None):
           self.logger = logger
           self.level = level
           self.trace = trace
           self.msg = msg

       def __unicode__(self):
           return self.__repr__()

       def __repr__(self):
           return "<Log: %s - %s>" % (self.created_at.strftime('%m/%d/%Y-%H:%M:%S'), self.msg[:50])

Not too much exciting is occuring here. We've simply created a
new table named 'logs'.

Before we get into how we use this table for good, here's a quick review
of how ``logging`` works in a script::
   
   # http://docs.python.org/howto/logging.html#configuring-logging
   import logging
   
   # create logger
   logger = logging.getLogger('simple_example')
   logger.setLevel(logging.DEBUG)
   
   # create console handler and set level to debug
   ch = logging.StreamHandler()
   ch.setLevel(logging.DEBUG)
   
   # create formatter
   formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
   
   # add formatter to ch
   ch.setFormatter(formatter)
   
   # add ch to logger
   logger.addHandler(ch)
   
   # 'application' code
   logger.debug('debug message')
   logger.info('info message')
   logger.warn('warn message')
   logger.error('error message')
   logger.critical('critical message')

What you should gain from the above intro is that your ``handler``
uses a ``formatter`` and does the heavy lifting of executing the
output of the ``logging.LogRecord``. The output actually comes
from ``logging.Handler.emit``, a method we will now override as
we create our SQLAlchemyHandler.

Let's subclass Handler now (put this in ``myapp.handlers``)::

   import logging
   import traceback
   
   import transaction
   
   from models import Log, DBSession
   
   class SQLAlchemyHandler(logging.Handler):
       # A very basic logger that commits a LogRecord to the SQL Db
       def emit(self, record):
           trace = None
           exc = record.__dict__['exc_info']
           if exc:
               trace = traceback.format_exc(exc)
           log = Log(
               logger=record.__dict__['name'],
               level=record.__dict__['levelname'],
               trace=trace,
               msg=record.__dict__['msg'],)
           DBSession.add(log)
           transaction.commit()
    
For a little more depth, ``logging.LogRecord``, for which ``record``
is an instance, contains all it's nifty log information in it's
``__dict__`` attribute.

Now, we need to add this logging handler to our .ini configuration files.
Before we add this, our production.ini file should contain something like:

.. code-block:: ini
   :linenos:

   [loggers]
   keys = root, myapp, sqlalchemy
   
   [handlers]
   keys = console
   
   [formatters]
   keys = generic
   
   [logger_root]
   level = WARN
   handlers = console
   
   [logger_myapp]
   level = WARN
   handlers =
   qualname = myapp
   
   [logger_sqlalchemy]
   level = WARN
   handlers =
   qualname = sqlalchemy.engine
   # "level = INFO" logs SQL queries.
   # "level = DEBUG" logs SQL queries and results.
   # "level = WARN" logs neither.  (Recommended for production systems.)
   
   [handler_console]
   class = StreamHandler
   args = (sys.stderr,)
   level = NOTSET
   formatter = generic
   
   [formatter_generic]
   format = %(asctime)s %(levelname)-5.5s [%(name)s][%(threadName)s] %(message)s
   
We must add our ``SQLAlchemyHandler`` to the mix. So make the following
changes to your production.ini file.

.. code-block:: ini
   :linenos:

   [handlers]
   keys = console, sqlalchemy
   
   [logger_myapp]
   level = DEBUG
   handlers = sqlalchemy
   qualname = myapp

   [handler_sqlalchemy]
   class = myapp.handlers.SQLAlchemyHandler
   args = ()
   level = NOTSET
   formatter = generic

The changes we made simply allow Paster to recognize a new handler -
``sqlalchemy``, located at ``[handler_sqlalchemy]``. Most everything
else about this configuration should be straightforward. If anything
is still baffling, then use this as a good opportunity to read the 
Python ``logging`` documentation.

Below is an example of how you might use the logger in ``myapp.views``::

   import logging
   from pyramid.view import view_config
   from pyramid.response import Response

   log = logging.getLogger(__name__)

   @view_config(route_name='home')
   def root(request):
       log.debug('exception impending!')
       try:
           1/0
       except:
           log.exception('1/0 error')
       log.info('test complete')
       return Response("test complete!")

When this view code is executed, you'll see up to three (depending
on the level of logging you allow in your configuation file) records!

For more power, match this up with pyramid_exclog at
http://docs.pylonsproject.org/projects/pyramid_exclog/en/latest/

