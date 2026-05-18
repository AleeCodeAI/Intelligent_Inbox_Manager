from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from configs import MainSettings

settings = MainSettings()

engine = create_engine(settings.POSTGRESQL_URL, echo=False)
print(f"Connected to database: {settings.POSTGRESQL_URL}")
SessionLocal = sessionmaker(bind=engine)