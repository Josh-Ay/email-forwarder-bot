import smtplib

import bs4
from dotenv import load_dotenv
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv()


def send_email(smtp_server_provider: str, recipient_address: str, email_subject: str,
               email_body: str | bs4.ResultSet) -> str:
    """
    Sends an email from one user to the other.

    The arguments are:
    smtp_server_provider : The smtp server of the sender mail address.
    recipient_address: The mail address you would like to send this mail to.
    email_subject: The subject of this email.
    email_body: The body of this email.

    """

    # creating a new smtp connection
    with smtplib.SMTP_SSL(smtp_server_provider) as connection:
        try:
            # logging in to the user account
            connection.login(os.environ.get("EMAIL_ADDRESS"), os.environ.get("PASSWORD"))

            # creating a new multipart message
            new_msg = MIMEMultipart("alternative")

            # adding headers to the multipart message
            new_msg['Subject'] = email_subject
            new_msg['From'] = os.environ.get("EMAIL_ADDRESS")
            new_msg['To'] = recipient_address

            # creating a html MIMEText of the 'email_body' passed above and attaching it to the new multipart message
            msg_html = MIMEText(email_body, "html")
            new_msg.attach(msg_html)

            # sending the mail
            connection.sendmail(
                from_addr=os.environ.get("EMAIL_ADDRESS"),
                to_addrs=recipient_address,
                msg=new_msg.as_string().encode('ascii')
            )

        # catch any exceptions
        except smtplib.SMTPException:
            return "Failed to forward mail"

        # show success message
        else:
            return f"Successfully forwarded mail to {recipient_address}!"
