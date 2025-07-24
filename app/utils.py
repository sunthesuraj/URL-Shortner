import random
import string
import validators

def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

def validate_url(url_string):
    result = validators.url(url_string)

    return bool(result)
