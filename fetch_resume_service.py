import yaml
import logging
import imaplib
import email
import os
from email.header import decode_header


ATTACHMENT_DIR = "downloaded_attachments"


def load_credentials(filepath):
    with open(filepath, 'r') as file:
        credentials = yaml.safe_load(file)
        return credentials['user'], credentials['password']


def connect_to_gmail_imap(user, password):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(user, password)
    mail.select("inbox")
    return mail


def clean_filename(filename):
    return filename.replace("/", "_").replace("\\", "_")

def list_matched_email_subjects(mail, subject):
    status, messages = mail.search(None, f'(SUBJECT "{subject}")')
    email_ids = messages[0].split()

    print(f"\nMatched Emails for Subject Keyword: '{subject}'\n")

    for index, email_id in enumerate(email_ids, start=1):
        status, msg_data = mail.fetch(email_id, "(RFC822)")
        raw_email = msg_data[0][1]

        msg = email.message_from_bytes(raw_email)

        subject_header = msg.get("Subject", "No Subject")
        decoded_subject, encoding = decode_header(subject_header)[0]

        if isinstance(decoded_subject, bytes):
            decoded_subject = decoded_subject.decode(encoding or "utf-8")

        print(f"{index}. {decoded_subject}")


def download_attachments_by_subject(mail, subject):
    os.makedirs(ATTACHMENT_DIR, exist_ok=True)

    status, messages = mail.search(None, f'(SUBJECT "{subject}")')
    email_ids = messages[0].split()

    print(f"Found {len(email_ids)} emails matching subject: {subject}")

    for email_id in email_ids:
        status, msg_data = mail.fetch(email_id, "(RFC822)")
        raw_email = msg_data[0][1]

        msg = email.message_from_bytes(raw_email)

        for part in msg.walk():
            if part.get_content_disposition() == "attachment":
                filename = part.get_filename()

                if filename:
                    decoded_name, encoding = decode_header(filename)[0]
                    if isinstance(decoded_name, bytes):
                        decoded_name = decoded_name.decode(encoding or "utf-8")

                    safe_name = clean_filename(decoded_name)
                    file_path = os.path.join(ATTACHMENT_DIR, safe_name)

                    with open(file_path, "wb") as f:
                        f.write(part.get_payload(decode=True))

                    print(f"Saved: {file_path}")


def main():
    user, password = load_credentials("credentials.yaml")
    mail = connect_to_gmail_imap(user, password)
    SUBJECT_TO_FILTER = "Resume"
    list_matched_email_subjects(mail, SUBJECT_TO_FILTER)
    download_attachments_by_subject(mail, SUBJECT_TO_FILTER)


if __name__ == "__main__":
    main()
