Pyramid Cookbook
================

The Pyramid Cookbook presents topical, practical usages of :mod:`Pyramid`.

.. toctree::
   :maxdepth: 2

   static
   exceptions
   authentication
   templates
   sqla

TODO
----

- Provide an example of using a newrequest subscriber to mutate the request,
  providing additional user data from a database based on the current
  authenticated userid.

- Provide an example of adding a database connection to ``settings`` in
  __init__ and using it from a view.

- Provide an example of a catchall 500 error view.

- [22:17] <AGreatJewel> In the forbidden view, is it possible to get the 
  permission that the user did not have?
  [22:18] <mcdonc> its in the exception
  [22:18] <mcdonc> request.exception
  [22:18] <mcdonc> request.exception.permission likely

- [22:04] <AGreatJewel> How do I redirect to a url and set some GET params? 
  some thing like return HTTPFound(location="whatever", params={ params here })
  [22:05] <mcdonc> return HTTPFound(location="whatever?a=1&b=2")
  [22:06] <AGreatJewel> ok. and I would need to urlencode the entire string?
  [22:06] <AGreatJewel> or is that handled automatically
  [22:07] <mcdonc> its a url
  [22:07] <mcdonc> like you'd type into the browser

- [22:47] <AGreatJewel> I am having some trouble with the session 
  [22:47] <AGreatJewel> http://pylonshq.com/pasties/743848dc31cc6230a7ba1abe80562550
  [22:47] <AGreatJewel> on line 30, I get ou = None. Inspite of setting the 
          session in the forbidden view.
  [22:47] <AGreatJewel> Any clues as to why this is happening?
  [22:53] <mcdonc> AGreatJewel: set session.cookie_on_exception = True in 
          your .ini configuration
  [22:54] <mcdonc> it depends how you're creating a session factory really
  [22:54] <mcdonc> but basically you have to make sure the session factory is 
          configured with cookie_on_exception = True
  [22:56] <mcdonc> if you're using a session factory from pyramid_beaker, 
          you'll need to make sure you're running version 0.4 of pyramid_beaker

- http://blog.abourget.net/2011/1/13/pyramid-and-mako:-how-to-do-i18n-the-pylons-way/

- http://blog.dannynavarro.net/2011/01/14/async-web-apps-with-pyramid/

- http://pylonshq.com/pasties/e4b933da7f577c541cc2f2489f825fdd (facebook)

- http://pylonshq.com/pasties/c549d2be586797da17c7fad5ae875372 (twitter)

- http://alexmarandon.com/articles/zodb_bfg_pyramid_notes/

- http://www.serverzen.net/2010/11/20/pyramid-setting-up-debug-werkzeug

- http://groups.google.com/group/pylons-devel/msg/ab58353594b135c9
  (pyramid_jinja2 i18n), also
  https://github.com/Pylons/pyramid_jinja2/pull/14

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

