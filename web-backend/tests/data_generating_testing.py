import json
import re
import string
from random import choice, randint

from mimesis import Generic

# Initialize Mimesis Generic
generic = Generic()


def generate_test_credentials() -> tuple[str, str]:
    """
    Generate a test user with a random username and password.

    The function creates a random username using a generic username generator
    and a password that consists of a random word followed by a random number

    :return tuple(str, str): A tuple containing the generated username and password
    """
    username = generic.person.username()
    password = generic.text.word() + str(
        randint(1000, 9999)
    )  # Simple password generation

    email_username = re.sub(r"[^a-zA-Z0-9]", "", username)

    return email_username, password


def generate_random_keycloak_token(length=765) -> str:
    """
    Generate a random token

    :param int length: The length of the token to be generated (default is 765)

    :return str token: A random token as a string
    """
    # Define the characters to use in the token
    characters = string.ascii_letters + string.digits + string.punctuation
    # Generate a random token
    token = "".join(choice(characters) for _ in range(length))
    return token


def find_event_by_name(data_string: str, event_name: str) -> dict | None:
    """
    Event finding by name

    :param str data_string: The data string from database
    :param str event_name: Name of the event

    :return dict | None event: Event dictionary or None
    """
    # Convert the string to list of dictionaries
    data_list = json.loads(data_string)
    # Search for the dictionary by name
    for event in data_list:
        if event["name"] == event_name:
            return event
    return None
