from invalid_user_input import InvalidUserInput

MIN_PASSWORD_LENGTH = 8


class PasswordVerifier:

    def verify(self, password):
        if password is None:
            raise ValueError('Password shall not be None')
        password_hints = []
        if len(password) < MIN_PASSWORD_LENGTH:
            password_hints.append(f'Longer than {MIN_PASSWORD_LENGTH} characters longs')
        if password.lower() == password:
            password_hints.append('Have at least one upper case letter')
        if password.upper() == password:
            raise InvalidUserInput('Password shall have at least one lower case letter')
        if ''.join(filter(lambda ch: ch < '0' or ch > '9', password)) == password:
            password_hints.append('Contain at least one number')
        if len(password_hints) > 1:
            raise InvalidUserInput('Invalid password, must meet all but one of the following conditions:\n{}'
                                   .format('\n'.join(password_hints)))
