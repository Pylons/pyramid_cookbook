Traversal with SQLAlchemy
%%%%%%%%%%%%%%%%%%%%%%%%%

This is a stub page, written by a non-expert. If you have expertise, please
verify the content, add recipes, and consider writing a tutorial on this.

Traversal works most naturally with an object database like ZODB because both
are naturally recursive. (I.e., "/a/b" maps naturally to ``root["a"]["b"]``.)
SQL tables are flat, not recursive. However, it's possible to use traversal
with SQLAlchemy, and it's becoming increasingly popular. To see how to do this,
it helps to consider recursive and non-recursive usage separately.

Non-recursive
=============

A non-recursive use case is where a certain URL maps to a table, and the
following component is a record ID. For instance::

    # /persons/123   =>   root["persons"][123]

    import myapp.model as model

    class Resource(dict):
        def __init__(self, name, parent):
            self.__name__ = name
            self.__parent__ = parent

    class Root(Resource):
        """The root resource."""

        def add_resource(self, name, orm_class):
            self[name] = ORMContainer(name, self, self.request, orm_class)

        def __init__(self, request):
            self.request = request
            self.add_resource('persons', model.Person)

    root_factory = Root

    class ORMContainer(dict):
        """Traversal component tied to a SQLAlchemy ORM class.

        Calling .__getitem__ fetches a record as an ORM instance, adds certain
        attributes to the object, and returns it.
        """
        def __init__(self, name, parent, request, orm_class):
            self.__name__  = name
            self.__parent__ = parent
            self.request = request
            self.orm_class = orm_class

        def __getitem__(self, key):
            try:
                key = int(key)
            except ValueError:
                raise KeyError(key)
            obj = model.DBSession.query(self.orm_class).get(key)
            # If the ORM class has a class method '.get' that performs the
            # query, you could do this:  ``obj = self.orm_class.get(key)``
            if obj is None:
                raise KeyError(key)
            obj.__name__ = key
            obj.__parent__ = self
            return obj

Here, ``root["persons"]`` is a container object whose ``__getitem__`` method
fetches the specified database record, sets name and parent attribues on it,
and returns it. (We've verified that SQLAlchemy does not define ``__name__`` or
``__parent__`` attributes in ORM instances.) If the record is not found, raise
KeyError to indicate the resource doesn't exist.

TODO: Describe URL generation, access control lists, and other things needed in
a complete application.

One drawback of this approach is that you have to fetch the entire record in
order to generate a URL to it. This does not help if you have index views that
display links to records, by querying the database directly for the IDs that
match a criterion (N most recent records, all records by date, etc). You don't
want to fetch the entire record's body, or do something silly like asking
traversal for the resource at "/persons/123" and then generate the URL -- which
would be "/persons/123"! There are a few ways to generate URLs in this case:

* Define a generation-only route; e.g.,
  ``config.add_route("person", "/persons/{id}", static=True)``
* Instead of returning an ORM instance, return a proxy that lazily fetches the
  instance when its attributes are accessed. This causes traversal to behave
  somewhat incorrectly. It *should* raise KeyError if the record doesn't exist,
  but it can't know whether the record exists without fetching it. If traversal
  returns a possibly-invalid resource, it puts a burden on the view to check
  whether its context is valid. Normally the view can just assume it is,
  otherwise the view wouldn't have been invoked.

Recursive
=========

The prototypical recursive use case is a content management system, where the
user can define URLs arbitrarily deep; e.g., "/a/b/c". It can also be useful
with "canned" data, where you want a small number of views to respond to a
large variety of URL hierarchies.

Kotti_ is the best current example of using traversal with SQLAlchemy
recursively. Kotti is a content management system that, yes, lets users define
arbitrarily deep URLs. Specifically, Kotti allows users to define a page with
subpages; e.g., a "directory" of pages.

.. _Kotti: http://kotti.readthedocs.org/en/latest/index.html

Kotti is rather complex and takes some time to study. It uses SQLAlchemy's
polymorphism to make tables "inherit" from other tables. This is an advanced
feature which can be complex to grok. On the other hand, if you have the time,
it's a great way to learn how to do recursive traversal and polymorphism.

The main characteristic of a recursive SQL setup is a self-referential table;
i.e., table with a foreign key colum pointing to the same table. This allows
each record to point to its parent. (The root record has NULL in the parent
field.)
