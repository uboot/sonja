from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, sessionmaker

Base = declarative_base()

class Repo(Base):
    __tablename__ = "repos"

    id = Column(Integer, primary_key=True)
    url = Column(String(255), nullable=False)

    def __init__(self, url=None):
        self.url = url

    def __repr__(self):
        return "Repo(%r)" % (self.url)

class Store(object):
    def __init__(self):
        engine = create_engine("mysql+mysqldb://root:secret@127.0.0.1/conan-ci")
        Base.metadata.create_all(engine)

        Session = sessionmaker(bind=engine)
        session = Session()
        repo = Repo("https://github.com/uboot/conan-ci")
        try:
            session.add(repo)
            session.commit()
        except:
            session.rollback()
