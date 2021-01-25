from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models_mod


class Database:
    def __init__(self, db_url):
        engine = create_engine(db_url)
        models_mod.Base.metadata.create_all(bind=engine)
        self.maker = sessionmaker(bind=engine)

    def get_or_create(self, session, model, **data):
        db_data = session.query(model).filter(model.url == data["url"]).first()
        if not db_data:
            db_data = model(**data)
        return db_data

    def create_post(self, data):
        session = self.maker()
        author = self.get_or_create(session, models_mod.Author, **data["author"])
        post = self.get_or_create(session, models_mod.Post, **data["post_data"], author=author)
        tags = map(lambda tag_data: self.get_or_create(
            session, models_mod.Tag, **tag_data
        ), data["tags"])
        comments = map(lambda comment_data: self.get_or_create(
            session, models_mod.Comment, **comment_data
        ), data["comments"])

        post.tags.extend(tags)
        post.comments.extend(comments)

        session.add(post)
        try:
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()
