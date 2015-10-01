from tokenizer import Tokenizer, Token, InvalidTokenException
import unittest

class TokenizerTestSuite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self, SingleTokenTests, MultiTokenTests)

class SingleTokenTests(unittest.TestCase):
    def setUp(self):
        self.tokenizer = Tokenizer()

    def test_empty_string(self):
        self.tokenizer.set_function_string("")
        tokens = self.tokenizer.get_tokens()
        assert len(tokens) == 0

    def test_comma(self):
        self.tokenizer.set_function_string(",")
        tokens = self.tokenizer.get_tokens()
        assert len(tokens) == 1
        token = tokens[0]
        assert token.type == "comma"
        assert token.position == 0

    def test_open_paren(self):
        self.tokenizer.set_function_string("(")
        tokens = self.tokenizer.get_tokens()
        assert len(tokens) == 1
        assert tokens[0].match("open_paren", None, None, 0, 1)

    def test_close_paren(self):
        self.tokenizer.set_function_string(")")
        tokens = self.tokenizer.get_tokens()
        assert len(tokens) == 1
        assert tokens[0].match("close_paren", None, None, 0, 1)

    def test_add_op(self):
        self.tokenizer.set_function_string("+")
        tokens = self.tokenizer.get_tokens()
        assert len(tokens) == 1
        assert tokens[0].match("arith_op", "+", None, 0, 1)

    def test_sub_op(self):
        self.tokenizer.set_function_string("-")
        tokens = self.tokenizer.get_tokens()
        assert len(tokens) == 1
        assert tokens[0].match("arith_op", "-", None, 0, 1)

    def test_mult_op(self):
        self.tokenizer.set_function_string("*")
        tokens = self.tokenizer.get_tokens()
        assert len(tokens) == 1
        assert tokens[0].match("factor_op", "*", None, 0, 1)

    def test_div_op(self):
        self.tokenizer.set_function_string("/")
        tokens = self.tokenizer.get_tokens()
        assert len(tokens) == 1
        assert tokens[0].match("factor_op", "/", None, 0, 1)

    def test_exp_op(self):
        self.tokenizer.set_function_string("^")
        tokens = self.tokenizer.get_tokens()
        assert len(tokens) == 1
        assert tokens[0].match("exp_op", "^", None, 0, 1)

    def test_eq_op(self):
        self.tokenizer.set_function_string("=")
        tokens = self.tokenizer.get_tokens()
        assert len(tokens) == 1
        assert tokens[0].match("rel_op", "eq", None, 0, 1)

    def test_neq_op(self):
        self.tokenizer.set_function_string("!=")
        tokens = self.tokenizer.get_tokens()
        assert len(tokens) == 1
        assert tokens[0].match("rel_op", "neq", None, 0, 2)

    def test_lt_op(self):
        self.tokenizer.set_function_string("<")
        tokens = self.tokenizer.get_tokens()
        assert len(tokens) == 1
        assert tokens[0].match("rel_op", "lt", None, 0, 1)

    def test_lte_op(self):
        self.tokenizer.set_function_string("<=")
        tokens = self.tokenizer.get_tokens()
        assert len(tokens) == 1
        assert tokens[0].match("rel_op", "lte", None, 0, 2)

    def test_gt_op(self):
        self.tokenizer.set_function_string(">")
        tokens = self.tokenizer.get_tokens()
        assert len(tokens) == 1
        assert tokens[0].match("rel_op", "gt", None, 0, 1)

    def test_gte_op(self):
        self.tokenizer.set_function_string(">=")
        tokens = self.tokenizer.get_tokens()
        assert len(tokens) == 1
        assert tokens[0].match("rel_op", "gte", None, 0, 2)

    def test_int_num(self):
        self.tokenizer.set_function_string("123")
        tokens = self.tokenizer.get_tokens()
        assert len(tokens) == 1
        assert tokens[0].match("number", None, "123", 0, 3)

    def test_decimal_num(self):
        self.tokenizer.set_function_string("123.456")
        tokens = self.tokenizer.get_tokens()
        assert len(tokens) == 1
        assert tokens[0].match("number", None, "123.456", 0, 7)

    def test_invalid_num(self):
        self.tokenizer.set_function_string("123.")
        try:
            tokens = self.tokenizer.get_tokens()
        except InvalidTokenException as e:
            assert e.position == 3
            pass
        else:
            self.fail("expected an InvalidTokenException")

    def test_invalid_char(self):
        self.tokenizer.set_function_string("&")
        try:
            tokens = self.tokenizer.get_tokens()
        except InvalidTokenException as e:
            assert e.position == 0
            pass
        else:
            self.fail("expected an InvalidTokenException")

    def test_invalid_rel_char(self):
        self.tokenizer.set_function_string("1 & 2")
        try:
            tokens = self.tokenizer.get_tokens()
        except InvalidTokenException as e:
            assert e.position == 2
            pass
        else:
            self.fail("expected an InvalidTokenException")

    def test_invalid_rel_not_char(self):
        self.tokenizer.set_function_string("1 !^ 2")
        try:
            tokens = self.tokenizer.get_tokens()
        except InvalidTokenException as e:
            assert e.position == 2
            pass
        else:
            self.fail("expected an InvalidTokenException")

    def test_alpha_identifier(self):
        self.tokenizer.set_function_string("abc")
        tokens = self.tokenizer.get_tokens()
        assert len(tokens) == 1
        assert tokens[0].match("ident", "ABC", None, 0, 3)

    def test_alphanumeric_identifier(self):
        self.tokenizer.set_function_string("abc123")
        tokens = self.tokenizer.get_tokens()
        assert len(tokens) == 1
        assert tokens[0].match("ident", "ABC123", None, 0, 6)

    def test_invalid_identifier(self):
        self.tokenizer.set_function_string("123abc")
        tokens = self.tokenizer.get_tokens()
        assert len(tokens) == 2
        assert tokens[0].match("number", None, "123", 0, 3)
        assert tokens[1].match("ident", "ABC", None, 3, 3)

    def test_spaces_ignored(self):
        self.tokenizer.set_function_string(" abc ")
        tokens = self.tokenizer.get_tokens()
        assert len(tokens) == 1
        assert tokens[0].match("ident", "ABC", None, 1, 3)

