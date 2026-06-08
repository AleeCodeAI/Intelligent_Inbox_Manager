from utils.color import Logger
from utils.delete_calendar import delete_calendar
from database import delete_email
from schemas import DeleteAppointment as delete_appointment_schema
import logging 

logging.basicConfig(level=logging.INFO, format="%(message)s")

class DeleteAppointment(Logger):
    name: str = "DeleteAppointment"
    colro: str = Logger.PINK

    def delete_appointment(self, data: delete_appointment_schema):
        try:
            self.log(f"Deleting appointment from database with gmail id: {data.gmail_id}")
            delete_email(gmail_id=data.gmail_id)

            self.log(f"Deleting appointment event from calendar with event id: {data.event_id}")
            delete_calendar(event_id=data.event_id)

        except Exception as e:
            self.log(f"deletion of appointment failed with error: {e}")
            raise 