import unittest
from mock import patch, call, Mock, MagicMock
from nightly_process.calculated_point_handler import CalculatedPointHandler


class TestCalculatedPointHandler(unittest.TestCase):

    @patch("nightly_process.calculated_point_handler.UoW")
    @patch("nightly_process.calculated_point_handler.CalculatedPointHandler._get_calculated_points")
    @patch("nightly_process.calculated_point_handler.CalculatedPointHandler._build_dependencies_list")
    @patch("nightly_process.calculated_point_handler.CalculatedPointHandler._build_safe_points_list")
    @patch("nightly_process.calculated_point_handler.CalculatedPointHandler._compile_equipment_point_records")
    def test_run(self, compile_equipment_point_records_mock, build_safe_points_list_mock, build_dependencies_list_mock, get_calculated_points_mock, uow_mock):
        calculated_point_handler = CalculatedPointHandler()

        calculated_point_handler.run()

        get_calculated_points_mock.assert_called_with()
        build_dependencies_list_mock.assert_called_with()
        build_safe_points_list_mock.assert_called_with()
        compile_equipment_point_records_mock.assert_called_with()


    @patch("nightly_process.calculated_point_handler.UoW")
    def test_finding_calculated_points(self, uow_mock):
        calculated_point_handler = CalculatedPointHandler()

        calculated_point_handler._get_calculated_points()

        uow_mock.return_value.component_points.get_points_by_type.assert_called_with("CP")
        assert calculated_point_handler.calculated_points == uow_mock.return_value.component_points.get_points_by_type.return_value

    @patch("nightly_process.calculated_point_handler.UoW")
    @patch("nightly_process.calculated_point_handler.CalculatedPointHandler._get_points_for_component_id")
    def test_build_dependencies_list(self, get_points_for_component_id_mock, uow_mock):
        calculated_point_handler = CalculatedPointHandler()
        calculated_point_handler.calculated_points = [
            {"code": "cp1", "formula": "ep1 * ep2", "component_id": "test"},
            {"code": "cp2", "formula": "cp1 * 2", "component_id": "test"},
            {"code": "cp3", "formula": "cp1 + cp2 * ep2", "component_id": "test"}
        ]
        test_component_points = [
            {"code": "ep1", "id": "_ep1", "point_type": "EP"},
            {"code": "ep2", "id": "_ep2", "point_type": "EP"},
            {"code": "cp1", "id": "_cp1", "point_type": "CP"},
            {"code": "cp2", "id": "_cp2", "point_type": "CP"},
            {"code": "cp3", "id": "_cp3", "point_type": "CP"}
        ]
        get_points_for_component_id_mock.return_value = test_component_points

        calculated_point_handler._build_dependencies_list()

        self.assertItemsEqual(calculated_point_handler.calculated_points[0]["parameters"],
                              [{"point_id": "_ep1", "name": "EP1"},
                               {"point_id": "_ep2", "name": "EP2"}])
        self.assertItemsEqual(calculated_point_handler.calculated_points[0]["dependencies"],
                              [])
        self.assertItemsEqual(calculated_point_handler.calculated_points[1]["parameters"],
                              [{"point_id": "_cp1", "name": "CP1"}])
        self.assertItemsEqual(calculated_point_handler.calculated_points[1]["dependencies"],
                              ["CP1"])
        self.assertItemsEqual(calculated_point_handler.calculated_points[2]["parameters"],
                              [{"point_id": "_cp1", "name": "CP1"},
                               {"point_id": "_cp2", "name": "CP2"},
                               {"point_id": "_ep2", "name": "EP2"}])
        self.assertItemsEqual(calculated_point_handler.calculated_points[2]["dependencies"],
                              ["CP1", "CP2"])

    @patch("nightly_process.calculated_point_handler.UoW")
    def test_is_point_safe_with_no_dependencies(self, uow_mock):
        calculated_point_handler = CalculatedPointHandler()
        calculated_point_handler.calculated_points_by_code = {
            "CP1": {"code": "CP1", "component_id": "test", "dependencies": []}
        }

        is_point_safe = calculated_point_handler._is_point_safe("CP1")

        assert is_point_safe

    @patch("nightly_process.calculated_point_handler.UoW")
    def test_is_point_safe_with_no_circular_dependencies(self, uow_mock):
        calculated_point_handler = CalculatedPointHandler()
        calculated_point_handler.calculated_points_by_code = {
            "CP1": {"code": "CP1", "component_id": "test", "dependencies": ["CP2", "CP3"]},
            "CP2": {"code": "CP2", "component_id": "test", "dependencies": ["CP4", "CP5"]},
            "CP3": {"code": "CP3", "component_id": "test", "dependencies": ["CP6", "CP7"]},
            "CP4": {"code": "CP4", "component_id": "test", "dependencies": ["CP6", "CP7"]},
            "CP5": {"code": "CP5", "component_id": "test", "dependencies": ["CP6", "CP7"]},
            "CP6": {"code": "CP6", "component_id": "test", "dependencies": []},
            "CP7": {"code": "CP7", "component_id": "test", "dependencies": []}
        }

        is_point_safe = calculated_point_handler._is_point_safe("CP1")

        assert is_point_safe

    @patch("nightly_process.calculated_point_handler.UoW")
    def test_is_point_safe_with_self_referential_circular_dependency(self, uow_mock):
        calculated_point_handler = CalculatedPointHandler()
        calculated_point_handler.calculated_points_by_code = {
            "CP1": {"code": "CP1", "component_id": "test", "dependencies": []},
            "CP2": {"code": "CP2", "component_id": "test", "dependencies": ["CP2"]}
        }

        is_point_safe = calculated_point_handler._is_point_safe("CP2")

        assert not is_point_safe

    @patch("nightly_process.calculated_point_handler.UoW")
    def test_is_point_safe_with_circular_dependency(self, uow_mock):
        calculated_point_handler = CalculatedPointHandler()
        calculated_point_handler.calculated_points_by_code = {
            "CP1": {"code": "CP1", "component_id": "test", "dependencies": ["CP2"]},
            "CP2": {"code": "CP2", "component_id": "test", "dependencies": ["CP1"]}
        }

        is_point_safe = calculated_point_handler._is_point_safe("CP1")

        assert not is_point_safe

    @patch("nightly_process.calculated_point_handler.UoW")
    @patch("nightly_process.calculated_point_handler.CalculatedPointHandler._evaluate_point")
    def test_evaluate_points(self, evaluate_point_mock, uow_mock):
        """
        This method needs to assert that calculated points with dependencies aren't evaluated
        until all of their dependencies have been evaluated. This means a post-order tree traversal
        must be performed. The test points have been set up in such a way so that their dependency tree
        looks like the following:

        CP1  CP2  CP3  CP4  CP5         CP6          CP7       CP8    CP9  CP10  CP11  CP12
             / \            /         /     \        / \       / \
          CP3  CP4       CP2      CP7        CP8   CP9  CP10 CP11 CP12
                         / \      / \        / \
                      CP3  CP4 CP9  CP10 CP11  CP12

        A post-order traversal will hit nodes in the following order:

        CP1, CP3, CP4, CP2, CP3, CP4, CP3, CP4, CP2, CP5, CP9, CP10, CP7, CP11, CP12, CP8, CP6, CP9, CP10, CP7
        CP11, CP12, CP8, CP9, CP10, CP11, CP12

        Nodes don't need to be hit multiple times, so duplicates can be eliminated, leaving:

        CP1, CP3, CP4, CP2, CP5, CP9, CP10, CP7, CP11, CP12, CP8, CP6

        This is the call order that is tested for, and guarantees that all of a point's dependencies will have
        been evaluated before it is.
        """
        calculated_point_handler = CalculatedPointHandler()
        safe_points = [
            {"code": "CP1", "component_id": "test", "dependencies": []},
            {"code": "CP2", "component_id": "test", "dependencies": ["CP3", "CP4"]},
            {"code": "CP3", "component_id": "test", "dependencies": []},
            {"code": "CP4", "component_id": "test", "dependencies": []},
            {"code": "CP5", "component_id": "test", "dependencies": ["CP2"]},
            {"code": "CP6", "component_id": "test", "dependencies": ["CP7", "CP8"]},
            {"code": "CP7", "component_id": "test", "dependencies": ["CP9", "CP10"]},
            {"code": "CP8", "component_id": "test", "dependencies": ["CP11", "CP12"]},
            {"code": "CP9", "component_id": "test", "dependencies": []},
            {"code": "CP10", "component_id": "test", "dependencies": []},
            {"code": "CP11", "component_id": "test", "dependencies": []},
            {"code": "CP12", "component_id": "test", "dependencies": []}
        ]
        safe_points_by_code = dict((point["code"], point) for point in safe_points)

        calculated_point_handler.safe_points = safe_points
        calculated_point_handler.calculated_points = safe_points
        calculated_point_handler.calculated_points_by_code = safe_points_by_code

        calculated_point_handler._evaluate_points()

        evaluate_point_mock.assert_has_calls([call(safe_points_by_code["CP1"]),
                                              call(safe_points_by_code["CP3"]),
                                              call(safe_points_by_code["CP4"]),
                                              call(safe_points_by_code["CP2"]),
                                              call(safe_points_by_code["CP5"]),
                                              call(safe_points_by_code["CP9"]),
                                              call(safe_points_by_code["CP10"]),
                                              call(safe_points_by_code["CP7"]),
                                              call(safe_points_by_code["CP11"]),
                                              call(safe_points_by_code["CP12"]),
                                              call(safe_points_by_code["CP8"]),
                                              call(safe_points_by_code["CP6"])])

    @patch("nightly_process.calculated_point_handler.UoW")
    @patch("nightly_process.calculated_point_handler.CalculatedPointHandler._evaluate_equipment_point")
    def test_evaluate_point(self, evaluate_equipment_point_mock, uow_mock):
        point_mock = MagicMock()
        equipment_points = [Mock(), Mock(), Mock()]
        uow_mock.return_value.equipment.get_equipment_points_by_component_point_id.return_value = equipment_points
        calculated_point_handler = CalculatedPointHandler()

        calculated_point_handler._evaluate_point(point_mock)

        # uow_mock.return_value.equipment.get_equipment_points_by_component_point_id.assert_called_with(point_mock["id"])
        # evaluate_equipment_point_mock.assert_has_calls([call(equipment_points[0], point_mock),
        #                                                 call(equipment_points[1], point_mock),
        #                                                 call(equipment_points[2], point_mock)])


    @patch("nightly_process.calculated_point_handler.UoW")
    @patch("nightly_process.calculated_point_handler.EnergyRecordCompiler")
    def test_compile(self, energy_record_compiler_mock, uow_mock):
        point_ranges = [{"syrx_num": "syrx_num1", "start_date": "start_date1", "end_date": "end_date1"},
                        {"syrx_num": "syrx_num2", "start_date": "start_date2", "end_date": "end_date2"}]
        calculated_point_handler = CalculatedPointHandler()
        calculated_point_handler.point_ranges = point_ranges

        calculated_point_handler._compile_equipment_point_records()

        delete_method = uow_mock.return_value.compiled_energy_records.delete_compiled_equipment_point_records
        delete_method.assert_has_calls([call(point_ranges[0]["syrx_num"], point_ranges[0]["start_date"],
                                                      point_ranges[0]["end_date"]),
                                                 call(point_ranges[1]["syrx_num"], point_ranges[1]["start_date"],
                                                      point_ranges[1]["end_date"])])

        compile_method = energy_record_compiler_mock.return_value.compile_component_point_records_by_year_span
        compile_method.assert_has_calls([call(point_ranges[0]["syrx_num"], point_ranges[0]["start_date"],
                                              point_ranges[0]["end_date"]),
                                         call(point_ranges[1]["syrx_num"], point_ranges[1]["start_date"],
                                              point_ranges[1]["end_date"])])