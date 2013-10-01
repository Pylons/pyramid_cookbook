Virtual Rooting
===============

You can present a folder other than the physical Substance D root object as the
"SDI root" to people.  For example, if you have the following structure from
your physical Substance D root::

  root--
        \-- folder1
        |
        |-- folder2

You can present either ``folder1`` or ``folder2`` to the user as a virtual
root when people log in to the SDI.

To do so, you have to pass an ``X-Vhm-Root`` header to SubstanceD in each
request.  It's easiest to do this with Apache or another frontend web server.
Here's a sample configuration which assumes you are telling Apache to proxy to
a Substance D application that runs on localhost on port 6543::

  <VirtualHost *:80>
      ServerAdmin webmaster@agendaless.com
      ServerName  example.com
      ErrorLog    /var/log/apache2/example.com-error.log
      CustomLog   /var/log/apache2/example.com-access.log combined
      RewriteEngine On
      RewriteRule ^(.*) http://127.0.0.1:6543/$1 [L,P]
      ProxyPreserveHost On
      RequestHeader add X-Vhm-Root /folder1
  </VirtualHost>

In the above configuration, when users log in on ``http://example.com/manage``,
the root they see in the SDI will be ``/folder1`` instead of the real root.
They will not be able to access the real root.

Note that retail requests (requests without ``/manage``) to the same hostname
will *also* be rooted at ``folder1``.

This feature requires Pyramid version 1.4.4 or better.
