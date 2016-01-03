Models
++++++

Models are essentially the same in Pyramid and Pylons because the framework
is only minimally involved with the model unlike, say, Django where the ORM
(object-relational mapper) is framework-specific and other parts of the
framework assume it's that specific kind. In Pyramid and Pylons, the
application skeleton merely suggests where to put the models and initializes a
SQLAlchemy database connection for you. Here's the
default Pyramid configuration (comments stripped and imports squashed):

.. literalinclude:: code/models.py
   :linenos:

and its INI files:

.. literalinclude:: code/model_development.ini
   :linenos:

It has the following differences from Pylons:

1. ZopeTransactionExtension and the "pyramid_tm" tween.
2. "models" (plural) instead of "model" (singular).
3. A module rather than a subpackage.
4. "DBSession" instead of "Session".
5. No init_model() function.
6. Slightly different import style and variable naming.

Only the first one is an essential difference; the rest are just aesthetic
programming styles.  So you can change them without harming anything.

The model-models difference is due to an ambiguity in how the word "model" is
used. Some people say "a model" to refer to an individual ORM class, while
others say "the model" to refer to the entire collection of ORM classes in an
application. This guide uses the word both ways.

What belongs in the model?
==========================

Good programming practice recommends keeping your data classes separate from
user-interface classes. That way the user interface can change without
affecting the data and vice-versa. The model is where the data classes go.
For instance, a Monopoly game has players, a board, squares, title deeds,
cards, etc, so a Monopoly program would likely have classes for each of these.
If the application requires saving data between runs (persistence), the data
will have to be stored in a database or equivalent. Pyramid can work with a
variety of database types: SQL database, object database, key-value database
("NoSQL"), document database (JSON or XML), CSV files, etc. The most common
choice is SQLAlchemy, so that's the first configuration provided by Pyramid and
Pylons.

At minimum you should define your ORM classes in the model. You can also add
any business logic in the form of functions, class methods, or regular methods.
It's sometimes difficult to tell whether a particular piece of code belongs in
the model or the view, but we'll leave that up to you. 

Another principle is that the model should not depend on the rest of the
application so that it can be used on its own; e.g., in utility programs or in
other applications. That also allows you to extract the data if the framework
or application breaks. So the view knows about the model but not vice-versa. Not
everybody agrees with this but it's a good place to start.

Larger projects may share a common model between multiple web applications and
non-web programs. In that case it makes sense to put the model in a separate
top-level package and import it into the Pyramid application.

Transaction manger
==================

Pylons has never used a transaction manager but it's common in TurboGears and
Zope. A transaction manager takes care of the commit-rollback cycle for you.
The database session in both applications above is a *scoped* session, meaning
it's a threadlocal global and must be cleared out at the end of every request.
The Pylons app has special code in the base controller to clear out the
session. A transaction manager takes this a step further by committing any
changes made during the request, or if an exception was raised during the
request, it rolls back the changes. The ZopeTransactionExtension provides a
module-level API in case the view wants to customize when/whether committing
occurs.

