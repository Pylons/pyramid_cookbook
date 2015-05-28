Using a View Mapper to Pass Query Parameters as Keyword Arguments
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

Pyramid supports a concept of a "view mapper".  See
:ref:`using_a_view_mapper` for general information about view mappers.  You
can use a view mapper to support an alternate convenience calling convention
in which you allow view callables to name extra required and optional
arguments which are taken from the request.params dictionary.  So, for
example, instead of::

   @view_config()
   def aview(request):
       name = request.params['name']
       value = request.params.get('value', 'default')
       ...

With a special view mapper you can define this as::

   @view_config(mapper=MapplyViewMapper)
   def aview(request, name, value='default'):
       ...

The below code implements the ``MapplyViewMapper``.  It works as a mapper for
function view callables and method view callables::

    import inspect
    import sys

    from pyramid.view import view_config
    from pyramid.response import Response
    from pyramid.config import Configurator
    from waitress import serve

    PY3 = sys.version_info[0] == 3

    if PY3:
        im_func = '__func__'
        func_defaults = '__defaults__'
        func_code = '__code__'
    else:
        im_func = 'im_func'
        func_defaults = 'func_defaults'
        func_code = 'func_code'

    def mapply(ob, positional, keyword):

        f = ob
        im = False

        if hasattr(f, im_func):
            im = True

        if im:
            f = getattr(f, im_func)
            c = getattr(f, func_code)
            defaults = getattr(f, func_defaults)
            names = c.co_varnames[1:c.co_argcount]
        else:
            defaults = getattr(f, func_defaults)
            c = getattr(f, func_code)
            names = c.co_varnames[:c.co_argcount]

        nargs = len(names)
        args = []
        if positional:
            positional = list(positional)
            if len(positional) > nargs:
                raise TypeError('too many arguments')
            args = positional

        get = keyword.get
        nrequired = len(names) - (len(defaults or ()))
        for index in range(len(args), len(names)):
            name = names[index]
            v = get(name, args)
            if v is args:
                if index < nrequired:
                    raise TypeError('argument %s was omitted' % name)
                else:
                    v = defaults[index-nrequired]
            args.append(v)

        args = tuple(args)
        return ob(*args)

        
    class MapplyViewMapper(object): 
        def __init__(self, **kw):
            self.attr = kw.get('attr')

        def __call__(self, view):
            def wrapper(context, request):
                keywords = dict(request.params.items())
                if inspect.isclass(view):
                    inst = view(request)
                    meth = getattr(inst, self.attr)
                    response = mapply(meth, (), keywords)
                else:
                    # it's a function
                    response = mapply(view, (request,), keywords)
                return response

            return wrapper

    @view_config(name='function', mapper=MapplyViewMapper)
    def view_function(request, one, two=False):
        return Response('one: %s, two: %s' % (one, two))

    class ViewClass(object):
        __view_mapper__ = MapplyViewMapper
        def __init__(self, request):
            self.request = request

        @view_config(name='method')
        def view_method(self, one, two=False):
            return Response('one: %s, two: %s' % (one, two))

    if __name__ == '__main__':
        config = Configurator()
        config.scan('.')
        app = config.make_wsgi_app()
        serve(app)

    # http://localhost:8080/function --> (exception; no "one" arg supplied)

    # http://localhost:8080/function?one=1 --> one: '1', two: False

    # http://localhost:8080/function?one=1&two=2 --> one: '1', two: '2'

    # http://localhost:8080/method --> (exception; no "one" arg supplied)

    # http://localhost:8080/method?one=1 --> one: '1', two: False

    # http://localhost:8080/method?one=1&two=2 --> one: '1', two: '2'
