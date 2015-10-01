from expression_tree_builder import ExpressionTreeBuilder, InvalidExpressionException, EmptyExpressionException
from tokenizer import Token
import unittest


class ParserTestSuite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self, ParserTests)


class InvalidParserTests(unittest.TestCase):
    def setUp(self):
        self.parser = ExpressionTreeBuilder()

    def test_empty_expression(self):
        self.parser.set_tokens([])
        try:
            expression_tree = self.parser.get_expression_tree()
        except EmptyExpressionException:
            pass
        else:
            self.fail("expected an EmptyExpressionException")

    def test_repeated_factors(self):
        tokens = [
            Token(type="number", value="123", position=0, length=3),
            Token(type="ident", name="ABC", position=4, length=3)
        ]
        self.parser.set_tokens(tokens)
        try:
            expression_tree = self.parser.get_expression_tree()
        except InvalidExpressionException as e:
            assert e.expecting == "none"
            assert e.position == 4
        else:
            self.fail("expected an InvalidExpressionException")

    def test_incomplete_arithmetic_operation(self):
        tokens = [
            Token(type="number", value="123", position=0, length=3),
            Token(type="arith_op", name="+", position=4, length=1)
        ]
        self.parser.set_tokens(tokens)
        try:
            expression_tree = self.parser.get_expression_tree()
        except InvalidExpressionException as e:
            assert e.expecting == "relation"
            assert e.end
        else:
            self.fail("expected an InvalidExpressionException")

    def test_incomplete_relation_operation(self):
        tokens = [
            Token(type="number", value="123", position=0, length=3),
            Token(type="rel_op", name="gte", position=4, length=2)
        ]
        self.parser.set_tokens(tokens)
        try:
            expression_tree = self.parser.get_expression_tree()
        except InvalidExpressionException as e:
            assert e.expecting == "term"
            assert e.end
        else:
            self.fail("expected an InvalidExpressionException")

    def test_incomplete_term_operation(self):
        tokens = [
            Token(type="number", value="123", position=0, length=3),
            Token(type="factor_op", name="*", position=4, length=1)
        ]
        self.parser.set_tokens(tokens)
        try:
            expression_tree = self.parser.get_expression_tree()
        except InvalidExpressionException as e:
            assert e.expecting == "exponent_factor"
            assert e.end
        else:
            self.fail("expected an InvalidExpressionException")

    def test_incomplete_factor_1(self):
        tokens = [
            Token(type="open_paren", position=0, length=1),
            Token(type="number", value="123", position=1, length=3),
            Token(type="factor_op", name="*", position=4, length=1),
            Token(type="number", value="123", position=5, length=3)
        ]
        self.parser.set_tokens(tokens)
        try:
            expression_tree = self.parser.get_expression_tree()
        except InvalidExpressionException as e:
            assert e.expecting == "close_paren"
            assert e.end
        else:
            self.fail("expected an InvalidExpressionException")

    def test_incomplete_factor_2(self):
        tokens = [
            Token(type="open_paren", position=0, length=1),
            Token(type="number", value="123", position=1, length=3),
            Token(type="factor_op", name="*", position=4, length=1),
            Token(type="number", value="123", position=5, length=3),
            Token(type="open_paren", position=8, length=1)
        ]
        self.parser.set_tokens(tokens)
        try:
            expression_tree = self.parser.get_expression_tree()
        except InvalidExpressionException as e:
            assert e.expecting == "close_paren"
            assert e.position == 8
        else:
            self.fail("expected an InvalidExpressionException")

    def test_incomplete_factor_3(self):
        tokens = [
            Token(type="number", value="123", position=0, length=3),
            Token(type="factor_op", name="*", position=3, length=1),
            Token(type="factor_op", name="*", position=4, length=1),
            Token(type="number", value="123", position=5, length=3)
        ]
        self.parser.set_tokens(tokens)
        try:
            expression_tree = self.parser.get_expression_tree()
        except InvalidExpressionException as e:
            assert e.expecting == "factor"
            assert e.position == 4
        else:
            self.fail("expected an InvalidExpressionException")

    def test_incomplete_function_1(self):
        tokens = [
            Token(type="ident", name="ABC", position=0, length=3),
            Token(type="open_paren", position=3, length=1),
            Token(type="number", value="123", position=4, length=3)
        ]
        self.parser.set_tokens(tokens)
        try:
            expression_tree = self.parser.get_expression_tree()
        except InvalidExpressionException as e:
            assert e.expecting == "comma"
            assert e.end
        else:
            self.fail("expected an InvalidExpressionException")

    def test_incomplete_function_2(self):
        tokens = [
            Token(type="ident", name="ABC", position=0, length=3),
            Token(type="open_paren", position=3, length=1),
            Token(type="number", value="123", position=4, length=3),
            Token(type="number", value="123", position=7, length=3)
        ]
        self.parser.set_tokens(tokens)
        try:
            expression_tree = self.parser.get_expression_tree()
        except InvalidExpressionException as e:
            assert e.expecting == "comma"
            assert e.position == 7
        else:
            self.fail("expected an InvalidExpressionException")

    def test_incomplete_function_3(self):
        tokens = [
            Token(type="ident", name="ABC", position=0, length=3),
            Token(type="open_paren", position=3, length=1),
            Token(type="number", value="123", position=4, length=3),
            Token(type="comma", position=7, length=1)
        ]
        self.parser.set_tokens(tokens)
        try:
            expression_tree = self.parser.get_expression_tree()
        except InvalidExpressionException as e:
            assert e.expecting == "expression"
            assert e.end
        else:
            self.fail("expected an InvalidExpressionException")

    def test_incomplete_function_4(self):
        tokens = [
            Token(type="ident", name="ABC", position=0, length=3),
            Token(type="open_paren", position=3, length=1),
            Token(type="number", value="123", position=4, length=3),
            Token(type="comma", position=7, length=1),
            Token(type="close_paren", position=8, length=1)
        ]
        self.parser.set_tokens(tokens)
        try:
            expression_tree = self.parser.get_expression_tree()
        except InvalidExpressionException as e:
            assert e.expecting == "factor"
            assert e.position == 8
        else:
            self.fail("expected an InvalidExpressionException")