The upshot is that your view method does not have to call
``DBSession.commit()``: the transaction manager will do it for you. Also, it doesn't
have to put the changes in a try-except block because the transaction manager
will call ``DBSession.rollback()`` if an exception occurs. (Many Pylons actions don't
do this so they're technically incorrect.) A side effect is that you *cannot*
call ``DBSession.commit()`` or ``DBSession.rollback()`` directly. If you want
to precisely control when something is committed, you'll have to do it this way::

    import transaction

    transaction.commit()
    # Or:
    transaction.rollback()

There's also a ``transaction.doom()`` function which you can call to prevent
*any* database writes during this request, including those performed by
other parts of the application. Of course, this doesn't affect changes that
have already been committed.

You can customize the circumstances under which an automatic rollback occurs by
defining a "commit veto" function. This is described in the pyramid_tm
documentation.

Using traversal as a model
==========================

Pylons doesn't have a traversal mode, so you have to fetch database objects in
the view code. Pyramid's traversal mode essentially does this for you,
delivering the object to the view as its *context*, and handling "not found"
for you. Traversal resource tree thus almost looks like a second kind of model,
separate from ``models``. (It's typically defined in a ``resources`` module.)
This raises the question of, what's the difference between the two?  Does it
make sense to convert my model to traversal, or to traversal under the control
of a route?  The issue comes up further with authorization, because Pyramid's
default authorization mechanism is designed for permissions (an access-control
list or ACL) to be attached to the *context* object. These are advanced
questions so we won't cover them here. Traversal has a learning curve, and it
may or may not be appropriate for different kinds of applications.
Nevertheless, it's good to know it exists so that you can explore it gradually
over time and maybe find a use for it someday.


SQLAHelper and a "models" subpackage
====================================

Earlier versions of Akhet used the SQLAHelper library to organize engines and
sessions. This is no longer documented because it's not that much benefit. The
main thing to remember is that if you split *models.py* into a package, beware
of circular imports. If you define the ``Base`` and ``DBSession`` in
*models/\_\_ini\_\_.py* and import them into submodules, and the init module
imports the submodules, there will be a circular import of two modules
importing each other. One module will appear semi-empty while the other module
is running its global code, which could lead to exceptions. 

Pylons dealt with this by putting the Base and Session in a submodule,
*models/meta.py*, which did not import any other model modules. SQLAHelper
deals with it by providing a third-party library to store engines, sessions,
and bases. The Pyramid developers decided to default to the simplest case of
the putting entire model in one module, and let you figure out how to split it
if you want to.

Model Examples
==============

These examples were written a while ago so they don't use the transaction
manager, and they have yet at third importing syntax. They should work with
SQLAlchemy 0.6, 0.7, and 0.8.

A simple one-table model
------------------------

::

    import sqlalchemy as sa
    import sqlalchemy.orm as orm
    import sqlalchemy.ext.declarative as declarative
    from zope.sqlalchemy import ZopeTransactionExtension as ZTE

    DBSession = orm.scoped_session(orm.sessionmaker(extension=ZTE()))
    Base = declarative.declarative_base()

    class User(Base):
        __tablename__ = "users"

        id = sa.Column(sa.Integer, primary_key=True)
        name = sa.Column(sa.Unicode(100), nullable=False)
        email = sa.Column(sa.Unicode(100), nullable=False)

This model has one ORM class, ``User`` corresponding to a database table
``users``. The table has three columns: ``id``, ``name``, and ``user``.


A three-table model
-------------------

We can expand the above into a three-table model suitable for a medium-sized
application.  ::

    import sqlalchemy as sa
    import sqlalchemy.orm as orm
    import sqlalchemy.ext.declarative as declarative
    from zope.sqlalchemy import ZopeTransactionExtension as ZTE

    DBSession = orm.scoped_session(orm.sessionmaker(extension=ZTE()))
    Base = declarative.declarative_base()

    class User(Base):
        __tablename__ = "users"

        id = sa.Column(sa.Integer, primary_key=True)
        name = sa.Column(sa.Unicode(100), nullable=False)
        email = sa.Column(sa.Unicode(100), nullable=False)

        addresses = orm.relationship("Address", order_by="Address.id")
        activities = orm.relationship("Activity",
            secondary="assoc_users_activities")

        @classmethod
        def by_name(class_):
            """Return a query of users sorted by name."""
            User = class_
            q = DBSession.query(User)
            q = q.order_by(User.name)
            return q
        

    class Address(Base):
        __tablename__ = "addresses"

        id = sa.Column(sa.Integer, primary_key=True)
        user_id = foreign_key_column(None, sa.Integer, "users.id")
        street = sa.Column(sa.Unicode(40), nullable=False)
        city = sa.Column(sa.Unicode(40), nullable=False)
        state = sa.Column(sa.Unicode(2), nullable=False)
        zip = sa.Column(sa.Unicode(10), nullable=False)
        country = sa.Column(sa.Unicode(40), nullable=False)
        foreign_extra = sa.Column(sa.Unicode(100, nullable=False))

        def __str__(self):
            """Return the address as a string formatted for a mailing label."""
            state_zip = u"{0} {1}".format(self.state, self.zip).strip()
            cityline = filterjoin(u", ", self.city, state_zip)
            lines = [self.street, cityline, self.foreign_extra, self.country]
            return filterjoin(u"|n", *lines) + u"\n"


    class Activity(Base):
        __tablename__ = "activities"

        id = sa.Column(sa.Integer, primary_key=True)
        activity = sa.Column(sa.Unicode(100), nullable=False)


    assoc_users_activities = sa.Table("assoc_users_activities", Base.metadata,
        foreign_key_column("user_id", sa.Integer, "users.id"),
        foreign_key_column("activities_id", sa.Unicode(100), "activities.id"))
            
    # Utility functions
    def filterjoin(sep, *items):
        """Join the items into a string, dropping any that are empty.
        """
        items = filter(None, items)
        return sep.join(items)

    def foreign_key_column(name, type_, target, nullable=False):
        """Construct a foreign key column for a table.

        ``name`` is the column name. Pass ``None`` to omit this arg in the 
        ``Column`` call; i.e., in Declarative classes.

        ``type_`` is the column type.

        ``target`` is the other column this column references.

        ``nullable``: pass True to allow null values. The default is False
        (the opposite of SQLAlchemy's default, but useful for foreign keys).
        """
        fk = sa.ForeignKey(target)
        if name:
            return sa.Column(name, type_, fk, nullable=nullable)
        else:
            return sa.Column(type_, fk, nullable=nullable)

This model has a ``User`` class corresponding to a ``users`` table, an
``Address`` class with an ``addresses`` table, and an ``Activity`` class with
``activities`` table.  ``users`` is in a 1:Many relationship with
``addresses``.  ``users`` is also in a Many:Many`` relationship with
``activities`` using the association table ``assoc_users_activities``.  This is
the SQLAlchemy "declarative" syntax, which defines the tables in terms of ORM
classes subclassed from a declarative ``Base`` class. Association tables do not
have an ORM class in SQLAlchemy, so we define it using the ``Table``
constructor as if we weren't using declarative, but it's still tied to the
Base's "metadata".

We can add instance methods to the ORM classes and they will be valid for one
database record, as with the ``Address.__str__`` method. We can also define
class methods that operate on several records or return a query object, as with
the ``User.by_name`` method. 

There's a bit of disagreement on whether ``User.by_name`` works better as a
class method or static method. Normally with class methods, the first argument
is called ``class_`` or ``cls`` or ``klass`` and you use it that way throughout
the method, but in ORM queries it's more normal to refer to the ORM class by
its proper name. But if you do that you're not using the ``class_`` variable
so why not make it a static method? But the method does belong to the class in
a way that an ordinary static method does not. I go back and forth on this, and
sometimes assign ``User = class_`` at the beginning of the method. But none of
these ways feels completely satisfactory, so I'm not sure which is best.

Common base class
-----------------

You can define a superclass for all your ORM classes, with common class methods
that all of them can use. It will be the parent of the declarative base::

    class ORMClass(object):
        @classmethod
        def query(class_):
            return DBSession.query(class_)

        @classmethod
        def get(class_, id):
            return Session.query(class_).get(id)

    Base = declarative.declarative_base(cls=ORMClass)
    
    class User(Base):
        __tablename__ = "users"

        # Column definitions omitted

Then you can do things like this in your views::

    user_1 = models.User.get(1)
    q = models.User.query()

Whether this is a good thing or not depends on your perspective.

Multiple databases
------------------

The default configuration in the main function configures one database. To
connect to multiple databases, list them all in
*development.ini* under distinct prefixes. You can put additional engine
arguments under the same prefixes. For instance:

.. code-block: ini

    sqlalchemy.url = postgresql://me:PASSWORD@localhost/mydb
    sqlalchemy.logging_name = maindb
    stats.url = sqlite:///%(here)s/scratch.sqlite
    stats.logging_name = sessionsdb

Then modify the main function to add each engine. You can also pass even more
engine arguments that override any same-name ones in the INI file. ::

    engine = sa.engine_from_config(settings, prefix="sqlalchemy.",
        pool_recycle=3600, convert_unicode=True)
    stats = sa.engine_from_config(settings, prefix="stats.")

At this point you have a choice. Do you want to bind different tables to
different databases in the same DBSession? That's easy::

    DBSession.configure(binds={models.Person: engine, models.Score: stats})

The keys in the ``binds`` dict can be SQLAlchemy ORM classes, table objects, or
mapper objects.

But some applications prefer multiple DBSessions, each connected to a different
database. Some applications prefer multiple declarative bases, so that
different groups of ORM classes have a different declarative base. Or perhaps
you want to bind the engine directly to the Base's metadata for low-level SQL
queries. Or you may be using a third-party package that defines
its own DBSession or Base. In these cases, you'll have to modify the model
itself, e.g., to add a DBSession2 or Base2. If the configuration is complex you
may want to define a model initialization function like Pylons does, so that
the top-level routine (the main function or a standalone utility) only has to
make one simple call. Here's a pretty elaborate init routine for a complex
application::

    DBSession1 = orm.scoped_session(orm.sessionmaker(extension=ZTE())
    DBSession2 = orm.scoped_session(orm.sessionmaker(extension=ZTE())
    Base1 = declarative.declarative_base()
    Base2 = declarative.declarative_base()
    engine1 = None
    engine2 = None

    def init_model(e1, e2):
        # e1 and e2 are SQLAlchemy engines. (We can't call them engine1 and
        # engine2 because we want to access globals with the same name.)
        global engine1, engine2
        engine1 = e1
        engine2 = e2
        DBSession1.configure(bind=e1)
        DBSession2.configure(bind=e2)
        Base1.metadata.bind = e1
        Base2.metadata.bind = e2


Reflected tables
----------------

Reflected tables pose a dilemma because they depend on a live database
connection in order to be initialized. But the engine is not known 
when the model is imported. This situation pretty much requires an
initialization function; or at least we haven't found any way around it.
The ORM classes can still be defined as module globals (not using the
declarative syntax), but the table definitions and mapper calls will have to be
done inside the function when the engine is known. Here's how you'd do it
non-declaratively::

    DBSession = orm.scoped_session(orm.sessionmaker(extension=ZTE())
    # Not using Base; not using declarative syntax
    md = sa.MetaData()
    persons = None   # Table, set in init_model().

    class Person(object):
        pass

    def init_model(engine):
        global persons
        DBSession.configure(bind=engine)
        md.bind = engine
        persons = sa.Table("persons", md, autoload=True, autoload_with=engine)
        orm.mapper(Person, persons)

With the declarative syntax, we *think* Michael Bayer has posted recipies for
this somewhere, but you'll have to poke around the SQLAlchmey planet to find
them. At worst you could put the entire declarative class inside the init_model
function and assign it to a global variable.


.. _Engine Configuration: http://www.sqlalchemy.org/docs/core/engines.html
.. _Dialects: http://www.sqlalchemy.org/docs/dialects/index.html
.. _Configuring Logging: http://www.sqlalchemy.org/docs/core/engines.html#configuring-logging
.. _scoped session: http://www.sqlalchemy.org/docs/orm/session.html#contextual-thread-local-sessions
.. _Using a Commit Veto: http://docs.repoze.org/tm2/#using-a-commit-veto

.. include:: ../links.rst
