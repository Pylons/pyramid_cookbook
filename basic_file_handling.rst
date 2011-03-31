Basic File Handling
-------------------

There are two parts necessary for file handling.  The first is to make sure you have a form that's been setup correctly to accept files.  This means adding ``enctype`` attribute to your ``form`` element with the value of ``multipart/form-data``.  A very simple example would be a form that accepts an mp3 file.  Notice we've setup the form as previously explained and also added an ``input`` element of the ``file`` type.

.. code-block:: html
    :linenos:
    
    <form action='.' method="post" accept-charset="utf-8" enctype="multipart/form-data"> 
        
        <label for="mp3">Mp3</label> 
        <input id="mp3" name="mp3" type="file" value="" /> 
        
        <input type='submit' value="submit" /> 
    </form>

The second part is handling the file upload in your view callable.  The uploaded file is added to the request object as a ``cgi.FieldStorage`` object accessible through the request.params multidict.  The two properties we're interested in are the ``file`` and ``filename`` and we'll use those to write the file to disk.

.. code-block:: python
    :linenos:
    
    # Note that there are many form libraries available for Pyramid
    # so in this example all form handling besides the actual file handling
    # is pseudo code.
    
    def store_mp3_view(request):
        form = MP3Form(request.params)
        
        if request.method == 'POST' and form.validate():
        
            # param.filename contains the name of the file in string format.
            filename = request.params['mp3'].filename
            
            # param.file contains the actual file data which needs to be
            # written to stored somewhere.            
            file_data = request.params['mp3'].file
            
            # Using the filename like this without cleaning it is very
            # insecure so please keep that in mind when writing your own
            # file handling.
            file_path = '/tmp/%s' % filename
            file_obj = open(filepath, 'w')
            
            # Finally write the object to disk
            file_obj.write(file_data)
            file_obj.close()
            
            return HTTPFound(location=route_url('mp3_view', request))
            
        return {'form': form}
        
   