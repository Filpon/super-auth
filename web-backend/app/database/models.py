from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Event(Base):  # pylint: disable=R0903
    """
    Events model for info and creation

    """
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    date = Column(Date)
    client_info = Column(String)

    def __repr__(self):
        return f"name={self.name}"
