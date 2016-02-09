TODO
%%%%

- Provide an example of using a newrequest subscriber to mutate the request,
  providing additional user data from a database based on the current
  authenticated userid.

- Provide an example of adding a database connection to ``settings`` in
  __init__ and using it from a view.

- Provide an example of a catchall 500 error view.

- Redirecting to a URL with Parameters::

    [22:04] <AGreatJewel> How do I redirect to a url and set some GET params? 
    some thing like return HTTPFound(location="whatever", params={ params here })
    [22:05] <mcdonc> return HTTPFound(location="whatever?a=1&b=2")
    [22:06] <AGreatJewel> ok. and I would need to urlencode the entire string?
    [22:06] <AGreatJewel> or is that handled automatically
    [22:07] <mcdonc> its a url
    [22:07] <mcdonc> like you'd type into the browser

- Add an example of using a cascade to serve static assets from the root.

- Explore static file return from handler action using wsgiapp2 + fileapp.

- http://blog.dannynavarro.net/2011/01/14/async-web-apps-with-pyramid/

- http://alexmarandon.com/articles/zodb_bfg_pyramid_notes/

- http://www.serverzen.net/2010/11/20/pyramid-setting-up-debug-werkzeug

- http://groups.google.com/group/pylons-devel/msg/ab58353594b135c9
  (pyramid_jinja2 i18n), also
  https://github.com/Pylons/pyramid_jinja2/pull/14

- Simple asynchronous task queue: http://blog.dannynavarro.net/2011/01/23/async-pyramid-example-done-right/

- `Installing Pyramid on Red Hat Enterprise Linux 6
  <http://jfulton.org/pyramid1-rhel6-install.html>`_ (John Fulton).

- Chameleon main template injected via BeforeRender.

- Hybrid authorization: https://github.com/mmerickel/pyramid_auth_demo

- http://whippleit.blogspot.com/2011/04/pyramid-on-google-app-engine-take-1-for.html

- Custom events: http://blog.dannynavarro.net/2011/06/12/using-custom-events-in-pyramid/

- TicTacToe and Long Polling With Pyramid: http://www.merickel.org/2011/6/21/tictactoe-and-long-polling-with-pyramid/

- Jim Penny's rolodex tutorial: http://jpenny.im/

- Thorsten Lockert's formhelpers/Pyramid example: https://github.com/tholo/formhelpers2

- The Python Ecosystem, an Introduction: http://mirnazim.org/writings/python-ecosystem-introduction/

- Outgrowing Pyramid Handlers: http://michael.merickel.org/2011/8/23/outgrowing-pyramid-handlers/

- Incorporate Google Analytics into a Pyramid Application: http://russell.ballestrini.net/incorporate-google-analytics-into-a-pyramid-application/

- Cookbook docs reorg

  - Move tutorials/overviews to tutorial project and replace with links
