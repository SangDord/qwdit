from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy import create_engine

SqlAlchemyBase = declarative_base()
__factory = None


def global_init(app):
    global __factory

    if __factory:
        return
    
    print(f"Connecting to {app.config['DATABASE_URI']}")

    engine = create_engine(app.config['DATABASE_URI'],
                           **app.config['DATABASE_CONNECT_OPTIONS'])
    __factory = sessionmaker(bind=engine)

    from qwdit.models import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()