from Backend.Business_Layer.utils.email_utils import send_joining_email

TEST_RECIPIENT = "221FA20021@gmail.com"


def main():
    print("\n--- Sending Joining Letter Email ---")

    send_joining_email(
        to_email=TEST_RECIPIENT,
        name="Preethika",
        joining_date_str="10 September 2026",
        location="Hyderabad",
        reporting_time="10:00 AM",
        department="Software Development",
        reporting_manager="HR Team",
        custom_message="Welcome to Paves Technologies.",
    )


if __name__ == "__main__":
    main()