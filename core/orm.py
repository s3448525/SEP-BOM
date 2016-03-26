import sqlalchemy
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from model import schema


class ORM(object):

    def __init__(self, host, port, username, password):
        self.engine = sqlalchemy.create_engine('postgresql://%s:%s@%s:%d/feva' % (username, password, host, port))
        self.session_factory = sessionmaker(bind=self.engine)
        schema.metadata.create_all(self.engine)


    @contextmanager
    def session_scope(self):
        """
        create a transactional scope
        see http://docs.sqlalchemy.org/en/latest/orm/contextual.html#unitofwork-contextual
        :return:
        """
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