class MultiTokenTests(unittest.TestCase):
    def setUp(self):
        self.tokenizer = Tokenizer()

    def test_numeric_arith_expression(self):
        self.tokenizer.set_function_string("123 + 456")
        tokens = self.tokenizer.get_tokens()
        assert len(tokens) == 3
        assert tokens[0].match("number", None, "123", 0, 3)
        assert tokens[1].match("arith_op", "+", None, 4, 1)
        assert tokens[2].match("number", None, "456", 6, 3)

    def test_complex_expression(self):
        self.tokenizer.set_function_string("if ( BP1 = 0 , ( ( VP1 + VP2 ) / ( VP1 * 2.0 ) + NP1 - NP2 ) , 0 )")
        tokens = self.tokenizer.get_tokens()
        assert len(tokens) == 26
        assert tokens[0].match("ident", "IF", None, 0, 2)
        assert tokens[1].match("open_paren", None, None, 3, 1)
        assert tokens[2].match("ident", "BP1", None, 5, 3)
        assert tokens[3].match("rel_op", "eq", None, 9, 1)
        assert tokens[4].match("number", None, "0", 11, 1)
        assert tokens[5].match("comma", None, None, 13, 1)
        assert tokens[6].match("open_paren", None, None, 15, 1)
        assert tokens[7].match("open_paren", None, None, 17, 1)
        assert tokens[8].match("ident", "VP1", None, 19, 3)
        assert tokens[9].match("arith_op", "+", None, 23, 1)
        assert tokens[10].match("ident", "VP2", None, 25, 3)
        assert tokens[11].match("close_paren", None, None, 29, 1)
        assert tokens[12].match("factor_op", "/", None, 31, 1)
        assert tokens[13].match("open_paren", None, None, 33, 1)
        assert tokens[14].match("ident", "VP1", None, 35, 3)
        assert tokens[15].match("factor_op", "*", None, 39, 1)
        assert tokens[16].match("number", None, "2.0", 41, 3)
        assert tokens[17].match("close_paren", None, None, 45, 1)
        assert tokens[18].match("arith_op", "+", None, 47, 1)
        assert tokens[19].match("ident", "NP1", None, 49, 3)
        assert tokens[20].match("arith_op", "-", None, 53, 1)
        assert tokens[21].match("ident", "NP2", None, 55, 3)
        assert tokens[22].match("close_paren", None, None, 59, 1)
        assert tokens[23].match("comma", None, None, 61, 1)
        assert tokens[24].match("number", None, "0", 63, 1)
        assert tokens[25].match("close_paren", None, None, 65, 1)


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(TokenizerTestSuite)