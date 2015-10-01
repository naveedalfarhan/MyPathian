class InvalidExpressionException(Exception):
    def __init__(self, expecting=None, position=None, end=False):
        self.exception_type = "InvalidExpressionException"
        self.expecting = expecting
        self.position = position
        self.end = end
        Exception.__init__(self)


class EmptyExpressionException(Exception):
    pass


class ExpressionTreeBuilder:
    def __init__(self, tokens=None):
        self.t_pos = -1
        self.t = None
        self.tokens = []
        self.identifier_names = set()
        self.function_names = set()
        self.variable_names = set()
        if tokens is not None:
            self.set_tokens(tokens)

    def set_tokens(self, tokens):
        self.t_pos = -1
        self.t = None
        self.tokens = tokens

    def read(self):
        try:
            self.t_pos += 1
            self.t = self.tokens[self.t_pos]
        except IndexError:
            self.t = None
            self.t_pos = len(self.tokens)

    def peek(self):
        try:
            return self.tokens[self.t_pos + 1]
        except IndexError:
            return None

    def get_expression_tree(self):
        self.read()

        if self.t is None:
            raise EmptyExpressionException

        expression_node = self.handle_expression()
        if self.t is not None:
            raise InvalidExpressionException("none", position=self.t.position)
        return expression_node

    def handle_expression(self):
        expressions = []
        operations = []

        expressions.append(self.handle_relation())

        while self.t is not None and self.t.type == "arith_op":
            operation = self.handle_arith_op()
            operations.append(operation)
            if self.t is None:
                raise InvalidExpressionException("relation", end=True)
            expressions.append(self.handle_relation())

        expression_node = expressions[0]
        for i in range(len(expressions) - 1):
            if i == 0:
                operations[0]["left"] = expressions[0]
                operations[0]["right"] = expressions[1]
            else:
                operations[i]["left"] = operations[i - 1]
                operations[i]["right"] = expressions[i + 1]
            expression_node = operations[i]

        return expression_node


    def handle_relation(self):
        expressions = []
        operations = []

        expressions.append(self.handle_term())

        while self.t is not None and self.t.type == "rel_op":
            operation = self.handle_rel_op()
            operations.append(operation)
            if self.t is None:
                raise InvalidExpressionException("term", end=True)
            expressions.append(self.handle_term())

        expression_node = expressions[0]
        for i in range(len(expressions) - 1):
            if i == 0:
                operations[0]["left"] = expressions[0]
                operations[0]["right"] = expressions[1]
            else:
                operations[i]["left"] = operations[i - 1]
                operations[i]["right"] = expressions[i + 1]
            expression_node = operations[i]

        return expression_node

    def handle_term(self):
        expressions = []
        operations = []

        expressions.append(self.handle_exponent_factor())

        while self.t is not None and self.t.type == "factor_op":
            operation = self.handle_factor_op()
            operations.append(operation)
            if self.t is None:
                raise InvalidExpressionException("exponent_factor", end=True)
            expressions.append(self.handle_exponent_factor())

        expression_node = expressions[0]
        for i in range(len(expressions) - 1):
            if i == 0:
                operations[0]["left"] = expressions[0]
                operations[0]["right"] = expressions[1]
            else:
                operations[i]["left"] = operations[i - 1]
                operations[i]["right"] = expressions[i + 1]
            expression_node = operations[i]

        return expression_node

    def handle_exponent_factor(self):
        expressions = []
        operations = []

        expressions.append(self.handle_factor())

        while self.t is not None and self.t.type == "exp_op":
            operation = self.handle_exponent_factor_op()
            operations.append(operation)
            if self.t is None:
                raise InvalidExpressionException("factor", end=True)
            expressions.append(self.handle_factor())

        expression_node = expressions[0]
        for i in range(len(expressions) - 1):
            if i == 0:
                operations[0]["left"] = expressions[0]
                operations[0]["right"] = expressions[1]
            else:
                operations[i]["left"] = operations[i - 1]
                operations[i]["right"] = expressions[i + 1]
            expression_node = operations[i]

        return expression_node

    def handle_factor(self):
        t2 = self.peek()
        if self.t is None:
            raise InvalidExpressionException("factor", end=True)
        elif self.t.type == "open_paren":
            self.read()
            expression_node = self.handle_expression()
            if self.t is None:
                raise InvalidExpressionException("close_paren", end=True)
            elif self.t.type != "close_paren":
                raise InvalidExpressionException("close_paren", position=self.t.position)
            self.read()

        elif self.t.type == "number":
            expression_node = self.handle_number()
        elif self.t.type == "ident":
            if t2 is not None and t2.type == "open_paren":
                expression_node = self.handle_function_call()
            else:
                expression_node = self.handle_identifier(False)
        else:
            raise InvalidExpressionException("factor", position=self.t.position)

        return expression_node

    def handle_function_call(self):
        identifier = self.handle_identifier(True)
        parameters = []

        if self.t is None or self.t.type != "open_paren":
            raise InvalidExpressionException
        self.read()

        while self.t is None or self.t.type != "close_paren":
            if len(parameters) > 0:
                if self.t is None:
                    raise InvalidExpressionException("comma", end=True)
                elif self.t.type != "comma":
                    raise InvalidExpressionException("comma", position=self.t.position)
                else:
                    self.read()
            if self.t is None:
                raise InvalidExpressionException("expression", end=True)
            parameters.append(self.handle_expression())

        # only way above loop will break is if self.t is not null and self.t.type is close_paren
        self.read()

        function_call_node = {
            "node_type": "func",
            "name": identifier["name"],
            "parameters": parameters
        }

        return function_call_node

    def handle_number(self):
        if self.t is None or self.t.type != "number":
            raise InvalidExpressionException
        expression_node = {
            "node_type": "number",
            "value": float(self.t.value),
            "token": self.t
        }
        self.read()
        return expression_node

    def handle_identifier(self, is_func_call):
        if self.t is None or self.t.type != "ident":
            raise InvalidExpressionException
        expression_node = {
            "node_type": "ident",
            "name": self.t.name,
            "token": self.t
        }

        self.identifier_names.add(self.t.name)
        if is_func_call:
            self.function_names.add(self.t.name)
        else:
            self.variable_names.add(self.t.name)
        self.read()
        return expression_node

    def handle_arith_op(self):
        if self.t is None or self.t.type != "arith_op":
            raise InvalidExpressionException
        expression_node = {
            "node_type": "arith_op",
            "name": self.t.name,
            "token": self.t
        }
        self.read()
        return expression_node

    def handle_rel_op(self):
        if self.t is None or self.t.type != "rel_op":
            raise InvalidExpressionException
        expression_node = {
            "node_type": "rel_op",
            "name": self.t.name,
            "token": self.t
        }
        self.read()
        return expression_node

    def handle_factor_op(self):
        if self.t is None or self.t.type != "factor_op":
            raise InvalidExpressionException
        expression_node = {
            "node_type": "factor_op",
            "name": self.t.name,
            "token": self.t
        }
        self.read()
        return expression_node

    def handle_exponent_factor_op(self):
        if self.t is None or self.t.type != "exp_op":
            raise InvalidExpressionException
        expression_node = {
            "node_type": "exp_op",
            "name": self.t.name,
            "token": self.t
        }
        self.read()
        return expression_node