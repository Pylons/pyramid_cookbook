.. _comparing_traversal_and_dispatch:

Comparing and Combining Traversal and URL Dispatch
--------------------------------------------------

(adapted from Bayle Shank's contribution at
https://github.com/bshanks/pyramid/commit/c73b462c9671b5f2c3be26cf088ee983952ab61a).

Here's is an example which compares URL dispatch to traversal.

Let's say we want to map 

``/hello/login`` to a function ``login`` in the file ``myapp/views.py``

``/hello/foo`` to a function ``foo`` in the file ``myapp/views.py``

``/hello/listDirectory`` to a function ``listHelloDirectory`` in the file
``myapp/views.py``

``/hello/subdir/listDirectory`` to a function ``listSubDirectory`` in the
file ``myapp/views.py``

With URL dispatch, we might have::

    config.add_route('helloLogin', '/hello/login')
    config.add_route('helloFoo', '/hello/foo')
    config.add_route('helloList', '/hello/listDirectory')
    config.add_route('list', '/hello/{subdir}/listDirectory')

    config.add_view('myapp.views.login', route_name='helloLogin')
    config.add_view('myapp.views.foo', route_name='helloFoo')
    config.add_view('myapp.views.listHelloDirectory', route_name='helloList')
    config.add_view('myapp.views.listSubDirectory', route_name='list')

When the listSubDirectory function from ``myapp/views.py`` is called, it can
tell what the subdirectory's name was by checking
``request.matchdict['subdir']``.  This is about all you need to know for
URL-dispatch-based apps.

With traversal, we have a more complex setup::

    class MyResource(dict):
        def __init__(self, name, parent):
            self.__name__ = name
            self.__parent__ = parent

    class MySubdirResource(MyResource):
        def __init__(self, name, parent):
            self.__name__ = name
            self.__parent__ = parent
   
        # returns a MyResource object when the key is the name 
        # of a subdirectory
        def __getitem__(self, key):
            return MySubdirResource(key, self)
            
    class MyHelloResource(MySubdirResource):
        pass
   
    def myRootFactory(request):
        rootResource = MyResource('', None)
        helloResource = MyHelloResource('hello', rootResource)
        rootResource['hello'] = helloResource
        return rootResource
        
    config.add_view('myapp.views.login', name='login')
    config.add_view('myapp.views.foo', name='foo')
    config.add_view('myapp.views.listHelloDirectory', context=MyHelloResource, 
                    name='listDirectory')
    config.add_view('myapp.views.listSubDirectory', name='listDirectory')
   
In the traversal example, when a request for ``/hello/@@login`` comes in, the
framework calls ``myRootFactory(request)``, and gets back the root
resource. It calls the MyResource instance's ``__getitem__('hello')``, and
gets back a ``MyHelloResource``. We don't traverse the next path segment
(``@@login`), because the ``@@`` means the text that follows it is an
explicit view name, and traversal ends.  The view name 'login' is mapped to
the ``login`` function in ``myapp/views.py``, so this view callable is
invoked.

When a request for ``/hello/@@foo`` comes in, a similar thing happens.

When a request for ``/hello/@@listDirectory`` comes in, the framework calls
``myRootFactory(request)``, and gets back the root resource. It calls
MyRootResource's ``__getitem__('hello')``, and gets back a
``MyHelloResource`` instance. It *does not* call MyHelloResource's
``__getitem__('listDirectory')`` (due to the ``@@`` at the lead of
``listDirectory``).  Instead, 'listDirectory' becomes the view name and
traversal ends. The view name 'listDirectory' is mapped to
``myapp.views.listRootDirectory``, because the context (the last resource
traversed) is an instance of ``MyHelloResource``.

When a request for ``/hello/xyz/@@listDirectory`` comes in, the framework
calls ``myRootFactory(request)``, and gets back an instance of
``MyRootResource``. It calls MyRootResource's ``__getitem__('hello')``, and
gets back a ``MyHelloResource`` instance. It calls MyHelloResource's
``__getitem__('xyz')``, and gets back another ``MySubdirResource``
instance. It *does not* call ``__getitem__('listDirectory')`` on the
``MySubdirResource`` instance. 'listDirectory' becomes the view name and
traversal ends. The view name 'listDirectory' is mapped to
``myapp.views.listSubDirectory``, because the context (the final traversed
resource object) is not an instance of ``MyHelloResource``. The view can
access the ``MySubdirResource`` via ``request.context``.

At we see, traversal is more complicated than URL dispatch. What's the
benefit? Well, consider the URL ``/hello/xyz/abc/listDirectory``. This is
handled by the above traversal code, but the above URL dispatch code would
have to be modified to describe another layer of subdirectories. That is,
traversal can handle arbitrarily deep, dynamic hierarchies in a general way,
and URL dispatch can't.

You can, if you want to, combine URL dispatch and traversal (in that
order). So, we could rewrite the above as::

    class MyResource(dict):
        def __init__(self, name, parent):
            self.__name__ = name
            self.__parent__ = parent
            
        # returns a MyResource object unconditionally
        def __getitem__(self, key):
            return MyResource(key, self)

    def myRootFactory(request):
        return MyResource('', None)
     
    config = Configurator()

    config.add_route('helloLogin', '/hello/login')
    config.add_route('helloFoo', '/hello/foo')
    config.add_route('helloList', '/hello/listDirectory')
    config.add_route('list', '/hello/*traverse', factory=myRootFactory)

    config.add_view('myapp.views.login', route_name='helloLogin')
    config.add_view('myapp.views.foo', route_name='helloFoo')
    config.add_view('myapp.views.listHelloDirectory', route_name='helloList')
    config.add_view('myapp.views.listSubDirectory', route_name='list',
                    name='listDirectory')

You will be able to visit
e.g. `<http://localhost:8080/hello/foo/bar/@@listDirectory>`_ to see the
listSubDirectory view.

This is simpler and more readable because we are using URL dispatch to take
care of the hardcoded URLs at the top of the tree, and we are using traversal
only for the arbitrarily nested subdirectories.

See Also
~~~~~~~~

- :ref:`traversal_in_views`
