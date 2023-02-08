from utils import email_imap_servers, email_smtp_servers, find_string_in_list, email_content_to_ignore
from dotenv import load_dotenv
import imaplib
import os
import datetime
from bs4 import BeautifulSoup
from messenger import send_email
import schedule
import time
from tkinter import messagebox

load_dotenv()

# your email inbox: Current valid choices are: 'gmail', 'yahoo', 'outlook', 'office365'
user_mailbox = "gmail"

# update 'None' to the subject of the mail if needed
email_subject = None

# time to check every day(24-hour format)
time_to_check_mail = "15:00"


def login_to_mail() -> imaplib.IMAP4_SSL:
    """
    Returns an authenticated IMAP instance.
    """
    # creating a new IMAP4 client instance over SSL to the email provider
    imap_client = imaplib.IMAP4_SSL(email_imap_servers.get(user_mailbox))

    # logging in to the user's email
    imap_client.login(os.environ.get("EMAIL_ADDRESS"), os.environ.get("PASSWORD"))

    # returning the authenticated IMAP4 client instance
    return imap_client


def search_for_mail_for_today(mail_connection: imaplib.IMAP4_SSL, type_of_mail: str,
                              sender_of_mail: str, subject_of_mail: str = None) -> tuple | None:
    """

    Gets the most recent mail received from an inbox for the current day(today).

    Either returns a 'tuple' containing the mail subject and its content OR 'None' if no mail is found for the day

    The arguments are:
    mail_connection: An authenticated IMAP instance.
    type_of_mail: The mail type to search for. It can either be 'FROM' or 'TO'.
    sender_of_mail: The mail address you would like to search in.
    subject_of_mail[Optional]: The subject of the email you would like to forward.

    """

    # searching for emails from the 'sender_of_mail'
    status_result_text, bytes_data = mail_connection.search(None, type_of_mail, '"{}"'.format(sender_of_mail))

    # reversing the 'bytes_data' array gotten back to have the recent messages come up first
    recent_messages = bytes_data[0].split()[::-1]

    if len(recent_messages) < 1:
        return None

    # getting the most recent message
    most_recent_message = recent_messages[0]

    # returns a single list with a tuple
    mail_message = mail_connection.fetch(most_recent_message, '(RFC822)')[1][0]

    if type(mail_message) is tuple:

        # decoding the bytes of the most recent mail
        string_content = mail_message[1].decode('utf-8')
        string_content_list = string_content.split("\n")

        # extracting the date the mail was received
        date_string_of_mail = find_string_in_list("Date: ", string_content_list)

        if date_string_of_mail is None:
            return None

        # creating variables to hold today's date and the date the last mail was received
        today, received_date = datetime.datetime.now(), date_string_of_mail.split("Date: ")[1].strip()

        if received_date.split(" ")[-1].find("(") == 0 or received_date.split(" ")[-1].find(")") == 0:
            received_date = " ".join(received_date.split(" ")[:-1])

        # formatting the date of the most recent mail
        received_date_in_proper_format = datetime.datetime.strptime(received_date, '%a, %d %b %Y %H:%M:%S %z')

        # # if no mail was received today from the sender
        if today.date() != received_date_in_proper_format.date():
            return None

        # extracting the subject of the mail
        mail_subject_str = find_string_in_list("Subject: ", string_content_list)

        if mail_subject_str is None:
            return None

        # stripping any trailing newlines from the subject of the mail
        mail_subject = mail_subject_str.split("Subject: ")[1].strip()

        if subject_of_mail is not None and mail_subject.lower() != subject_of_mail.lower():
            return None

        # creating a new soup instance
        soup = BeautifulSoup(string_content, parser="lxml", features="lxml")

        # getting the body of the mail
        mail_html_body = soup.find('body')
        message_contents = mail_html_body.findChildren(recursive=False)

        if len(message_contents) < 1:
            return mail_subject, ""

        # extracting only the html content -> version 1
        start_index_of_html_content_1 = find_string_in_list("<!DOCTYPE html", str(message_contents[0]).split("\n"),
                                                            return_index=True)
        if start_index_of_html_content_1:
            html_content = '\n'.join(str(message_contents[0]).split("\n")[start_index_of_html_content_1:])

            # returning the subject of the mail and its html content
            return mail_subject, html_content

        # extracting only the html content -> version 2
        start_index_of_html_content_2 = find_string_in_list("Content-Transfer-Encoding: ",
                                                            str(message_contents[0]).split("\n"), return_index=True,
                                                            last_index=True)
        if start_index_of_html_content_2:
            extracted_content = '\n'.join(str(message_contents[0]).split("\n")[start_index_of_html_content_2 + 1:])

            # removing email headers from the body of the email
            formatted_content_to_send = [content_line for content_line in extracted_content.split("\n") if not any(
                content_to_ignore in content_line for content_to_ignore in email_content_to_ignore)]

            content_to_send = '\n'.join(formatted_content_to_send)

            # returning the subject of the mail and its content
            return mail_subject, content_to_send

        # returning the subject of the mail and all its content
        return mail_subject, message_contents[0]

    return None


def forward_mail_for_today() -> None:
    """
    Forwards the most recent mail from an email address if any.

    Prints a string indicating the status.

    """

    print(f"Checking for mail received from {os.environ.get('INCOMING_MAIL_ADDRESS')}...")

    login_connection = login_to_mail()
    status, messages = login_connection.select("INBOX")

    # print(status, messages)     # the 'status' should be OK

    if email_subject:
        mail_for_today = search_for_mail_for_today(login_connection, 'FROM', os.environ.get('INCOMING_MAIL_ADDRESS'))
    else:
        mail_for_today = search_for_mail_for_today(login_connection, 'FROM', os.environ.get('INCOMING_MAIL_ADDRESS'),
                                                   subject_of_mail=email_subject)

    if mail_for_today is None:
        print(f"No message from {os.environ.get('INCOMING_MAIL_ADDRESS')} was received today.")
    else:
        print(f"Forwarding mail with subject of '{mail_for_today[0]}' to {os.environ.get('RECIPIENT_MAIL_ADDRESS')}...")
        email_response = send_email(email_smtp_servers.get(user_mailbox), os.environ.get("RECIPIENT_MAIL_ADDRESS"),
                                    mail_for_today[0], mail_for_today[1])
        print(email_response)
        messagebox.showinfo(title="Info", message=email_response)
        print("\nWill check next tomorrow.")


if __name__ == "__main__":
    print("========Email forwarder bot========\n")

    # waiting 2secs to mimic a system coming on delay
    time.sleep(2)
    print("Bot online.")
    print(f"Time to check everyday: {time_to_check_mail}")

    # scheduling the script to run everyday at the time specified in line 21
    schedule.every().day.at(time_to_check_mail).do(forward_mail_for_today)

    while True:
        schedule.run_pending()
