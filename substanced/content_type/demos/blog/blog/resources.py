import colander
import datetime
import time

import deform.widget

from persistent import Persistent

from pyramid.security import (
    Allow,
    Everyone,
    )

from substanced.content import content
from substanced.folder import Folder
from substanced.property import PropertySheet
from substanced.root import Root
from substanced.schema import (
    Schema,
    NameSchemaNode,
    )
from substanced.util import renamer


class BinderSchema(Schema):
    name = NameSchemaNode(
        editing=lambda c, r: r.registry.content.istype(c, 'Binder')
        )
    title = colander.SchemaNode(
        colander.String(),
        )

class BinderPropertySheet(PropertySheet):
    schema = BinderSchema()

@content(
    'Binder',
    propertysheets=(
        ('Basic', BinderPropertySheet),
        ),
    icon='icon-home',
    )
class Binder(Folder):
    title = ''

    def __init__(self, title):
        Folder.__init__(self)
        self.title = title

    @property
    def sdi_title(self):
        return self.title

    @sdi_title.setter
    def sdi_title(self, value):
        self.title = value

    def after_create2(self, inst, registry):
        acl = getattr(self, '__acl__', [])
        acl.append((Allow, Everyone, 'view'))
        self.__acl__ = acl

@colander.deferred
def now_default(node, kw):
    return datetime.date.today()

class BlogEntrySchema(Schema):
    name = NameSchemaNode(
        editing=lambda c, r: r.registry.content.istype(c, 'BlogEntry')
        )
    title = colander.SchemaNode(
        colander.String(),
        )
    entry = colander.SchemaNode(
        colander.String(),
        widget = deform.widget.TextAreaWidget(rows=20, cols=70),
        )
    format = colander.SchemaNode(
        colander.String(),
        validator = colander.OneOf(['rst', 'html']),
        widget = deform.widget.SelectWidget(
            values=[('rst', 'rst'), ('html', 'html')]),
        )
    pubdate = colander.SchemaNode(
       colander.DateTime(default_tzinfo=None),
       default = now_default,
       )

class BlogEntryPropertySheet(PropertySheet):
    schema = BlogEntrySchema()

@content(
    'Blog Entry',
    icon='icon-book',
    add_view='add_blog_entry',
    propertysheets=(
        ('Basic', BlogEntryPropertySheet),
        ),
    catalog=True,
    tab_order=('properties', 'contents', 'acl_edit'),
    )
class BlogEntry(Folder):

    name = renamer()

    def __init__(self, title, entry, format, pubdate):
        Folder.__init__(self)
        self.modified = datetime.datetime.utcnow()
        self.title = title
        self.entry = entry
        self.pubdate = pubdate
        self.format = format
        self['attachments'] = Folder()
        self['comments'] = Folder()

    def add_comment(self, comment):
        while 1:
            name = str(time.time())
            if not name in self:
                self['comments'][name] = comment
                break

class CommentSchema(Schema):
    commenter = colander.SchemaNode(
       colander.String(),
       )
    text = colander.SchemaNode(
       colander.String(),
       )
    pubdate = colander.SchemaNode(
       colander.DateTime(),
       default = now_default,
       )

class CommentPropertySheet(PropertySheet):
    schema = CommentSchema()

@content(
    'Comment',
    icon='icon-comment',
    add_view='add_comment',
    propertysheets = (
        ('Basic', CommentPropertySheet),
        ),
    catalog = True,
    )
class Comment(Persistent):
    def __init__(self, commenter_name, text, pubdate):
        self.commenter_name = commenter_name
        self.text = text
        self.pubdate = pubdate

class BlogSchema(Schema):
    """ The schema representing the blog root. """
    title = colander.SchemaNode(
        colander.String(),
        missing=''
        )
    description = colander.SchemaNode(
        colander.String(),
        missing=''
        )

class BlogPropertySheet(PropertySheet):
    schema = BlogSchema()

@content(
    'Root',
    icon='icon-home',
    propertysheets = (
        ('', BlogPropertySheet),
        ),
    after_create= ('after_create', 'after_create2')
    )
class Blog(Root):
    title = ''
    description = ''

    @property
    def sdi_title(self):
        return self.title

    @sdi_title.setter
    def sdi_title(self, value):
        self.title = value
    
    def after_create2(self, inst, registry):
        acl = getattr(self, '__acl__', [])
        acl.append((Allow, Everyone, 'view'))
        self.__acl__ = acl
