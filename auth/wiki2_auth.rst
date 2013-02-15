Wiki Flow of Authentication
===========================

This tutorial describes the "flow of authentication" of the result of the
completing the :ref:`wiki2_adding_authorization` tutorial chapter from the
main Pyramid documentation.

This text was contributed by John Shipman.

.. _wiki2_flow_of_authentication:

Overall flow of an authentication
---------------------------------

Now that you have seen all the pieces of the authentication
mechanism, here are some examples that show how they all work
together.

#. Failed login: The user requests ``/FrontPage/edit_page``.  The
   site presents the login form.  The user enters ``editor`` as
   the login, but enters an invalid password ``bad``.
   The site redisplays the login form with the message "Failed
   login".  See :ref:`failed_login`.

#. The user again requests ``/FrontPage/edit_page``.  The site
   presents the login form, and this time the user enters
   login ``editor`` and password ``editor``.  The site presents
   the edit form with the content of ``/FrontPage``.  The user
   makes some changes and saves them.  See :ref:`good_login`.

#. The user again revisits ``/FrontPage/edit_page``.  The site
   goes immediately to the edit form without requesting
   credentials. See :ref:`revisit`.

#. The user clicks the ``Logout`` link.  See :ref:`logging_out`.

.. _failed_login:

Failed login
~~~~~~~~~~~~

The process starts when the user enters URL
``http://localhost:6543/FrontPage/edit_page``.  Let's assume that
this is the first request ever made to the application and the
page database is empty except for the ``Page`` instance created
for the front page by the ``initialize_sql`` function in
:file:`models.py`.

This process involves two complete request/response cycles.

1. From the front page, the user clicks :guilabel:`Edit page`.
   The request is to ``/FrontPage/edit_page``.  The view callable
   is ``login.login``. The response is the ``login.pt`` template
   with blank fields.

2. The user enters invalid credentials and clicks :guilabel:`Log
   in`.  A ``POST`` request is sent to ``/FrontPage/edit_page``.
   The view callable is again ``login.login``.  The response is
   the ``login.pt`` template showing the message "Failed login",
   with the entry fields displaying their former values.

Cycle 1:

#. During URL dispatch, the route ``'/{pagename}/edit_page'`` is
   considered for matching.  The associated view has a
   ``view_permission='edit'`` permission attached, so the
   dispatch logic has to verify that the user has that permission
   or the route is not considered to match.
   
   The context for all route matching comes from the configured
   root factory, :meth:`RootFactory` in :file:`models.py`.
   This class has an ``__acl__`` attribute that defines the
   access control list for all routes::

        __acl__ = [ (Allow, Everyone, 'view'),
                    (Allow, 'group:editors', 'edit') ]

   In practice, this means that for any route that requires the
   ``edit`` permission, the user must be authenticated and
   have the ``group:editors`` principal or the route is not
   considered to match.

#. To find the list of the user's principals, the authorization
   first policy checks to see if the user has a
   ``paste.auth.auth_tkt`` cookie.  Since the user has never been
   to the site, there is no such cookie, and the user is
   considered to be unauthenticated.

#. Since the user is unauthenticated, the ``groupfinder``
   function in :file:`security.py` is called with ``None`` as its
   ``userid`` argument.  The function returns an empty list of
   principals.

#. Because that list does not contain the ``group:editors``
   principal, the ``'/{pagename}/edit_page'`` route's ``edit``
   permission fails, and the route does not match.

#. Because no routes match, the `forbidden view` callable is
   invoked: the ``login`` function in module ``login.py``.

#. Inside the ``login`` function, the value of ``login_url`` is
   ``http://localhost:6543/login``, and the value of
   ``referrer`` is ``http://localhost:6543/FrontPage/edit_page``.
   
   Because ``request.params`` has no key for ``'came_from'``, the
   variable ``came_from`` is also set to
   ``http://localhost:6543/FrontPage/edit_page``.  Variables
   ``message``, ``login``, and ``password`` are set to the empty
   string.

   Because ``request.params`` has no key for
   ``'form.submitted'``, the ``login`` function returns this
   dictionary::

    {'message': '', 'url':'http://localhost:6543/login',
     'came_from':'http://localhost:6543/FrontPage/edit_page',
     'login':'', 'password':''}

