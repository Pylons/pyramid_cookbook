JSON Web Tokens (JWT) and Security Policy
=========================================

Introduction
############
This guide is for Pyramid 2.0 and above. `JWT (JSON Web Token) <https://jwt.io/>`_ is a standard of authentication token, mainly used for securing web APIs. 
This small tutorial aims to explain why a JWT is useful and how we can use it with Pyramid,
to create a secure authentication system for an API server, coupled with Pyramid's built in 
`security policy. <https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/security.html>`_ 

Pre 2.0 Pyramid
###############

Before Pyramid 2.0 and the new style security policy, there was a great library 
`pyramid_jwt <https://github.com/wichert/pyramid_jwt>`_  that handled all of this automatically, the method to create a JWT has been taken from that library.
If you have a codebase pre Pyramid 2.0 and want to learn more about the changes and how to upgrade to a security policy, please check out the
`upgrading authentication/authorization <https://docs.pylonsproject.org/projects/pyramid/en/latest/whatsnew-2.0.html#upgrading-auth-20>`_.

Workflow
########
Below is a brief overview of what an JWT based login and authorization looks like with a JWT based security policy.
For the example below the "API Server" is this example Pyramid application.

1. API Server creates a JWT token
2. Token is sent back to user/front end website
3. Each subsequent request from the "front end" sends this token as a header
4. API server then evaluates the JWT (checks it has not expired, and that it can be decoded with a secret)
5. If all is OK Pyramid can then grant access to the `protected 
   view <https://docs.pylonsproject.org/projects/pyramid/en/latest/glossary.html#term-permissions>`_
   with this JWT

Generating the JWT
###################
It may be "out of scope" for your application to generate the JWT, but usually it's required,
so I will include an example here, using the `PyJWT <https://pyjwt.readthedocs.io/en/stable/>`_ library.

So, let's start off with a basic Pyramid login view that takes a username and password from the request.

.. code-block:: python

    import jwt
    # some global variables we will call later
    JWT_SECRET = "myJWTsecret100#"
    JWT_ALGO = "HS512"
    @view_config(route_name='login', request_method='POST', renderer='json')
    def login(request):
        #Login view, takes basic inputs then returns JWT
        username = request.json_body['username']
        password = request.json_body['password']
        # test_login is an example, you will need to implement this
        user = test_login(request, username, password)
        if user:
            token = create_token(
                    user_id=999,
                    permissions=['view', 'edit'],
                    user_name='joe',
                    key=JWT_SECRET,
                    expiration=set_token_expiry(),
                )
            return {
                'result': 'ok',
                'token': token
            }
        # No valid user
        response = Response(None)
        response.status_int = 403
        return None



If we look at this a bit further, we can see we have a function called ``create_token`` and another called ``set_token_expiry``.
We will start with the expiry, as this is a key function of the JWT. Once the token is expired, it is no longer meant to be used.
When creating a JWT token, expiry is meant as in "how many seconds from now". 
There is no right or wrong method to work out when to expire JWT, but for argument's sake, let's say we want them to last a week.
I also like to set my tokens to expire at a time when they are unlikely to be being used, to save a user potentially getting a broken session.

.. code-block:: python

    def set_token_expiry():
        ''' We want to set the token expiry to be 7 days
            but at 3am, this should stop users been thrown out
            of a session during normal working time
        '''
        now = datetime.datetime.now()
        expiry = now + datetime.timedelta(days=8)
        expiry_midnight = expiry.replace(hour=3, minute=0, second=0)
        # Calculate the difference in seconds between two dates
        seconds_to_expire = (expiry_midnight-now).total_seconds()
        return seconds_to_expire



Now we have all of the information we need to create a basic JWT token.
There are more examples of this online, but the below covers us for now.

.. code-block:: python

    def create_token(key, user_id, permissions, user_name, expiration, audience=None):
        # create an empty dict
        payload = {}
        # set the expiration
        payload["exp"] = expiration
        if audience:
            # audience claims are out of scope for this tutorial, but
            # a useful placeholder to expand this code
            payload["aud"] = audience
        # 'sub' is the primary contents of a JWT, so I user "user_id" here
        payload['sub'] = user_id
        # available permissions associated to this user or JWT, not required here
        # but helpful to explain how they work
        payload['permissions'] = permissions
        # again an extension of the token, we will explain further on why only user_id
        # is required, but passing back to the frontend can be very useful.
        payload['user_name'] = user_name
        token = jwt.encode(payload, key, algorithm=JWT_ALGO, json_encoder=None)
        if not isinstance(token, str):  # Python3 unicode madness
            token = token.decode("ascii")
        return token

