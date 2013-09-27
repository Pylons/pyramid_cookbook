from sqlalchemy import (
    Column,
    Integer,
    Text,
    Unicode,
    ForeignKey
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

    @property
    def __parent__(self):
        return self.parent


class Folder(Base):
    __tablename__ = 'folders'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(50), nullable=False)
    parent_id = Column(ForeignKey('roots.id'))
    title = Column(Text, unique=True)

    @property
    def __name__(self):
        return self.name

    @property
    def __parent__(self):
        return self.parent


class Root(Base):
    __tablename__ = 'roots'
    __name__ = ''
    __parent__ = None
    id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True)

    def __setitem__(self, key, node):
        node.name = unicode(key)
        DBSession.add(node)

    def __getitem__(self, key):
        return DBSession.query(Folder).filter_by(
            name=key, parent=self).one()


def root_factory(request):
    return DBSession.query(Root).one()
