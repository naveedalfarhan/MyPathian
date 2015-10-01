from function_parser.expression_tree_builder import ExpressionTreeBuilder
from function_parser.tokenizer import Tokenizer


class FunctionParser:
    def __init__(self):
        pass

    @classmethod
    def parse(cls, function):
        tokenizer = Tokenizer(function)
        tokens = tokenizer.get_tokens()
        expression_tree_builder = ExpressionTreeBuilder(tokens)
        expression_tree = expression_tree_builder.get_expression_tree()
        identifier_names = list(expression_tree_builder.identifier_names)
        function_names = list(expression_tree_builder.function_names)
        variable_names = list(expression_tree_builder.variable_names)

        return {
            "expression_tree": expression_tree,
            "identifier_names": identifier_names,
            "function_names": function_names,
            "variable_names": variable_names
        }