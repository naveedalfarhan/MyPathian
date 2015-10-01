import unittest

from db.repositories.component_point_repository import ComponentPointRepository
from fix_cp_functions import CPFixer
from function_parser.tokenizer import InvalidTokenException
from mock import Mock, patch, call, MagicMock


__author__ = 'Brian'


class TestDecimalFix(unittest.TestCase):
    def setUp(self):
        self.uow = Mock()
        self.repo = ComponentPointRepository(self.uow)
        self.fixer = CPFixer(self.uow)

    def test_has_decimal_func(self):
        value = {
            'formula': '1+2+Test1+.15'
        }

        rv = self.repo.has_decimal_func(value)

        self.assertEqual(rv, True)

    @patch("db.repositories.component_point_repository.ComponentPointRepository.has_decimal_func")
    def test_get_all_cp_with_decimal(self, has_decimal_func):
        table_mock = self.uow.tables.component_points

        rv = self.repo.get_all_cp_with_decimal()

        # table.get_all()
        table_mock.get_all.assert_called_with('CP', index='point_type')
        return_value = table_mock.get_all.return_value

        # table.get_all().filter()
        return_value.filter.assert_called_with(has_decimal_func)
        return_value = return_value.filter.return_value

        self.uow.run_list.assert_called_with(return_value)
        return_value = self.uow.run_list.return_value

        self.assertEqual(rv, return_value)

    @patch("fix_cp_functions.CPFixer.handle_zeros_for_point")
    def test_fix_leading_zeros(self, handle_zeros_for_point):
        # set up
        get_all_rv = [{'formula': '1+2.0'},
                      {'formula': '.09'},
                      {'formula': '1+2+Test1+.100'},
                      {'formula': '0.0000001'},
                      {'formula': '100.012'}]
        self.fixer.uow.component_points.get_all_cp_with_decimal.return_value = get_all_rv

        # actual function call
        self.fixer.fix_leading_zeros()

        # assert the points were found
        self.fixer.uow.component_points.get_all_cp_with_decimal.assert_called_with()

        # assert the fixing function was called for each point in the return
        handle_zeros_for_point.assert_has_calls([call(get_all_rv[0]),
                                                 call(get_all_rv[1]),
                                                 call(get_all_rv[2]),
                                                 call(get_all_rv[3]),
                                                 call(get_all_rv[4])])

    @patch("function_parser.FunctionParser.parse")
    @patch("fix_cp_functions.CPFixer.fix_zeros_for_point")
    def test_handle_zeros_for_point_not_necessary(self, fix_zeros_for_point, parse):
        point = {'formula': '1+2.0'}
        parse.return_value = ''

        self.fixer.handle_zeros_for_point(point)

        parse.assert_called_with(point['formula'])

        # assert that the fix function was not called
        self.assertEqual(fix_zeros_for_point.call_count, 0)

    @patch("function_parser.FunctionParser.parse")
    @patch("fix_cp_functions.CPFixer.fix_zeros_for_point")
    def test_handle_zeros_for_point_necessary(self, fix_zeros_for_point, parse):
        point = {'formula': '1+2+Test1+.100'}
        parse.side_effect = InvalidTokenException(10)

        self.fixer.handle_zeros_for_point(point)
        parse.assert_called_with(point['formula'])

        # assert that the fix function is called
        fix_zeros_for_point.assert_called_with(point, 10)

    @patch("fix_cp_functions.ComponentPoint")
    def test_fix_zeros_for_point_no_recursion(self, ComponentPoint):
        point = {'formula': '1+2+Test1+.100'}

        fixed_point = {'formula': '1+2+Test1+0.100'}
        fixed_point_obj = ComponentPoint(fixed_point)
        ComponentPoint.return_value = fixed_point_obj

        self.fixer.fix_zeros_for_point(point, 10)
        self.fixer.uow.component_points.update.assert_called_with(fixed_point_obj)

    @patch("fix_cp_functions.ComponentPoint")
    def test_fix_zeros_for_point_leading_decimal_no_recursion(self, ComponentPoint):
        point = {'formula': '.100+1'}

        fixed_point = {'formula': '0.100+1'}
        fixed_point_obj = ComponentPoint(fixed_point)
        ComponentPoint.return_value = fixed_point_obj

        self.fixer.fix_zeros_for_point(point, 0)
        self.fixer.uow.component_points.update.assert_called_with(fixed_point_obj)

    @patch("fix_cp_functions.CPFixer.handle_parameters_for_point")
    def test_fix_parameters(self, handle_parameters_for_point):
        # set up
        get_all_rv = [{'formula': '1+2.0+Test',
                       'parameters': []},
                      {'formula': '0.09',
                       'parameters': []},
                      {'formula': '1+2+Test1+0.100',
                       'parameters': []},
                      {'formula': '0.0000001+1',
                       'parameters': []},
                      {'formula': '100.012+Test.2',
                       'parameters': []}]
        self.fixer.uow.component_points.get_points_by_type.return_value = get_all_rv

        # function call
        self.fixer.fix_parameters()

        # get all calculated points
        self.fixer.uow.component_points.get_points_by_type.assert_called_with("CP")

        # fix_parameters_for_point for each point in list
        handle_parameters_for_point.assert_has_calls([call(get_all_rv[0]),
                                                      call(get_all_rv[1]),
                                                      call(get_all_rv[2]),
                                                      call(get_all_rv[3]),
                                                      call(get_all_rv[4])])

    @patch("function_parser.FunctionParser.parse")
    @patch("fix_cp_functions.CPFixer.fix_parameters_for_point")
    def test_handle_parameters_for_point_not_necessary(self, fix_parameters_for_point, parse):
        point = {'formula': '1+2.0'}
        parse.return_value = {
            'identifier_names': []
        }

        self.fixer.handle_parameters_for_point(point)

        parse.assert_called_with(point['formula'])

        # assert that the fix function was not called
        self.assertEqual(fix_parameters_for_point.call_count, 0)

    @patch("function_parser.FunctionParser.parse")
    @patch("fix_cp_functions.CPFixer.fix_parameters_for_point")
    def test_handle_parameters_for_point_necessary(self, fix_parameters_for_point, parse):
        point = {'formula': '1+2+Test1+0.100'}
        expression_tree = {
            'identifier_names':['Test1']
        }
        parse.return_value = expression_tree

        self.fixer.handle_parameters_for_point(point)
        parse.assert_called_with(point['formula'])

        # assert that the fix function is called
        fix_parameters_for_point.assert_called_with(point, expression_tree['identifier_names'])

    @patch("function_parser.FunctionParser.parse")
    @patch("fix_cp_functions.CPFixer.fix_parameters_for_point")
    def test_handle_parameters_for_point_error(self, fix_parameters_for_point, parse):
        # set up
        point = {'formula': '1+2+Test1+.100',
                 'id': '1'}
        parse.side_effect = InvalidTokenException(10)

        self.fixer.handle_parameters_for_point(point)
        parse.assert_called_with(point['formula'])

        self.assertEqual(fix_parameters_for_point.call_count, 0)

    def test_check_if_parameters_are_valid_fail(self):
        point = {
            'formula': '1+2+Test1+0.100',
            'parameters': []
        }
        identifier_names = ['Test1']

        rv = self.fixer.check_if_parameters_are_valid(point['parameters'], identifier_names)

        self.assertFalse(rv)

    def test_check_if_parameters_are_valid_succeed(self):
        point = {
            'forumula': '1+2+Test1+0.100',
            'parameters': [{'name': 'TEST1', 'point_id':1}]
        }
        identifier_names = ['Test1']

        rv = self.fixer.check_if_parameters_are_valid(point['parameters'], identifier_names)

        self.assertTrue(rv)

    @patch("fix_cp_functions.CPFixer.check_if_parameters_are_valid")
    @patch("fix_cp_functions.CPFixer.match_parameter_names")
    def test_fix_parameters_for_point_valid(self, match_parameter_names, check_if_parameters_are_valid):
        point = MagicMock()
        identifier_names = []

        # set the return value
        check_if_parameters_are_valid.return_value = True

        # call the function
        self.fixer.fix_parameters_for_point(point, identifier_names)

        # assert that the matching function was not called
        self.assertEqual(match_parameter_names.call_count, 0)

    @patch("fix_cp_functions.CPFixer.check_if_parameters_are_valid")
    @patch("fix_cp_functions.CPFixer.match_parameter_names")
    def test_fix_parameters_for_point_invalid(self, match_parameter_names, check_if_parameters_are_valid):
        point = MagicMock()
        identifier_names = []

        # set the return value
        check_if_parameters_are_valid.return_value = False

        # call the function
        self.fixer.fix_parameters_for_point(point, identifier_names)

        # assert that the matching function was called
        match_parameter_names.assert_called_with(point, identifier_names)

    @patch("fix_cp_functions.ComponentPoint")
    def test_match_parameter_names_success(self, ComponentPoint):
        # set up
        point = {'component_id': '1',
                 'parameters': []}
        component_point_return = [{'code': 'Test1',
                                   'id': '1'},
                                  {'code': 'Test2',
                                   'id': '2'}]
        identifier_names = ['test1', 'TEST2']
        final_point = {'component_id': '1',
                       'parameters': [
                           {'name': 'TEST1',
                            'point_id': '1'},
                           {'name': 'TEST2',
                            'point_id': '2'}
                       ]}
        final_point_obj = ComponentPoint(final_point)
        ComponentPoint.return_value = final_point_obj
        self.fixer.uow.component_points.get_points_for_component_id.return_value = component_point_return

        # function call
        self.fixer.match_parameter_names(point, identifier_names)

        # assertions
        self.fixer.uow.component_points.get_points_for_component_id.assert_called_with(point['component_id'])
        self.fixer.uow.component_points.update.assert_called_with(final_point_obj)

    def test_match_parameter_names_fail_missing_point(self):
        # set up
        point = {'component_id': '1',
                 'id': '3'}
        component_point_return = [{'code': 'Test1',
                                   'id': '1'}]
        identifier_names = ['test1', 'TEST2']

        self.fixer.uow.component_points.get_points_for_component_id.return_value = component_point_return

        # function call
        self.fixer.match_parameter_names(point, identifier_names)

        # assertions
        self.fixer.uow.component_points.get_points_for_component_id.assert_called_with(point['component_id'])
        self.assertEqual(self.fixer.uow.component_points.update.call_count, 1)

    @patch("fix_cp_functions.CPFixer.fix_leading_zeros")
    @patch("fix_cp_functions.CPFixer.fix_parameters")
    def test_run(self, fix_parameters, fix_leading_zeros):
        self.fixer.run()
        fix_leading_zeros.assert_called_with()
        fix_parameters.assert_called_with()