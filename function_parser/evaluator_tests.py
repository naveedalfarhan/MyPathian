import random
from evaluator import Evaluator
import unittest


class ParserTestSuite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self, ParserTests)

class ParserTests(unittest.TestCase):
    def setUp(self):
        self.evaluator = Evaluator()

    def test_single_number(self):
        expression_tree = {
            "node_type": "number",
            "value": 123.456
        }

        result = self.evaluator.evaluate(expression_tree, {})

        assert result == 123.456

    def test_single_identifier(self):
        expression_tree = {
            "node_type": "ident",
            "name": "VP1"
        }

        parameters = {
            "VP1": 123.456
        }

        result = self.evaluator.evaluate(expression_tree, parameters)

        assert result == 123.456

    def test_simple_arithmetic_expression(self):
        expression_tree = {
            "node_type": "arith_op",
            "name": "+",
            "left": {
                "node_type": "number",
                "value": 1
            },
            "right": {
                "node_type": "number",
                "value": 2
            }
        }

        result = self.evaluator.evaluate(expression_tree, {})

        assert result == 3

    def test_exponentiation_expression(self):
        expression_tree = {
            "node_type": "exp_op",
            "name": "^",
            "left": {
                "node_type": "number",
                "value": 3
            },
            "right": {
                "node_type": "number",
                "value": 2
            }
        }

        result = self.evaluator.evaluate(expression_tree, {})

        assert result == 9

    def test_order_of_operations(self):
        expression_tree = {
            "node_type": "arith_op",
            "name": "-",
            "left": {
                "node_type": "arith_op",
                "name": "-",
                "left": {
                    "node_type": "number",
                    "value": 3
                },
                "right": {
                    "node_type": "number",
                    "value": 2
                }
            },
            "right": {
                "node_type": "number",
                "value": 1
            }
        }

        result = self.evaluator.evaluate(expression_tree, {})

        assert result == 0

    def test_complex_operation(self):
        expression_tree = {
            "node_type": "arith_op",
            "name": "-",
            "left": {
                "node_type": "arith_op",
                "name": "-",
                "left": {
                    "node_type": "arith_op",
                    "name": "+",
                    "left": {
                        "node_type": "factor_op",
                        "name": "/",
                        "left": {
                            "node_type": "arith_op",
                            "name": "+",
                            "left": {
                                "node_type": "ident",
                                "name": "VP1"
                            },
                            "right": {
                                "node_type": "ident",
                                "name": "VP2"
                            }
                        },
                        "right": {
                            "node_type": "factor_op",
                            "name": "*",
                            "left": {
                                "node_type": "ident",
                                "name": "VP1"
                            },
                            "right": {
                                "node_type": "number",
                                "value": 2
                            }
                        }
                    },
                    "right": {
                        "node_type": "ident",
                        "name": "NP1"
                    }
                },
                "right": {
                    "node_type": "ident",
                    "name": "NP2"
                }
            },
            "right": {
                "node_type": "exp_op",
                "name": "^",
                "left": {
                    "node_type": "ident",
                    "name": "NP3"
                },
                "right": {
                    "node_type": "number",
                    "value": 2
                }
            }
        }

        parameters = {
            "VP1": 1.0,
            "VP2": 2.0,
            "NP1": 3.0,
            "NP2": 4.0,
            "NP3": 5.0
        }

        result = self.evaluator.evaluate(expression_tree, parameters)

        assert result == -24.5

    def test_rel_eq_operations(self):
        expression_tree = {
            "node_type": "rel_op",
            "name": "=",
            "left": {
                "node_type": "number",
                "value": 0.0
            },
            "right": {
                "node_type": "number",
                "value": 1.0
            }
        }

        assert self.evaluator.evaluate(expression_tree, {}) == 0

        expression_tree["left"]["value"] = 1.0

        assert self.evaluator.evaluate(expression_tree, {}) == 1

        expression_tree["left"]["value"] = 2.0

        assert self.evaluator.evaluate(expression_tree, {}) == 0

    def test_rel_neq_operations(self):
        expression_tree = {
            "node_type": "rel_op",
            "name": "!=",
            "left": {
                "node_type": "number",
                "value": 0.0
            },
            "right": {
                "node_type": "number",
                "value": 1.0
            }
        }

        assert self.evaluator.evaluate(expression_tree, {}) == 1

        expression_tree["left"]["value"] = 1.0

        assert self.evaluator.evaluate(expression_tree, {}) == 0

        expression_tree["left"]["value"] = 2.0

        assert self.evaluator.evaluate(expression_tree, {}) == 1

    def test_rel_gt_operations(self):
        expression_tree = {
            "node_type": "rel_op",
            "name": ">",
            "left": {
                "node_type": "number",
                "value": 0.0
            },
            "right": {
                "node_type": "number",
                "value": 1.0
            }
        }

        assert self.evaluator.evaluate(expression_tree, {}) == 0

        expression_tree["left"]["value"] = 1.0

        assert self.evaluator.evaluate(expression_tree, {}) == 0

        expression_tree["left"]["value"] = 2.0

        assert self.evaluator.evaluate(expression_tree, {}) == 1

    def test_rel_gte_operations(self):
        expression_tree = {
            "node_type": "rel_op",
            "name": ">=",
            "left": {
                "node_type": "number",
                "value": 0.0
            },
            "right": {
                "node_type": "number",
                "value": 1.0
            }
        }

        assert self.evaluator.evaluate(expression_tree, {}) == 0

        expression_tree["left"]["value"] = 1.0

        assert self.evaluator.evaluate(expression_tree, {}) == 1

        expression_tree["left"]["value"] = 2.0

        assert self.evaluator.evaluate(expression_tree, {}) == 1

    def test_rel_lt_operations(self):
        expression_tree = {
            "node_type": "rel_op",
            "name": "<",
            "left": {
                "node_type": "number",
                "value": 0.0
            },
            "right": {
                "node_type": "number",
                "value": 1.0
            }
        }

        assert self.evaluator.evaluate(expression_tree, {}) == 1

        expression_tree["left"]["value"] = 1.0

        assert self.evaluator.evaluate(expression_tree, {}) == 0

        expression_tree["left"]["value"] = 2.0

        assert self.evaluator.evaluate(expression_tree, {}) == 0

    def test_rel_lte_operations(self):
        expression_tree = {
            "node_type": "rel_op",
            "name": "<=",
            "left": {
                "node_type": "number",
                "value": 0.0
            },
            "right": {
                "node_type": "number",
                "value": 1.0
            }
        }

        assert self.evaluator.evaluate(expression_tree, {}) == 1

        expression_tree["left"]["value"] = 1.0

        assert self.evaluator.evaluate(expression_tree, {}) == 1

        expression_tree["left"]["value"] = 2.0

        assert self.evaluator.evaluate(expression_tree, {}) == 0

    def test_if_func(self):
        expression_tree = {
            "node_type": "func",
            "name": "IF",
            "parameters": [
                {
                    "node_type": "ident",
                    "name": "CONDITION"
                },
                {
                    "node_type": "ident",
                    "name": "IFTRUE"
                },
                {
                    "node_type": "ident",
                    "name": "IFFALSE"
                }
            ]
        }

        parameters = {
            "CONDITION": 1,
            "IFTRUE": 5000,
            "IFFALSE": 4000
        }

        result = self.evaluator.evaluate(expression_tree, parameters)
        assert result == 5000

        parameters["CONDITION"] = 0

        result = self.evaluator.evaluate(expression_tree, parameters)
        assert result == 4000

    def test_power_func(self):
        expression_tree = {
            "node_type": "func",
            "name": "POWER",
            "parameters": [{"node_type": "ident", "name": "BASE"}, {"node_type": "ident", "name": "EXP"}]
        }

        for i in range(0, 25):
            parameters = {"BASE": random.random(), "EXP": random.random()}
            assert self.evaluator.evaluate(expression_tree, parameters) == parameters["BASE"] ** parameters["EXP"]

    def test_abs_func(self):
        expression_tree = {
            "node_type": "func",
            "name": "ABS",
            "parameters": [{"node_type": "ident", "name": "ITEM"}]
        }

        for i in range(0, 25):
            parameters = {"ITEM": random.random()}
            assert self.evaluator.evaluate(expression_tree, parameters) == abs(parameters["ITEM"])

