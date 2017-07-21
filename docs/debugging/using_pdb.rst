Using PDB to Debug Your Application
+++++++++++++++++++++++++++++++++++

``pdb`` is an interactive tool that comes with Python, which allows you to
break your program at an arbitrary point, examine values, and step through
code.  It's often much more useful than print statements or logging
statements to examine program state.  You can place a ``pdb.set_trace()``
statement in your Pyramid application at a place where you'd like to examine
program state.  When you issue a request to the application, and that point
in your code is reached, you will be dropped into the ``pdb`` debugging
console within the terminal that you used to start your application.

There are lots of great resources that can help you learn PDB.

- Doug Hellmann's PyMOTW blog entry entitled "pdb - Interactive Debugger" at
  https://pymotw.com/3/pdb/ is the canonical text resource to learning PDB.

- The PyCon video presentation by Chris McDonough entitled "Introduction to
  PDB" at http://pyvideo.org/video/644/introduction-to-pdb is a good place to
  start learning PDB.

- The video at http://pyvideo.org/pycon-us-2012/introduction-to-pdb.html shows you
  how to start how to start to using pdb.  The video describes using ``pdb``
  in a command-line program.
