Debugging Pyramid
+++++++++++++++++

This tutorial provides a brief introduction to using the python
debugger (``pdb``) for debugging pyramid applications.

This scenario assume you've created a Pyramid project already.  The scenario
assumes you've created a Pyramid project named ``buggy`` using the
``alchemy`` scaffold.

Introducing PDB
---------------

- This single line of python is your new friend::

    import pdb;  pdb.set_trace()

- As valid python, that can be inserted practically anywhere in a Python
  source file.  When the python interpreter hits it - execution will be
  suspended providing you with interactive control from the parent TTY.

PDB Commands
------------

- pdb exposes a number of standard interactive debugging
  commands, including::

    Documented commands (type help <topic>):
    ========================================
    EOF    bt         cont      enable  jump  pp       run      unt   
    a      c          continue  exit    l     q        s        until 
    alias  cl         d         h       list  quit     step     up    
    args   clear      debug     help    n     r        tbreak   w     
    b      commands   disable   ignore  next  restart  u        whatis
    break  condition  down      j       p     return   unalias  where 
    
    Miscellaneous help topics:
    ==========================
    exec  pdb
    
    Undocumented commands:
    ======================
    retval  rv

Debugging Our ``buggy`` App
---------------------------

- Back to our demo ``buggy`` application we generated from the ``alchemy``
  scaffold, lets see if we can learn anything debugging it.

- The traversal documentation describes how pyramid first acquires a root
  object, and then descends the resource tree using the ``__getitem__`` for
  each respective resource.

Huh?
----

- Let's drop a pdb statement into our root factory object's ``__getitem__``
  method and have a look.  Edit the project's ``models.py`` and add the
  aforementioned ``pdb`` line in ``MyModel.__getitem__``::

    def __getitem__(self, key):
        import pdb; pdb.set_trace()
        session = DBSession()
        # ...

- Restart the Pyramid application, and request a page.  Note the request
  requires a path to hit our break-point::

    http://localhost:6543/   <- misses the break-point, no traversal
    http://localhost:6543/1  <- should find an object
    http://localhost:6543/2  <- does not

- For a very simple case, attempt to insert a missing key by default.  Set
  item to a valid new MyModel in ``MyRoot.__getitem__`` if a match isn't
  found in the database::

        item = session.query(MyModel).get(id)
        if item is None:
            item = MyModel(name='test %d'%id, value=str(id))  # naive insertion

- Move the break-point within the if clause to avoid the false positive hits::

        if item is None:
            import pdb; pdb.set_trace()
            item = MyModel(name='test %d'%id, value=str(id))  # naive insertion

- Run again, note multiple request to the same id continue to create
  new MyModel instances.  That's not right!

- Ah, of course, we forgot to add the new item to the session.  Another line
  added to our ``__getitem__`` method::

        if item is None:
            import pdb; pdb.set_trace()
            item = MyModel(name='test %d'%id, value=str(id))
            session.add(item)

- Restart and test.  Observe the stack; debug again.  Examine the item
  returning from MyModel::

    (pdb) session.query(MyModel).get(id)

- Finally, we realize the item.id needs to be set as well before adding::

        if item is None:
            item = MyModel(name='test %d'%id, value=str(id))
            item.id = id
            session.add(item)

- Many great resources can be found describing the details of using
  pdb.  Try the interactive ``help`` (hit 'h') or a search engine near
  you.

.. note:: There is a well known bug in ``PDB`` in UNIX, when user cannot 
  see what he is typing in terminal window after any interruption during 
  ``PDB`` session (it can be caused by ``CTRL-C`` or when the server restarts 
  automatically). This can be fixed by launching any of this commands in broken 
  terminal: ``reset``, ``stty sane``. Also one can add one of this commands into
  ``~/.pdbrc`` file, so they will be launched before ``PDB`` session::

          from subprocess import Popen
          Popen(["stty", "sane"])


