class InvalidIdentifierException(Exception):
    pass

class InvalidNodeException(Exception):
    pass

class Evaluator:
    def __init__(self):
        pass

    def evaluate(self, expression_tree, parameters):
        if expression_tree is None:
            return None

        elif expression_tree["node_type"] == "number":
            return expression_tree["value"]

        elif expression_tree["node_type"] == "ident":
            try:
                return parameters[expression_tree["name"]]
            except IndexError:
                raise InvalidIdentifierException

        elif expression_tree["node_type"] == "arith_op":
            return self.evaluate_arith_op(expression_tree, parameters)

        elif expression_tree["node_type"] == "rel_op":
            return self.evaluate_rel_op(expression_tree, parameters)

        elif expression_tree["node_type"] == "factor_op":
            return self.evaluate_factor_op(expression_tree, parameters)

        elif expression_tree["node_type"] == "exp_op":
            return self.evaluate_exp_op(expression_tree, parameters)

        elif expression_tree["node_type"] == "func":
            return self.evaluate_func(expression_tree, parameters)

        else:
            raise InvalidNodeException

    def evaluate_arith_op(self, expression_tree, parameters):
        left_result = self.evaluate(expression_tree["left"], parameters)
        right_result = self.evaluate(expression_tree["right"], parameters)
        if expression_tree["name"] == "-":
            return left_result - right_result
        else:
            return left_result + right_result

    def evaluate_rel_op(self, expression_tree, parameters):
        left_result = self.evaluate(expression_tree["left"], parameters)
        right_result = self.evaluate(expression_tree["right"], parameters)

        if expression_tree["name"] == "=":
            return 1 if left_result == right_result else 0
        elif expression_tree["name"] == "!=":
            return 1 if left_result != right_result else 0
        elif expression_tree["name"] == ">":
            return 1 if left_result > right_result else 0
        elif expression_tree["name"] == ">=":
            return 1 if left_result >= right_result else 0
        elif expression_tree["name"] == "<":
            return 1 if left_result < right_result else 0
        elif expression_tree["name"] == "<=":
            return 1 if left_result <= right_result else 0

    def evaluate_factor_op(self, expression_tree, parameters):
        left_result = self.evaluate(expression_tree["left"], parameters)
        right_result = self.evaluate(expression_tree["right"], parameters)
        if expression_tree["name"] == "/":
            return left_result / right_result
        else:
            return left_result * right_result

    def evaluate_exp_op(self, expression_tree, parameters):
        left_result = self.evaluate(expression_tree["left"], parameters)
        right_result = self.evaluate(expression_tree["right"], parameters)
        return left_result ** right_result

    def evaluate_func(self, expression_tree, parameters):
        if expression_tree["name"] == "IF":
            if not expression_tree["parameters"] or len(expression_tree["parameters"]) != 3:
                raise InvalidNodeException

            cond_eval = self.evaluate(expression_tree["parameters"][0], parameters)
            if cond_eval == 0:
                return self.evaluate(expression_tree["parameters"][2], parameters)
            else:
                return self.evaluate(expression_tree["parameters"][1], parameters)

        elif expression_tree["name"] == "POWER":
            if not expression_tree["parameters"] or len(expression_tree["parameters"]) != 2:
                raise InvalidNodeException

            base_expression = self.evaluate(expression_tree["parameters"][0], parameters)
            exp_expression = self.evaluate(expression_tree["parameters"][1], parameters)

            return base_expression ** exp_expression

        elif expression_tree["name"] == "ABS":
            if not expression_tree["parameters"] or len(expression_tree["parameters"]) != 1:
                raise InvalidNodeException

            value_expression = self.evaluate(expression_tree["parameters"][0], parameters)

            return abs(value_expression)
