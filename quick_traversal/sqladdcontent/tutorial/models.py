from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey,
    )

from .sqltraversal import Node


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
