import re

# ======================= Regular expressions for validation
# a-z(lowercase) 0-9
re_username = re.compile(r'^[a-z0-9]{1,200}$')
# a-z(lowercase), A-Z(uppercase)
re_name = re.compile(r'^[a-zA-Z]{1,200}$')
# a-z(lowercase), A-Z(uppercase), 0-9, symbols: !@#$%^&*()_+=[]{}<>? , 4-200 characters
re_password = re.compile(r'^[a-zA-Z0-9!@#$%^&*()_+=[\]{}<>?]{4,200}$')


def validate_data(data: dict, data_class: type):
    fields = {name: type_ for name, type_ in data_class.__annotations__.items() if name != 'return'}
    errors = []

    for name, type_ in fields.items():
        if not hasattr(data, name):
            errors.append(f'Missing required field: {name}')
        elif not isinstance(getattr(data, name), type_):
            errors.append(f'Invalid type for: "{name}": expected "{type_.__name__}" but got "{type(getattr(data, name)).__name__}"')

    # if there are errors, we return a string with the errors
    if errors:
        error_msg = f'Validation failed: {0}'.format("\n".join(errors))
        return error_msg

    # if there are no errors, we return None
    return None


def validate_username(username: str):
    if not re_username.match(username):
        return False
    return True


def validate_name(name: str):
    if not re_name.match(name):
        return False
    return True


def validate_password(password: str):
    if not re_password.match(password):
        return False
    return True
