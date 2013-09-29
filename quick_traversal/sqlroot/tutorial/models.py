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


class Root(Base):
    __name__ = ''
    __parent__ = None
    __tablename__ = 'root'
    uid = Column(Integer, primary_key=True)
    title = Column(Text, unique=True)


def root_factory(request):
    return DBSession.query(Root).one()