class ParserTests(unittest.TestCase):
    def setUp(self):
        self.parser = ExpressionTreeBuilder()

    def test_single_number(self):
        token = Token()
        token.type = "number"
        token.value = "123.456"
        tokens = [token]
        self.parser.set_tokens(tokens)
        expression_tree = self.parser.get_expression_tree()
        assert expression_tree is not None
        assert expression_tree["node_type"] == "number"
        assert expression_tree["value"] == 123.456

    def test_single_identifier(self):
        token = Token()
        token.type = "ident"
        token.name = "VP1"
        tokens = [token]
        self.parser.set_tokens(tokens)
        expression_tree = self.parser.get_expression_tree()
        assert expression_tree is not None
        assert expression_tree["node_type"] == "ident"
        assert expression_tree["name"] == "VP1"

    def test_simple_arithmetic_expression(self):
        t1 = Token("number", value="1")
        t2 = Token("arith_op", name="+")
        t3 = Token("number", value="2")
        tokens = [t1, t2, t3]
        self.parser.set_tokens(tokens)
        expression_tree = self.parser.get_expression_tree()
        assert expression_tree is not None
        assert expression_tree["node_type"] == "arith_op"
        assert expression_tree["name"] == "+"
        assert expression_tree["left"] is not None
        assert expression_tree["left"]["node_type"] == "number"
        assert expression_tree["left"]["value"] == 1
        assert expression_tree["right"]["node_type"] == "number"
        assert expression_tree["right"]["value"] == 2

    def test_simple_relational_expression(self):
        tokens = [
            Token("ident", name="VP1"),
            Token("rel_op", name="eq"),
            Token("ident", name="VP2")
        ]
        self.parser.set_tokens(tokens)
        expression_tree = self.parser.get_expression_tree()
        assert expression_tree is not None
        assert expression_tree["node_type"] == "rel_op"
        assert expression_tree["name"] == "eq"
        assert expression_tree["left"] is not None
        assert expression_tree["left"]["node_type"] == "ident"
        assert expression_tree["left"]["name"] == "VP1"
        assert expression_tree["right"] is not None
        assert expression_tree["right"]["node_type"] == "ident"
        assert expression_tree["right"]["name"] == "VP2"

    def test_simple_exponential_expression(self):
        t1 = Token("number", value="1")
        t2 = Token("exp_op", name="^")
        t3 = Token("number", value="2")
        tokens = [t1, t2, t3]
        self.parser.set_tokens(tokens)
        expression_tree = self.parser.get_expression_tree()
        assert expression_tree is not None
        assert expression_tree["node_type"] == "exp_op"
        assert expression_tree["name"] == "^"
        assert expression_tree["left"] is not None
        assert expression_tree["left"]["node_type"] == "number"
        assert expression_tree["left"]["value"] == 1
        assert expression_tree["right"]["node_type"] == "number"
        assert expression_tree["right"]["value"] == 2

    def test_identifier_arithmetic_expression(self):
        t1 = Token("ident", name="VP1")
        t2 = Token("arith_op", name="+")
        t3 = Token("number", value="2")
        tokens = [t1, t2, t3]
        self.parser.set_tokens(tokens)
        expression_tree = self.parser.get_expression_tree()
        assert expression_tree is not None
        assert expression_tree["node_type"] == "arith_op"
        assert expression_tree["name"] == "+"
        assert expression_tree["left"] is not None
        assert expression_tree["left"]["node_type"] == "ident"
        assert expression_tree["left"]["name"] == "VP1"
        assert expression_tree["right"] is not None
        assert expression_tree["right"]["node_type"] == "number"
        assert expression_tree["right"]["value"] == 2
        pass

    def test_non_associative_expression(self):
        tokens = [
            Token("number", value="3"),
            Token("arith_op", name="-"),
            Token("number", value="2"),
            Token("arith_op", name="-"),
            Token("number", value="1")
        ]
        self.parser.set_tokens(tokens)
        expression_tree = self.parser.get_expression_tree()

        assert expression_tree is not None
        assert expression_tree["node_type"] == "arith_op"
        assert expression_tree["name"] == "-"
        assert expression_tree["left"] is not None
        assert expression_tree["left"]["node_type"] == "arith_op"
        assert expression_tree["left"]["name"] == "-"
        assert expression_tree["left"]["left"] is not None
        assert expression_tree["left"]["left"]["node_type"] == "number"
        assert expression_tree["left"]["left"]["value"] == 3
        assert expression_tree["left"]["right"] is not None
        assert expression_tree["left"]["right"]["node_type"] == "number"
        assert expression_tree["left"]["right"]["value"] == 2
        assert expression_tree["right"] is not None
        assert expression_tree["right"]["node_type"] == "number"
        assert expression_tree["right"]["value"] == 1

    def test_complex_arithmetic_expression1(self):
        tokens = [
            Token("open_paren"),
            Token("ident", name="VP1"),
            Token("arith_op", name="+"),
            Token("ident", name="VP2"),
            Token("close_paren"),
            Token("factor_op", name="*"),
            Token("ident", name="VP3")
        ]
        self.parser.set_tokens(tokens)
        expression_tree = self.parser.get_expression_tree()
        assert expression_tree is not None
        assert expression_tree["node_type"] == "factor_op"
        assert expression_tree["name"] == "*"
        assert expression_tree["left"] is not None
        assert expression_tree["left"]["node_type"] == "arith_op"
        assert expression_tree["left"]["name"] == "+"
        assert expression_tree["left"]["left"] is not None
        assert expression_tree["left"]["left"]["node_type"] == "ident"
        assert expression_tree["left"]["left"]["name"] == "VP1"
        assert expression_tree["left"]["right"] is not None
        assert expression_tree["left"]["right"]["node_type"] == "ident"
        assert expression_tree["left"]["right"]["name"] == "VP2"
        assert expression_tree["right"]["node_type"] == "ident"
        assert expression_tree["right"]["name"] == "VP3"
        pass

    def test_complex_arithmetic_expression2(self):
        tokens = [
            Token("open_paren"),
            Token("open_paren"),
            Token("ident", name="VP1"),
            Token("arith_op", name="+"),
            Token("ident", name="VP2"),
            Token("close_paren"),
            Token("factor_op", name="/"),
            Token("open_paren"),
            Token("ident", name="VP1"),
            Token("factor_op", name="*"),
            Token("number", value="2"),
            Token("close_paren"),
            Token("arith_op", name="+"),
            Token("ident", name="NP1"),
            Token("arith_op", name="-"),
            Token("ident", name="NP2"),
            Token("arith_op", name="-"),
            Token("ident", name="NP3"),
            Token("close_paren")
        ]
        self.parser.set_tokens(tokens)
        expression_tree = self.parser.get_expression_tree()


        assert expression_tree is not None
        assert expression_tree["node_type"] == "arith_op"
        assert expression_tree["name"] == "-"
        assert expression_tree["left"] is not None
        assert expression_tree["left"]["node_type"] == "arith_op"
        assert expression_tree["left"]["name"] == "-"
        assert expression_tree["left"]["left"] is not None
        assert expression_tree["left"]["left"]["node_type"] == "arith_op"
        assert expression_tree["left"]["left"]["name"] == "+"
        assert expression_tree["left"]["left"]["left"] is not None
        assert expression_tree["left"]["left"]["left"]["node_type"] == "factor_op"
        assert expression_tree["left"]["left"]["left"]["name"] == "/"
        assert expression_tree["left"]["left"]["left"]["left"] is not None
        assert expression_tree["left"]["left"]["left"]["left"]["node_type"] == "arith_op"
        assert expression_tree["left"]["left"]["left"]["left"]["name"] == "+"
        assert expression_tree["left"]["left"]["left"]["left"]["left"] is not None
        assert expression_tree["left"]["left"]["left"]["left"]["left"]["node_type"] == "ident"
        assert expression_tree["left"]["left"]["left"]["left"]["left"]["name"] == "VP1"
        assert expression_tree["left"]["left"]["left"]["left"]["right"] is not None
        assert expression_tree["left"]["left"]["left"]["left"]["right"]["node_type"] == "ident"
        assert expression_tree["left"]["left"]["left"]["left"]["right"]["name"] == "VP2"
        assert expression_tree["left"]["left"]["left"]["right"] is not None
        assert expression_tree["left"]["left"]["left"]["right"]["node_type"] == "factor_op"
        assert expression_tree["left"]["left"]["left"]["right"]["name"] == "*"
        assert expression_tree["left"]["left"]["left"]["right"]["left"] is not None
        assert expression_tree["left"]["left"]["left"]["right"]["left"]["node_type"] == "ident"
        assert expression_tree["left"]["left"]["left"]["right"]["left"]["name"] == "VP1"
        assert expression_tree["left"]["left"]["left"]["right"]["right"] is not None
        assert expression_tree["left"]["left"]["left"]["right"]["right"]["node_type"] == "number"
        assert expression_tree["left"]["left"]["left"]["right"]["right"]["value"] == 2
        assert expression_tree["left"]["left"]["right"] is not None
        assert expression_tree["left"]["left"]["right"]["node_type"] == "ident"
        assert expression_tree["left"]["left"]["right"]["name"] == "NP1"
        assert expression_tree["left"]["right"] is not None
        assert expression_tree["left"]["right"]["node_type"] == "ident"
        assert expression_tree["left"]["right"]["name"] == "NP2"
        assert expression_tree["right"] is not None
        assert expression_tree["right"]["node_type"] == "ident"
        assert expression_tree["right"]["name"] == "NP3"

    def test_function_call_expression(self):
        tokens = [
            Token("ident", name="IF"),
            Token("open_paren"),
            Token("ident", name="VP1"),
            Token("rel_op", name="gt"),
            Token("number", value="0"),
            Token("comma"),
            Token("number", value="1"),
            Token("comma"),
            Token("number", value="0"),
            Token("close_paren")
        ]
        self.parser.set_tokens(tokens)
        expression_tree = self.parser.get_expression_tree()

        assert expression_tree is not None
        assert expression_tree["node_type"] == "func"
        assert expression_tree["name"] == "IF"
        assert expression_tree["parameters"] is not None
        assert expression_tree["parameters"][0] is not None
        assert expression_tree["parameters"][0]["node_type"] == "rel_op"
        assert expression_tree["parameters"][0]["name"] == "gt"
        assert expression_tree["parameters"][0]["left"] is not None
        assert expression_tree["parameters"][0]["left"]["node_type"] == "ident"
        assert expression_tree["parameters"][0]["left"]["name"] == "VP1"
        assert expression_tree["parameters"][0]["right"] is not None
        assert expression_tree["parameters"][0]["right"]["node_type"] == "number"
        assert expression_tree["parameters"][0]["right"]["value"] == 0
        assert expression_tree["parameters"][1] is not None
        assert expression_tree["parameters"][1]["node_type"] == "number"
        assert expression_tree["parameters"][1]["value"] == 1
        assert expression_tree["parameters"][2] is not None
        assert expression_tree["parameters"][2]["node_type"] == "number"
        assert expression_tree["parameters"][2]["value"] == 0

    def test_function_call_expression_2(self):
        tokens = [
            Token("ident", name="OP1"),
            Token("open_paren"),
            Token("ident", name="VP1"),
            Token("close_paren"),
            Token("arith_op", name="+"),
            Token("ident", name="OP2"),
            Token("open_paren"),
            Token("ident", name="VP1"),
            Token("close_paren")
        ]
        self.parser.set_tokens(tokens)
        expression_tree = self.parser.get_expression_tree()

        assert expression_tree is not None
        assert expression_tree["node_type"] == "arith_op"
        assert expression_tree["name"] == "+"
        assert expression_tree["left"] is not None
        assert expression_tree["left"]["node_type"] == "func"
        assert expression_tree["left"]["name"] == "OP1"
        assert expression_tree["left"]["parameters"] is not None
        assert len(expression_tree["left"]["parameters"]) == 1
        assert expression_tree["left"]["parameters"][0]["node_type"] == "ident"
        assert expression_tree["left"]["parameters"][0]["name"] == "VP1"
        assert expression_tree["right"] is not None
        assert expression_tree["right"]["node_type"] == "func"
        assert expression_tree["right"]["name"] == "OP2"
        assert expression_tree["right"]["parameters"] is not None
        assert len(expression_tree["right"]["parameters"]) == 1
        assert expression_tree["right"]["parameters"][0]["node_type"] == "ident"
        assert expression_tree["right"]["parameters"][0]["name"] == "VP1"




if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(ParserTestSuite)