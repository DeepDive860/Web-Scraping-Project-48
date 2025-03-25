from sqlalchemy import Column, Integer, String, create_engine, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UNDATASETS(Base):
    __tablename__ = "undataset"
    id = Column(Integer, primary_key=True)
    table_name = Column(String(500), nullable=False)
    source_url = Column(String(500), nullable=False)
    __table_args__ = (UniqueConstraint('table_name', name='uq_un_data_sets'),)
 

class UNITEDSTATESCODE(Base):
    __tablename__ = "unitedstatescode"
    id = Column(Integer, primary_key=True)
    header_name = Column(String(500), nullable=False)
    source_link = Column(String(500), nullable=False)
    source_pdf = Column(String(500), nullable=False)


engine = create_engine('mysql+pymysql://root:HAHAHA@localhost/governmentdata')
Base.metadata.create_all(engine)






