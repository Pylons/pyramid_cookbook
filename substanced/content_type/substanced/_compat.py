
try:
    STRING_TYPES = (str, unicode)
except NameError: #pragma NO COVER Python >= 3.0
    STRING_TYPES = (str,)

try:
    u = unicode
except NameError: #pragma NO COVER Python >= 3.0
    TEXT = str
    def u(x, encoding='ascii'):
        if isinstance(x, str):
            return x
        if isinstance(x, bytes):
            return x.decode(encoding)
    b = bytes
else: #pragma NO COVER Python < 3.0
    TEXT = unicode
    b = str

try:
    INT_TYPES = (int, long)
except NameError: #pragma NO COVER Python >= 3.0
    INT_TYPES = (int,)

try: # pragma: no cover Python < 3.0
    from base64 import decodebytes
    from base64 import encodebytes
except ImportError: #pragma NO COVER
    from base64 import decodestring as decodebytes
    from base64 import encodestring as encodebytes

try:
    from urllib.parse import parse_qsl
except ImportError: #pragma NO COVER
    from cgi import parse_qsl

try:
    from urllib.parse import urlsplit
except ImportError: #pragma NO COVER
    from urlparse import urlsplit
    from urlparse import urlunsplit
else: #pragma NO COVER
    from urllib.parse import urlunsplit

import string
try:
    _LETTERS = string.letters
except AttributeError: #pragma NO COVER
    _LETTERS = string.ascii_letters
del string

try: # pragma: no cover
    from functools import total_ordering
except ImportError: # pragma: no cover
    # this doesn't exist in Python < 2.7
    def total_ordering(cls): # pragma: no cover
        """Class decorator that fills in missing ordering methods"""
        convert = {
            '__lt__': [('__gt__', lambda self, other: not (self < other or self == other)),
                       ('__le__', lambda self, other: self < other or self == other),
                       ('__ge__', lambda self, other: not self < other)],
            '__le__': [('__ge__', lambda self, other: not self <= other or self == other),
                       ('__lt__', lambda self, other: self <= other and not self == other),
                       ('__gt__', lambda self, other: not self <= other)],
            '__gt__': [('__lt__', lambda self, other: not (self > other or self == other)),
                       ('__ge__', lambda self, other: self > other or self == other),
                       ('__le__', lambda self, other: not self > other)],
            '__ge__': [('__le__', lambda self, other: (not self >= other) or self == other),
                       ('__gt__', lambda self, other: self >= other and not self == other),
                       ('__lt__', lambda self, other: not self >= other)]
        }
        roots = set(dir(cls)) & set(convert)
        if not roots:
            raise ValueError('must define at least one ordering operation: < > <= >=')
        root = max(roots)       # prefer __lt__ to __le__ to __gt__ to __ge__
        for opname, opfunc in convert[root]:
            if opname not in roots:
                opfunc.__name__ = opname
                opfunc.__doc__ = getattr(int, opname).__doc__
                setattr(cls, opname, opfunc)
        return cls
