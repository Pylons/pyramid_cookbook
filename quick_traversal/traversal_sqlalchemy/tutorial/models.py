from sqlalchemy import (
    Column,
    Integer,
    Text,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(
    sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True)
    body = Column(Text)

    @property
    def __name__(self):
        return self.id

class Folder(Base):
    __tablename__ = 'folders'
    id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True)

    @property
    def __name__(self):
        return self.id

    def __setitem__(self, key, node):
        key = node.name = unicode(key)
        self.children.append(node)

class Root(object):
    def __init__(self, request):
        pass