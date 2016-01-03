from sqlalchemy import (
    Column,
    Integer,
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
from sqlalchemy.util import classproperty
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


def root_factory(request):
    return DBSession.query(Node).filter_by(parent_id=None).one()


class Node(Base):
    __tablename__ = 'node'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(50), nullable=False)
    parent_id = Column(Integer, ForeignKey('node.id'))
    children = relationship("Node",
                            backref=backref('parent', remote_side=[id])
    )
    type = Column(String(50))

    @classproperty
    def __mapper_args__(cls):
        return dict(
            polymorphic_on='type',
            polymorphic_identity=cls.__name__.lower(),
            with_polymorphic='*',
        )

    def __setitem__(self, key, node):
        node.name = u(key)
        if self.id is None:
            DBSession.flush()
        node.parent_id = self.id
        DBSession.add(node)
        DBSession.flush()

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
