Integration with Enterprise Systems
===================================

When using Pyramid within an "enterprise" (or an intranet), it is often desirable to
integrate with existing authentication and authorization (entitlement) systems.
For example, in Microsoft Network environments, the user database is typically
maintained in Active Directory. At present, there is no ready-to-use recipe, but we
are listing places that may be worth looking at for ideas when developing one:

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

