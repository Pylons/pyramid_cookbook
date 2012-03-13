Authentication and Authorization
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

.. toctree::
   :maxdepth: 1

   user_object
   custom
   basic
   wiki2_auth

Auth Tutorial
=============

See Michael Merickel's authentication/authorization tutorial at
http://michael.merickel.org/projects/pyramid_auth_demo/ with code on Github at
https://github.com/mmerickel/pyramid_auth_demo.

Pyramid Auth with Akhet and SQLAlchemy
======================================

Learn how to set up Pyramid authorization using Akhet and SQLAlchemy at
http://pyramid.chromaticleaves.com/simpleauth/.

Google, Facebook, Tweeter, and any OpenID Authentication
========================================================

See `Wayne Witzel III's blog post
<http://pieceofpy.com/blog/2011/07/24/pyramid-and-velruse-for-google-authentication/>`_
about using Velruse and Pyramid together to do Google OAuth authentication.

See Matthew Housden and Chris Davies pyramid_apex project for any basic and openid
authentication such as Google, Facebook, Tweeter and more at 
https://github.com/cd34/pyramid_apex.

Integration with Enterprise Systems
===================================

When using Pyramid within an "enterprise" or the intranet it is often desireable to 
integrate with existing authentication and authorization (entitlement) systems. For
example in Microsoft Networks driven environments, user database is typically 
maintained in Active Directory. At present there is no ready to use recipe but we
are listing places that may be worth looking for ideas when developing one.

Authentication
--------------

* `adpasswd project on pypi <http://pypi.python.org/pypi/adpasswd/0.2>`_
* `Tim Golden's Active Directory Cookbook <http://timgolden.me.uk/python/ad_cookbook.html>`_
* `python-ad <http://code.google.com/p/python-ad/>`_
* `python-ldap.org <http://www.python-ldap.org/>`_
* `python-ntmlm <http://code.google.com/p/python-ntlm/>`_
* `Blog post on managing AD from Python in Linux <http://marcitland.blogspot.com/2011/02/python-active-directory-linux.html>`_

Authorization
-------------

* `Microsoft Authorization Manager <http://msdn.microsoft.com/en-us/library/aa480244.aspx>`_
* `Fundamentals of WCF Security <http://www.code-magazine.com/article.aspx?quickid=0611051>`_
* `Calling WCF Services from C++ using gSOAP <http://coab.wordpress.com/2009/10/15/calling-wcf-services-from-a-linux-c-client-using-gsoap/>`_

