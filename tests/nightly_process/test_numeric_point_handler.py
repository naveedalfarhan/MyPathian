import unittest
from mock import patch, Mock, call, MagicMock
from nightly_process.numeric_point_handler import NumericPointHandler


class TestNumericPointHandler(unittest.TestCase):

    @patch("nightly_process.numeric_point_handler.UoW")
    @patch("nightly_process.numeric_point_handler.NumericPointHandler._compile_equipment_point_records")
    @patch("nightly_process.numeric_point_handler.NumericPointHandler._get_numeric_points")
    @patch("nightly_process.numeric_point_handler.NumericPointHandler._evaluate_points")
    def test_run(self, compile_equipment_point_records_mock, evaluate_points_mock, get_numeric_points_mock, uow_mock):
        calculated_point_handler = NumericPointHandler()

        calculated_point_handler.run()

        get_numeric_points_mock.assert_called_with()
        evaluate_points_mock.assert_called_with()
        compile_equipment_point_records_mock.assert_called_with()


    @patch("nightly_process.numeric_point_handler.UoW")
    def test_finding_numeric_points(self, uow_mock):
        numeric_point_handler = NumericPointHandler()

        numeric_point_handler._get_numeric_points()

        uow_mock.return_value.component_points.get_points_by_type.assert_called_with("NP")
        assert numeric_point_handler.numeric_points == uow_mock.return_value.component_points.get_points_by_type.return_value

    @patch("nightly_process.numeric_point_handler.UoW")
    @patch("nightly_process.numeric_point_handler.NumericPointHandler._evaluate_point")
    def test_evaluate_points(self, evaluate_point_mock, uow_mock):
        numeric_point_handler = NumericPointHandler()
        numeric_point_handler.numeric_points = [Mock(), Mock(), Mock()]

        numeric_point_handler._evaluate_points()

        evaluate_point_mock.assert_has_calls([call(numeric_point_handler.numeric_points[0]),
                                              call(numeric_point_handler.numeric_points[1]),
                                              call(numeric_point_handler.numeric_points[2])])

    @patch("nightly_process.numeric_point_handler.UoW")
    @patch("nightly_process.numeric_point_handler.NumericPointHandler._evaluate_equipment_point")
    def test_evaluate_point(self, evaluate_equipment_point_mock, uow_mock):
        point_mock = MagicMock()
        equipment_points = [Mock(), Mock(), Mock()]
        uow_mock.return_value.equipment.get_equipment_points_by_component_point_id.return_value = equipment_points
        numeric_point_handler = NumericPointHandler()

        numeric_point_handler._evaluate_point(point_mock)

        uow_mock.return_value.equipment.get_equipment_points_by_component_point_id.assert_called_with(point_mock["id"])
        evaluate_equipment_point_mock.assert_has_calls([call(equipment_points[0], point_mock),
                                                        call(equipment_points[1], point_mock),
                                                        call(equipment_points[2], point_mock)])
