from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DB_URL = "postgresql://postgres.mjqyvtlejtkjyfhpfqpe:LKzKcusHMOzErl0s@aws-0-eu-west-2.pooler.supabase.com:5432/postgres"

engine = create_engine(DB_URL)

SessionLocal = sessionmaker(autocommut=False, autoflush=False, bind=engine)

Base = declarative_base()