Now the token should look something like the following.

.. code-block:: text

    eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjY1MDM5Ny4wLCJzdWIiOjk5OSwicGVybWlzc2lvbnMiOlsidmlldyIsImVkaXQiXSwidXNlcl9uYW1lIjoiam9lIn0.dTCQxCorZtzIExeUtxB49_JAKljS9M8FZEhBvT_JPudzGuOyTPGYpTaxgaYWEjvnMG1m_kKvASJcn77Klgb9lQ

We can work onto the next phase, intercepting this token in the security policy and evaluating it.
It is important to note that all data inside a JWT is available for anyone to view it.
All the secret does is verify the token has not been manipulated, so NEVER send information inside a JWT that you don't mind getting out.


Evaluating with Pyramid 
#######################

Now that we have sent the JWT token to our front-end application, we can presume that it will get sent back to the Pyramid application 
(`in the header <https://docs.pylonsproject.org/projects/pyramid/en/latest/api/request.html#pyramid.request.Request.authorization>`_)
for evaluation to access protected views. So we will create a security policy to handle this.

Let's assume we have a protected view.

.. code-block:: python

    @view_config(route_name='view_basket', renderer='json', permission="view")
    def view_basket(request):

Only a JWT token that has the permission ``view`` *should* be able to access this view, so how does this work?

Before we delve into our security policy, we need to be able to decode our JWT token.
Here is an example of how this *could* be done.
You can read more on the `PyJWT Docs <https://pyjwt.readthedocs.io/en/stable/>`_.

.. code-block:: python

    def decode_jwt_token(token, secret):
        ''' Function to decode our JWT token
        '''
        try:
            decode_token = jwt.decode(
                token,
                secret,
                algorithms=JWT_ALGO,
                leeway=0,
                audience=None,
            )
            return {
                'user_id': decode_token['sub'],
                'user_name': decode_token['user_name'],
                'permissions': decode_token['permissions']
            }
        except jwt.exceptions.InvalidTokenError as e:
            # Invalid token detected
            return None

If our token is valid and not expired, we will return some information, such as ``user_id`` and available permissions, if not, return ``None``.

So we can now write a nice and concise security policy to match up with this decode function.

.. code-block:: python

    class MySecurityPolicy:
        def __init__(self, secret):
            self.helper = AuthTktCookieHelper(secret)

        def permits(self, request, context, permission):
            ''' permission argument comes from Pyramid core, each time a view
                protected with permission="foo" is called, so is this function
            '''
            # permission is the value of the permission set in the view
            # we are trying to access
            if request.authorization:
                # or wherever the JWT token is present in your request
                token = request.authorization.params
                token_response = decode_jwt_token(token, JWT_SECRET)
                if token_response == None:
                    # Token is invalid, expired, bad secret or corrupt
                    reason = "Invalid JWT token"
                    return Denied(reason)
                else:
                    if permission in token_response['permissions']:
                        reason = "User matched role, allow"
                        return Allowed(reason)
                    else:
                        denied_reason = "No role matched"
                        return Denied(reason)
            reason = "No Authorization present"
            return Denied(denied_reason)

There you go, you now have a working security policy with JWT and Pyramid.

Let's clean this up a bit though, as in reality, you only *need* to send the ``user_id`` as the ``'sub'`` in the JWT token,
and the rest *should probably* be accessed as shown. 

.. code-block:: python

    class MySecurityPolicy:
        def __init__(self, secret):
            self.helper = AuthTktCookieHelper(secret)

        def identity(self, request):
            # Return a DB user object
            if request.authorization:
                token = request.authorization.params
                token_response = decode_jwt_token(token, JWT_SECRET)
                if token_response == None:
                    return None
                else:
                    user = request.DBSession.query(User).\
                        filter(User.id == token_response['sub']).first()
                    return user
                
        def permits(self, request, context, permission):
            identity = request.identity
            if identity.permissions:
                # now we can evaluate said permissions
                    if permission in identity.permissions:
                        # same logic as before

The obvious advantage to the above approach is that the user permission can be revoked in the database and user access is denied immediately.
If the permission is stored in the token, it will remain active until such time as the token expires. 
The above method will increase database calls significantly, as one will be made to the ``User`` table, for each request.
It is important to assess the security needs of your application and the merits to each approach before production use.

Hopefully the examples in this tutorial will help you understand how to protect your API views with JWT and why it might be useful.


