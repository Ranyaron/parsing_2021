from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime

Base = declarative_base()


class IdMixin:
    id = Column(Integer, autoincrement=True, primary_key=True)


class UrlMixin:
    url = Column(String, unique=True, nullable=False)


class NameMixin:
    name = Column(String, nullable=False)


post_tag = Table(
    "post_tag",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("post.id")),
    Column("tag_id", Integer, ForeignKey("tag.id"))
)


class Post(IdMixin, UrlMixin, Base):
    __tablename__ = "post"
    title = Column(String, unique=False, nullable=False)
    img_url = Column(String, unique=True, nullable=False)
    date_time = Column(DateTime, nullable=False)
    author_id = Column(Integer, ForeignKey("author.id"))
    author = relationship("Author")
    tags = relationship("Tag", secondary=post_tag)
    comments = relationship("Comment")


class Author(IdMixin, UrlMixin, NameMixin, Base):
    __tablename__ = "author"
    post = relationship("Post")


class Tag(IdMixin, UrlMixin, NameMixin, Base):
    __tablename__ = "tag"
    posts = relationship("Post", secondary=post_tag)


class Comment(IdMixin, UrlMixin, NameMixin, Base):
    __tablename__ = "comment"
    text = Column(String, unique=False, nullable=False)
    post = relationship("Post")
    post_id = Column(Integer, ForeignKey("post.id"))
