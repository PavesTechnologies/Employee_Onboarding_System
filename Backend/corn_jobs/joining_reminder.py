import datetime
from Backend.DAL.dao.offerletter_dao import OfferLetterDAO
from Backend.DAL.utils.database import AsyncSessionLocal
from .corn_email import send_joinning_email as send_email

# import asyncio


async def send_joining_date_reminders():

    today = datetime.date.today()
    # three_days_later = today + datetime.timedelta(days=3)

    async with AsyncSessionLocal() as session:

        dao = OfferLetterDAO(session)

        users = await dao.get_upcoming_joinings()  # if you add this method

        if not users:
            return

        subject = "Upcoming Employee Joinings (Next 3 Days)"

        rows = ""

        for user in users:
            rows += f"""
        Name: {user.first_name} {user.last_name}
        Email: {user.mail}
        Joining Date: {user.joining_date}
        """

        body = f"""
        Dear Management Team,

        The following employees are scheduled to join in the next 3 days:

        {rows}

        Please ensure that onboarding arrangements are completed.

        Regards,
        HR Automation System
        """
        try:
            send_email("sumiyapatan2@gmail.com", subject, body)
            print(f"📧 Sent to sumiyapatan2@gmail.com")

        except Exception as e:
            print(f"❌ Email failed: {e}")


# may be used in future if we want to run the job in the main filed
# def run_job():
#     loop = asyncio.get_event_loop()
#     loop.create_task(send_joining_date_reminders())
