import string
from random import choice, randint

from mimesis import Generic

# Initialize Mimesis Generic
generic = Generic()


def generate_test_credentials() -> tuple[str, str]:
    """
    Generate a test user with a random username and password.

    This function creates a random username using a generic username generator
    and a password that consists of a random word followed by a random number.

    :return tuple(str, str): A tuple containing the generated username and password.
    """
    username = generic.person.username()
    password = generic.text.word() + str(
        randint(1000, 9999)
    )  # Simple password generation
    return username, password


def generate_random_keycloak_token(length=765) -> string:
    """
    Generate a random token.

    :param int length: The length of the token to be generated (default is 765).
    :return str token: A random token as a string.
    """
    # Define the characters to use in the token
    characters = string.ascii_letters + string.digits + string.punctuation
    # Generate a random token
    token = "".join(choice(characters) for _ in range(length))
    return token
