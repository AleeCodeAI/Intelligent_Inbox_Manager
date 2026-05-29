
from database.base import Base
from database.session import engine

# Import all models so SQLAlchemy knows them
from database.models.email import Email
from database.models.processing import EmailProcessing
from database.models.basic import BasicEmailData
from database.models.priority import PriorityEmailData
from database.models.appointment import Appointment
from database.models.nonbusiness import NonBusinessEmailData

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()