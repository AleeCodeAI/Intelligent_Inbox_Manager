# ==============================================================================
# Inserting data into the database repositories
# ==============================================================================

from .repositories.insert_repos.basic_repo import insert_basic, mark_basic_reviewed
from .repositories.insert_repos.email_repo import insert_email, get_email_by_thread, get_email_by_gmail_id
from .repositories.insert_repos.nonbusiness_repo import insert_nonbusiness, mark_nonbusiness_reviewed
from .repositories.insert_repos.priority_repo import insert_priority, mark_priority_reviewed
from .repositories.insert_repos.processing_repo import insert_processing
from .repositories.insert_repos.appointment_repo import insert_appointment

# ==============================================================================
# Querying data from the database repositories
# ==============================================================================

from .repositories.retrieval_repos.get_basic_emails import get_basic_manual_pending
from .repositories.retrieval_repos.get_priority_emails import get_priority_unreviewed
from .repositories.retrieval_repos.get_nonbusiness_emails import get_nonbusiness_unreviewed
from .repositories.retrieval_repos.get_all_emails import get_all_emails
from .repositories.retrieval_repos.get_processed_emails import get_all_email_processing
from .repositories.retrieval_repos.get_all_appointments import get_all_appointments