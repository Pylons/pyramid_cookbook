Conditional HTTP
%%%%%%%%%%%%%%%%

Pyramid requests and responses support conditional HTTP requests via the
``ETag`` and ``Last-Modified`` header. It is useful to enable this for an
entire site to save on bandwidth for repeated requests. Enabling ``ETag``
support for an entire site can be done using a tween::

    def conditional_http_tween_factory(handler, registry):
        def conditional_http_tween(request):
            response = handler(request)

            # If the Last-Modified header has been set, we want to enable the
            # conditional response processing.
            if response.last_modified is not None:
                response.conditional_response = True

            # We want to only enable the conditional machinery if either we
            # were given an explicit ETag header by the view or we have a
            # buffered response and can generate the ETag header ourself.
            if response.etag is not None:
                response.conditional_response = True
            elif (isinstance(response.app_iter, collections.abc.Sequence) and
                    len(response.app_iter) == 1):
                response.conditional_response = True
                response.md5_etag()

            return response
        return conditional_http_tween

The effect of this tween is that it will first check the response to determine
if it already has a ``Last-Modified`` or ``ETag`` header set. If it does, then
it will enable the conditional response processing. If the response does not
have an ``ETag`` header set, then it will attempt to determine if the response
is already loaded entirely into memory (to avoid loading what might be a very
large object into memory). If it is already loaded into memory, then it will
generate an ``ETag`` header from the MD5 digest of the response body, and
again enable the conditional response processing.
