import random
import string


def generate_random_string():
    characters = string.ascii_letters
    random_string = ''.join(random.choice(characters) for _ in range(10))
    return random_string
