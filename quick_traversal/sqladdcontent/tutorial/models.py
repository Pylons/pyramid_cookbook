from sqlalchemy import (
    Column,
    Integer,
    Text,
    Unicode,
    ForeignKey,
    String
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref
    )

from sqlalchemy.orm.exc import NoResultFound

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(
    sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

def u(s):
    # Backwards compatibility for Python 3 not having unicode()
    try:
        return unicode(s)
    except NameError:
        return str(s)

class Node(Base):
    __tablename__ = 'node'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(50), nullable=False)
    parent_id = Column(Integer, ForeignKey('node.id'))
    children = relationship("Node",
                            backref=backref('parent', remote_side=[id])
    )
    type = Column(String(50))
    __mapper_args__ = dict(
        polymorphic_on=type,
        polymorphic_identity='node',
        with_polymorphic='*'
    )


    def __setitem__(self, key, node):
        node.name = u(key)
        DBSession.add(node)
        DBSession.flush()
        node.parent_id = self.id

    def __getitem__(self, key):
        try:
            return DBSession.query(Node).filter_by(
                name=key, parent=self).one()
        except NoResultFound:
            raise KeyError(key)

    def values(self):
        return DBSession.query(Node).filter_by(parent=self)

    @property
    def __name__(self):
        return self.name

    @property
    def __parent__(self):
        return self.parent

    @property
    def is_empty(self):
        return self.values().count() == 0


class Root(Node):
    __tablename__ = 'root'
    __mapper_args__ = dict(
        polymorphic_identity='root',
        with_polymorphic='*',
    )
    id = Column(Integer, ForeignKey('node.id'), primary_key=True)
    title = Column(Text)


class Folder(Node):
    __tablename__ = 'folder'
    __mapper_args__ = dict(
        polymorphic_identity='folder',
        with_polymorphic='*',
    )
    id = Column(Integer, ForeignKey('node.id'), primary_key=True)
    title = Column(Text)


class Document(Node):
    __tablename__ = 'document'
    id = Column(Integer, ForeignKey('node.id'), primary_key=True)
    __mapper_args__ = dict(
        polymorphic_identity='document',
        with_polymorphic='*',
    )
    title = Column(Text)


def root_factory(request):
    return DBSession.query(Root).one()
