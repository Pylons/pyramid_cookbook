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

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Page(Base):
    __tablename__ = 'wikipages'
    id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True)
    body = Column(Text)

    def __init__(self, title, body):
        self.title = title
        self.body = body
