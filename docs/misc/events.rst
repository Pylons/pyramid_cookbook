Using Object Events in Pyramid
------------------------------

.. warning:: This code works only in Pyramid 1.1a4+.  It will also make your
   brain explode.

Zope's Component Architecture supports the concept of "object events", which
are events which call a subscriber with an context object *and* the event
object.

Here's an example of using an object event subscriber via the ``@subscriber``
decorator::

    from zope.component.event import objectEventNotify
    from zope.component.interfaces import ObjectEvent

    from pyramid.events import subscriber
    from pyramid.view import view_config

    class ObjectThrownEvent(ObjectEvent):
        pass

    class Foo(object):
      pass

    @subscriber([Foo, ObjectThrownEvent])
    def objectevent_listener(object, event):
        print object, event

    @view_config(renderer='string')
    def theview(request):
        objectEventNotify(ObjectThrownEvent(Foo()))
        objectEventNotify(ObjectThrownEvent(None))
        objectEventNotify(ObjectEvent(Foo()))
        return 'OK'

    if __name__ == '__main__':
        from pyramid.config import Configurator
        from paste.httpserver import serve
        config = Configurator(autocommit=True)
        config.hook_zca()
        config.scan('__main__')
        serve(config.make_wsgi_app())

The ``objectevent_listener`` listener defined above will only be called when
the ``object`` of the ObjectThrownEvent is of class ``Foo``.  We can tell
that's the case because only the first call to objectEventNotify actually
invokes the subscriber.  The second and third calls to objectEventNotify do
not call the subscriber.  The second call doesn't invoke the subscriber
because its object type is ``None`` (and not ``Foo``).  The third call
doesn't invoke the subscriber because its objectevent type is ObjectEvent
(and not ``ObjectThrownEvent``).  Clear as mud?
