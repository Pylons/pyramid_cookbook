Basic File Handling
-------------------

There are two parts necessary for file handling.  The first is to make sure
you have a form that's been setup correctly to accept files.  This means
adding ``enctype`` attribute to your ``form`` element with the value of
``multipart/form-data``.  A very simple example would be a form that accepts
an mp3 file.  Notice we've setup the form as previously explained and also
added an ``input`` element of the ``file`` type.

.. code-block:: html
    :linenos:
    
    <form action="/store_mp3_view" method="post" accept-charset="utf-8" 
          enctype="multipart/form-data"> 
        
        <label for="mp3">Mp3</label> 
        <input id="mp3" name="mp3" type="file" value="" /> 
        
        <input type="submit" value="submit" /> 
    </form>

The second part is handling the file upload in your view callable (above,
assumed to answer on ``/store_mp3_view``).  The uploaded file is added to the
request object as a ``cgi.FieldStorage`` object accessible through the
``request.POST`` multidict.  The two properties we're interested in are the
``file`` and ``filename`` and we'll use those to write the file to disk.

.. code-block:: python
   :linenos:
    
    import os
    from pyramid.response import Response

    def store_mp3_view(request):
        mp3 = request.POST['mp3']
        # ``filename`` contains the name of the file in string format.
        filename = request.POST['mp3'].filename
        
        # ``input_file`` contains the actual file data which needs to be
        # stored somewhere.            
        input_file = request.POST['mp3'].file

        # Using the filename like this without cleaning it is very
        # insecure so please keep that in mind when writing your own
        # file handling.
        file_path = os.path.join('/tmp', 'filename')
        output_file = open(filepath, 'wb')
        
        # Finally write the data to the output file
        input_file.seek(0)
        while 1:
            data = input_file.read(2<<16)
            if not data:
                break
            output_file.write(data)
        file_obj.close()

        return Response('OK')
        
      
File Handling in Practice        
-------------------------

The previous example was simply to illustrate the basics of accepting files and handling them with a view callable.  In practice there are a few issues surrounding file handling that one should be aware of.

Memory Leaks
============

When accepting files there's always the potential for someone to upload a file larger than your server has RAM to handle.  A simple way to solve this is to use a file buffer.  Consuming the file in smaller chunks will keep your application from running out of memory when consuming large files.  Below we'll create a generator named file_buffer and use that to store an incoming as it's uploaded.

.. code-block:: python
   :linenos:
    
    def file_buffer(file_obj, chunk_size=1024):
        """
        Reads a file object yielding the specified chunk size. Default chunk
        size is 1024.
        """
        
        file_obj.seek(0)
        
        while True:
            chunk = file_obj.read(chunk_size)
            if not chunk:
                break
            yield chunk

    # Our incoming file.
    input_file = request.POST['mp3'].file
    
    # Opening a new file object that will be written to disk.
    output_file = open(final_dest, 'wb')
    
    # Iterate over our file_buffer generator and write the results to our output_file.
    for chunk in file_buffer(input_file):
        output_file.write(chunk)
        
    output_file.close()


Temporary Location
==================

TODO

Secure Filenames
================

TODO