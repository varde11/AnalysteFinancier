from sqlalchemy import Column,Integer,String,DateTime,ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.types import JSON,TEXT

class Base(DeclarativeBase):
    pass

class Client(Base):
    __tablename__ = 'client'
    id_client = Column (String,primary_key=True,index=True)
    nom = Column (String,nullable=False)
    password_hash = Column(String,nullable=False)
    

class Prediction(Base):
    __tablename__ ='prediction'

    id_prediction = Column(Integer,primary_key=True,autoincrement=True,index=True)
    id_client = Column(String,ForeignKey("client.id_client"),nullable=False)
    ticket = Column (String,nullable=False)
    time_stamp = Column(DateTime,nullable=False)
    key_news = Column(JSON)
    sentiment = Column(String,nullable=False)
    notes = Column(TEXT)
    step_by_step_check = Column(TEXT,nullable=False)
    decision = Column(String,nullable=False)
    reasoning = Column(TEXT,nullable=False)
    report_detail = Column(JSON,nullable=False)

