# list of imap servers of some email providers
email_imap_servers = {
    "gmail": "imap.gmail.com",
    "yahoo": "imap.mail.yahoo.com",
    "outlook": "imap-mail.outlook.com",
    "office365": "outlook.office365.com"
}

# list of smtp servers of some email providers
email_smtp_servers = {
    "gmail": "smtp.gmail.com",
    "yahoo": "smtp.mail.yahoo.com",
    "outlook": "smtp-mail.outlook.com",
    "office365": "smtp.office365.com",
}

# list of email header content to ignore in body of email
email_content_to_ignore = [
    "From: ",
    "Mime-Version: ",
    "Date: ",
    "Subject: ",
    "Message-Id: ",
    "To: ",
    "X-Mailer: ",
]


def find_string_in_list(string_to_find: str, input_list: list, return_index: bool = False, last_index: bool = False) -> str | int | None:
    """
    Returns a string found in a list.
    If 'return_index' is specified, it returns the index of the string in the list instead.

    The arguments are:
    string_to_find : The string you would like to find.
    inout_list : A list you would like to check.
    return_index[Optional] : Whether you would like to return the found index of the string or not. Default is False.
    last_index[Optional]: Whether you would like to return the last found index of the string or not. Default is False

    For example:
    output = find_string_in_list('a', ['a','b','c'])
    print(output) -> 'a'

    output = find_string_in_list('a', ['a','b','c'], return_index=True)
    print(output) -> 0

    """

    found_indexes = []

    for index, content in enumerate(input_list):

        if content.find(string_to_find) == 0:
            if return_index:
                found_indexes.append(index)
                continue
            return content

    if return_index and len(found_indexes) > 0:
        if last_index:
            return found_indexes[-1]
        return found_indexes[0]

    return None
