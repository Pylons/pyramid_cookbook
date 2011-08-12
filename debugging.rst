Debugging
---------

Using PDB to Debug Your Application
+++++++++++++++++++++++++++++++++++

``pdb`` is an interactive tool that comes with Python, which allows you to
break your program at an arbitrary point, examine values, and step through
code.  It's often much more useful than print statements or logging
statements to examine program state.

See the video at http://marakana.com/forums/python/python/423.html to learn
how to start to use it.  The video describes using ``pdb`` in a command-line
program, however, as long as you run your Pyramid application in the
foreground (without the ``--daemon`` flag to ``paster serve``), you can place
a ``pdb.set_trace()`` statement in your Pyramid application at a place where
you'd like to examine program state.  When you issue a request to the
application, and that point in your code is reached, you will be dropped into
the ``pdb`` debugging console within the terminal that you used to start your
application.

