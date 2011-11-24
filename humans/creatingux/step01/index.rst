===============================
Step 01: Hello World in Pyramid
===============================

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

Microframeworks are all the rage these days. They provide low-overhead
on execution. But also, they have a low mental overhead: they do so
little, the only things you have to worry about are *your things*.

Pyramid is special because it can act as a single-file module
microframework. You have a single Python file that can be executed
directly by Python. But Pyramid also scales to the largest of
applications.

Steps
=====

#. Make sure you have followed the steps in :doc:`../../setup`.

#. ``$ mkdir creatingux; cd creatingux``

#. ``$ mkdir step01; cd step01``

#. Copy the following into ``step01/application.py``:

   .. literalinclude:: application.py
      :linenos:

#. ``$ python application.py``

#. Open ``http://127.0.0.1:8080/`` in your browser.

Extra Credit
============

#. What happens if you return a string of HTML? A sequence of integers?

#. Put something invalid, such as ``print xyz``, in the view function.
   Kill your ``python application.py`` and restart,
   then reload your browser. See the exception in the console?

#. Does Pyramid support automatic reloading of Python code?

Analysis
========

This single-file module does quite a bit for so few lines,
thus making it spiritually similar to microframeworks. A view function
is added to the configuration. When called, the view returns a response.

Discussion
==========

- Background on megaframeworks, microframeworks, and Pyramid's opinion
  thereof

