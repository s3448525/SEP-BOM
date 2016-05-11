import sqlalchemy
from sqlalchemy.orm import scoped_session, sessionmaker
from contextlib import contextmanager
from model import schema


class ORM(object):

    def __init__(self, host, port, username, password):
        self.engine = sqlalchemy.create_engine('postgresql://%s:%s@%s:%d/feva' % (username, password, host, port), pool_size=20, max_overflow=100)
        self.session_factory = sessionmaker(bind=self.engine)
        schema.metadata.create_all(self.engine)
        # Create a scoped_session that helps create & reuse a session for each
        # web request or application execution.
        # see http://flask.pocoo.org/docs/0.10/patterns/sqlalchemy/
        self.session = scoped_session(self.session_factory)

    def shutdown_session(self):
        '''
        Shutdown the session inside the scoped_session registry.
        Usefull at the end of a webserver request.
        '''
        self.session.remove()

    @contextmanager
    def transaction_session(self):
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
