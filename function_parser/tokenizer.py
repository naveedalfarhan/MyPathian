class InvalidTokenException(Exception):
    def __init__(self, position):
        self.exception_type = "InvalidTokenException"
        self.position = position
        Exception.__init__(self)


class Tokenizer:
    def __init__(self, function_string=None):
        self.function_string = ""
        self.function_string_length = 0
        self.c_pos = -1
        self.c = None
        self.tokens = []

        if function_string is not None:
            self.set_function_string(function_string)
        pass

    def set_function_string(self, function_string):
        self.function_string = function_string
        self.function_string_length = len(self.function_string)
        self.c_pos = -1
        self.c = None
        self.tokens = []

    @staticmethod
    def is_digit(d):
        return d in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

    @staticmethod
    def is_alpha(d):
        return d in ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j",
                     "k", "l", "m", "n", "o", "p", "q", "r", "s", "t",
                     "u", "v", "w", "x", "y", "z",
                     "A", "B", "C", "D", "E", "F", "G", "H", "I", "J",
                     "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T",
                     "U", "V", "W", "X", "Y", "Z"]

    def read(self):
        self.c_pos += 1
        self.c = self.function_string[self.c_pos]

    def peek(self):
        try:
            return self.function_string[self.c_pos + 1]
        except IndexError:
            return ""

    def get_tokens(self):
        function_string_length = len(self.function_string)

        while (self.c_pos + 1) < function_string_length:
            self.read()

            if self.c == ",":
                token = Token(position=self.c_pos, length=1)
                token.type = "comma"
                self.tokens.append(token)

            elif self.c == "(":
                token = Token(position=self.c_pos, length=1)
                token.type = "open_paren"
                self.tokens.append(token)

            elif self.c == ")":
                token = Token(position=self.c_pos, length=1)
                token.type = "close_paren"
                self.tokens.append(token)

            elif self.c == "+" or self.c == "-":
                token = Token(position=self.c_pos, length=1)
                token.type = "arith_op"
                token.name = self.c
                self.tokens.append(token)

            elif self.c == "*" or self.c == "/":
                token = Token(position=self.c_pos, length=1)
                token.type = "factor_op"
                token.name = self.c
                self.tokens.append(token)

            elif self.c == "^":
                token = Token(position=self.c_pos, length=1)
                token.type = "exp_op"
                token.name = self.c
                self.tokens.append(token)

            elif self.c == "=" or self.c == "<" or self.c == ">" or self.c == "!":
                self.get_relational_token()

            elif self.is_digit(self.c):
                self.get_number_token()

            elif self.is_alpha(self.c) or self.c == "_":
                self.get_identifier_token()

            elif self.c == " ":
                pass

            else:
                raise InvalidTokenException(self.c_pos)

        return self.tokens

    def get_relational_token(self):
        c2 = self.peek()
        if self.c == "=":
            token = Token(position=self.c_pos, length=1)
            token.type = "rel_op"
            token.name = "eq"
            self.tokens.append(token)

        elif self.c == "<":
            if c2 == "=":
                token = Token(position=self.c_pos, length=2)
                self.read()
                token.type = "rel_op"
                token.name = "lte"
                self.tokens.append(token)

            else:
                token = Token(position=self.c_pos, length=1)
                token.type = "rel_op"
                token.name = "lt"
                self.tokens.append(token)

        elif self.c == ">":
            if c2 == "=":
                token = Token(position=self.c_pos, length=2)
                self.read()
                token.type = "rel_op"
                token.name = "gte"
                self.tokens.append(token)

            else:
                token = Token(position=self.c_pos, length=1)
                token.type = "rel_op"
                token.name = "gt"
                self.tokens.append(token)

        elif self.c == "!":
            if c2 == "=":
                token = Token(position=self.c_pos, length=2)
                self.read()
                token.type = "rel_op"
                token.name = "neq"
                self.tokens.append(token)

            else:
                raise InvalidTokenException(self.c_pos)

        else:
            raise InvalidTokenException(self.c_pos)

    def get_number_token(self):
        token = Token(position=self.c_pos)
        token.type = "number"
        token.value = self.c

        encountered_decimal = False
        encountered_digit_after_decimal = False

        while True:
            c2 = self.peek()
            if self.is_digit(c2):
                token.value += c2
                self.read()
                if encountered_decimal and not encountered_digit_after_decimal:
                    encountered_digit_after_decimal = True
            elif c2 == "." and not encountered_decimal:
                token.value += "."
                encountered_decimal = True
                self.read()
            elif c2 == "." and encountered_decimal:
                # add 1 to c_pos because we are checking the value of a peaked char
                raise InvalidTokenException(self.c_pos + 1)
            else:
                break

        token.length = len(token.value)

        if encountered_decimal and not encountered_digit_after_decimal:
            raise InvalidTokenException(self.c_pos)
        self.tokens.append(token)

    def get_identifier_token(self):
        token = Token(position=self.c_pos)
        token.type = "ident"
        token.name = self.c

        while True:
            c2 = self.peek()
            if self.is_alpha(c2) or self.is_digit(c2) or c2 == "_":
                token.name += c2
                self.read()
            else:
                break

        token.name = token.name.upper()
        token.length = len(token.name)
        self.tokens.append(token)


class Token:
    def __init__(self, type=None, name=None, value=None, position=None, length=None):
        self.type = type
        self.name = name
        self.value = value
        self.position = position
        self.length = length

    def match(self, type, name, value, position, length):
        return self.type == type and self.name == name and self.value == value \
               and self.position == position and self.length == length