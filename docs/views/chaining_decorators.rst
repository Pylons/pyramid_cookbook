Chaining Decorators
%%%%%%%%%%%%%%%%%%%

Pyramid has a ``decorator=`` argument to its view configuration.  It accepts
a single decorator that will wrap the *mapped* view callable represented by
the view configuration.  That means that, no matter what the signature and
return value of the original view callable, the decorated view callable will
receive two arguments: ``context`` and ``request`` and will return a response
object::

    # the decorator

    def decorator(view_callable):
        def inner(context, request):
            return view_callable(context, request)
        return inner

    # the view configuration

    @view_config(decorator=decorator, renderer='json')
    def myview(request):
        return {'a':1}

But the ``decorator`` argument only takes a single decorator.  What happens
if you want to use more than one decorator?  You can chain them together::

    def combine(*decorators):
        def floo(view_callable):
            for decorator in decorators:
                view_callable = decorator(view_callable)
            return view_callable
        return floo

    def decorator1(view_callable):
        def inner(context, request):
            return view_callable(context, request)
        return inner

    def decorator2(view_callable):
        def inner(context, request):
            return view_callable(context, request)
        return inner

    def decorator3(view_callable):
        def inner(context, request):
            return view_callable(context, request)
        return inner

    alldecs = combine(decorator1, decorator2, decorator3)
    two_and_three = combine(decorator2, decorator3)
    one_and_three = combine(decorator1, decorator3)

    @view_config(decorator=alldecs, renderer='json')
    def myview(request):
        return {'a':1}
