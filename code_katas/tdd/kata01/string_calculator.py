import re

DEFAULT_DELIMITER = ','


class StringCalculator:

    def __init__(self, logger, webservice):
        self.logger = logger
        self.webservice = webservice

    def add(self, numbers):
        if numbers == '':
            return 0
        delimiters = [DEFAULT_DELIMITER, '\n']
        if numbers.startswith('//'):
            header, numbers = numbers.split('\n', maxsplit=1)
            # eg. [aa][b][*][%]
            custom_delimiters = re.findall(r'\[([^\s]+?)\]', header[2:])
            delimiters.extend(custom_delimiters)
            # eg. //;\n
            if not custom_delimiters:
                delimiters.append(header[2])

        for d in delimiters:
            if d != DEFAULT_DELIMITER:
                numbers = numbers.replace(d, DEFAULT_DELIMITER)

        numbers_int = [int(str_num) for str_num in numbers.split(DEFAULT_DELIMITER)]
        numbers_list = []
        for num in numbers_int:
            if num < 0:
                raise ValueError('negatives not allowed')
            if num > 1000:
                continue
            numbers_list.append(num)

        result = sum(numbers_list)
        try:
            self.logger.write(f'{result}\n')
        except RuntimeError as error:
            self.webservice.logging_failed(str(error))

        return result
