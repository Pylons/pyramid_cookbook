================================
1: Single-File WSGI Applications
================================

What's the simplest way to get started in Pyramid? A single-file module.
No packages, imports, ``setup.py``, or other machinery.

Goals
=====

- Get Pyramid pixels on the screen as easily as possible

- Use that as a well-understood base for adding each unit of complexity

Objectives
==========

- Create a module with a view that acts as an HTTP server

- Visit the URL in your browser

Background
==========

Microframeworks are all the rage these days. "Microframework" is a
marketing term, not a technical one.  They have a low mental overhead:
they do so little, the only things you have to worry about are *your
things*.

Pyramid is special because it can act as a single-file module
microframework. You have a single Python file that can be executed
directly by Python. But Pyramid also scales to the largest of
applications.

Steps
=====

#. Make sure you have followed the steps in :doc:`../python_setup`.

#. ``(env33)$ mkdir step01; cd step01``

#. Copy the following into ``helloworld.py``:

   .. literalinclude:: helloworld.py
    :linenos:

#. Open ``http://127.0.0.1:6547/`` in your browser.

Analysis
========

The ``main()`` function is run from the ``if`` at the bottom,
which makes a WSGI application, hands it to an HTTP server (the
pure-Python server in the Python standard library), and starts listening.

This single-file module does quite a bit for so few lines,
thus making it spiritually similar to microframeworks. A view function
is added to the configuration. When called, the view returns a response.

The ``hello`` view is mapped to a route which is matched to the root
URL of the application.

Extra Credit
============

#. Why do we do this:

.. code-block:: python

  print ('Starting up server on http://localhost:6547')

...instead of:

.. code-block:: python

  print 'Starting up server on http://localhost:6547'

#. What happens if you return a string of HTML? A sequence of integers?

#. Put something invalid, such as ``print xyz``, in the view function.
   Kill your ``python helloworld.py`` and restart,
   then reload your browser. See the exception in the console?

Discussion
==========

- Background on megaframeworks, microframeworks, and Pyramid's opinion
  thereof