#. This dictionary is used to render the ``login.pt`` template.
   In the form, the ``action`` attribute is
   ``http://localhost:6543/login``, and the value of
   ``came_from`` is included in that form as a hidden field
   by this line in the template::

       <input type="hidden" name="came_from" value="${came_from}"/>

Cycle 2:

#. The user enters incorrect credentials and clicks the
   :guilabel:`Log in` button, which does a ``POST`` request to
   URL ``http://localhost:6543/login``.  The name of the
   :guilabel:`Log in` button in this form is ``form.submitted``.

#. The route with pattern ``'/login'`` matches this URL, so
   control is passed again to the ``login`` view callable.
   
#. The ``login_url`` and ``referrer`` have the same value
   this time (``http://localhost:6543/login``), so variable
   ``referrer`` is set to ``'/'``.

   Since ``request.params`` does have a key ``'form.submitted'``,
   the values of ``login`` and ``password`` are retrieved from
   ``request.params``.

   Because the login and password do not match any of the entries
   in the ``USERS`` dictionary in ``security.py``, variable
   ``message`` is set to ``'Failed login'``.

   The view callable returns this dictionary::

    {'message':'Failed login',
     'url':'http://localhost:6543/login', 'came_from':'/',
     'login':'editor', 'password':'bad'}

#. The ``login.pt`` template is rendered using those values.

.. _good_login:

Successful login
~~~~~~~~~~~~~~~~

In this scenario, the user again requests URL
``/FrontPage/edit_page``.

This process involves four complete request/response cycles.

1. The user clicks :guilabel:`Edit page`.  The view callable is
   ``login.login``.  The response is template ``login.pt``,
   with all the fields blank.

2. The user enters valid credentials and clicks :guilabel:`Log in`.
   The view callable is ``login.login``.  The response is a
   redirect to ``/FrontPage/edit_page``.

3. The view callable is ``views.edit_page``.  The response
   renders template ``edit.pt``, displaying the current page
   content.

4. The user edits the content and clicks :guilabel:`Save`.
   The view callable is ``views.edit_page``.  The response
   is a redirect to ``/FrontPage``.

Execution proceeds as in :ref:`failed_login`, up to the point
where the password ``editor`` is successfully matched against the
value from the ``USERS`` dictionary.

Cycle 2:

#. Within the ``login.login`` view callable, the value of
   ``login_url`` is ``http://localhost:6543/login``, and the
   value of ``referrer`` is ``'/'``, and ``came_from`` is
   ``http://localhost:6543/FrontPage/edit_page`` when this block
   is executed::

        if USERS.get(login) == password:
            headers = remember(request, login)
            return HTTPFound(location=came_from, headers=headers)

#. Because the password matches this time,
   :mod:`pyramid.security.remember` returns a sequence of header
   tuples that will set a ``paste.auth.auth_tkt`` authentication
   cookie in the user's browser for the login ``'editor'``.

#. The ``HTTPFound`` exception returns a response that redirects
   the browser to ``http://localhost:6543/FrontPage/edit_page``,
   including the headers that set the authentication cookie.

Cycle 3:

#. Route pattern ``'/{pagename}/edit_page'`` matches this URL,
   but the corresponding view is restricted by an ``'edit'``
   permission.
   
#. Because the user now has an authentication cookie defining
   their login name as ``'editor'``, the ``groupfinder`` function
   is called with that value as its ``userid`` argument.

#. The ``groupfinder`` function returns the list
   ``['group:editors']``.  This satisfies the access control
   entry ``(Allow, 'group:editors', 'edit')``, which grants the
   ``edit`` permission.  Thus, this route matches, and control
   passes to view callable ``edit_page``.

#. Within ``edit_page``, ``name`` is set to ``'FrontPage'``, the
   page name from ``request.matchdict['pagename']``, and
   ``page`` is set to an instance of :class:`models.Page`
   that holds the current content of ``FrontPage``.

#. Since this request did not come from a form,
   ``request.params`` does not have a key for
   ``'form.submitted'``.

#. The ``edit_page`` function calls
   :meth:`pyramid.security.authenticated_userid` to find out
   whether the user is authenticated.  Because of the cookies
   set previously, the variable ``logged_in`` is set to
   the userid ``'editor'``.

#. The ``edit_page`` function returns this dictionary::

    {'page':page, 'logged_in':'editor',
     'save_url':'http://localhost:6543/FrontPage/edit_page'}

#. Template :file:`edit.pt` is rendered with those values.
   Among other features of this template, these lines
   cause the inclusion of a :guilabel:`Logout` link::

      <span tal:condition="logged_in">
        <a href="${request.application_url}/logout">Logout</a>
      </span>

   For the example case, this link will refer to
   ``http://localhost:6543/logout``.

   These lines of the template display the current page's
   content in a form whose ``action`` attribute is
   ``http://localhost:6543/FrontPage/edit_page``::

      <form action="${save_url}" method="post">
        <textarea name="body" tal:content="page.data" rows="10" cols="60"/>
        <input type="submit" name="form.submitted" value="Save"/>
      </form>

Cycle 4:

#. The user edits the page content and clicks
   :guilabel:`Save`.

#. URL ``http://localhost:6543/FrontPage/edit_page`` goes through
   the same routing as before, up until the line that checks
   whether ``request.params`` has a key ``'form.submitted'``.
   This time, within the ``edit_page`` view callable, these
   lines are executed::
    
        page.data = request.params['body']
        session.add(page)
        return HTTPFound(location = route_url('view_page', request,
                                              pagename=name))

   The first two lines replace the old page content with the
   contents of the ``body`` text area from the form, and then
   update the page stored in the database.  The third line
   causes a response that redirects the browser to
   ``http://localhost:6543/FrontPage``.

.. _revisit:

Revisiting after authentication
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this case, the user has an authentication cookie set in their
browser that specifies their login as ``'editor'``.  The
requested URL is ``http://localhost:6543/FrontPage/edit_page``.
   
This process requires two request/response cycles.

1. The user clicks :guilabel:`Edit page`.  The view callable is
   ``views.edit_page``.  The response is ``edit.pt``, showing
   the current page content.   

2. The user edits the content and clicks :guilabel:`Save`.
   The view callable is ``views.edit_page``.  The response is
   a redirect to ``/Frontpage``.

Cycle 1:

#. The route with pattern ``/{pagename}/edit_page`` matches the
   URL, and because of the authentication cookie, ``groupfinder``
   returns a list containing the ``group:editors`` principal,
   which ``models.RootFactory.__acl__`` uses to grant the
   ``edit`` permission, so this route matches and dispatches
   to the view callable :meth:`views.edit_page`.

#. In ``edit_page``, because the request did not come from a form
   submission, ``request.params`` has no key for
   ``'form.submitted'``.

#. The variable ``logged_in`` is set to  the login name
   ``'editor'`` by calling ``authenticated_userid``, which
   extracts it from the authentication cookie.

#. The function returns this dictionary::

    {'page':page,
     'save_url':'http://localhost:6543/FrontPage/edit_page',
     'logged_in':'editor'}

#. Template :file:`edit.pt` is rendered with the values from
   that dictionary.  Because of the presence of the
   ``'logged_in'`` entry, a :guilabel:`Logout` link appears.

Cycle 2:

#. The user edits the page content and clicks :guilabel:`Save`.

#. The ``POST`` operation works as in :ref:`good_login`.

.. _logging_out:

Logging out
~~~~~~~~~~~

This process starts with a request URL
``http://localhost:6543/logout``.

#. The route with pattern ``'/logout'`` matches and dispatches
   to the view callable ``logout`` in :file:`login.py`.

#. The call to :meth:`pyramid.security.forget` returns a list of
   header tuples that will, when returned with the response,
   cause the browser to delete the user's authentication cookie.

#. The view callable returns an ``HTTPFound`` exception that
   redirects the browser to named route ``view_wiki``, which
   will translate to URL ``http://localhost:6543``.  It
   also passes along the headers that delete the
   authentication cookie.
