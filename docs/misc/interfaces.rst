Interfaces
==========

This chapter contains information about using ``zope.interface`` with
Pyramid.

Dynamically Compute the Interfaces Provided by an Object
--------------------------------------------------------

(Via Marius Gedminas)

When persisting the interfaces that are provided by an object in a pickle or
in ZODB is not reasonable for your application, you can use this trick to
dynamically return the set of interfaces provided by an object based on other
data in an instance of the object::

    from zope.interface.declarations import Provides

    from mypackage import interfaces

    class MyClass(object):

        color = None

        @property
        def __provides__(self):
            # black magic happens here: we claim to provide the right IFrob
            # subinterface depending on the value of the ``color`` attribute.
            iface = getattr(interfaces, 'I%sFrob' % self.color.title(),
                            interfaces.IFrob))
            return Provides(self.__class__, iface)

If you need the object to implement more than one interface, use
``Provides(self.__class__, iface1, iface2, ...)``.
