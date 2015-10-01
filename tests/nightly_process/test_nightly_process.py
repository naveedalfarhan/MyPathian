import unittest
from mock import Mock, patch, MagicMock
from nightly_process.main import NightlyProcess


class TestNightlyProcess(unittest.TestCase):
    @patch("nightly_process.main.NightlyProcess.get_logger")
    @patch("nightly_process.main.NightlyProcess.group_johnson_files")
    @patch("nightly_process.main.NightlyProcess.group_fieldserver_files")
    @patch("nightly_process.main.NightlyProcess.group_invensys_files")
    @patch("nightly_process.main.NightlyProcess.group_siemens_files")
    def test_group_vendor_data(self, group_siemens_files, group_invensys_files, group_fieldserver_files, group_johnson_files, get_logger):
        nightly_process_config = MagicMock()

        nightly_process = NightlyProcess(nightly_process_config)
        nightly_process.group_vendor_data()
        group_johnson_files.assert_called_with()
        group_fieldserver_files.assert_called_with()
        group_invensys_files.assert_called_with()
        group_siemens_files.assert_called_with()

    @patch("nightly_process.main.NightlyProcess.get_logger")
    @patch("nightly_process.main.NightlyProcess.process_johnson_files")
    @patch("nightly_process.main.NightlyProcess.process_fieldserver_files")
    @patch("nightly_process.main.NightlyProcess.process_syrx_files")
    @patch("nightly_process.main.NightlyProcess.process_invensys_files")
    @patch("nightly_process.main.NightlyProcess.process_siemens_files")
    def test_process_vendor_data(self, process_siemens_files, process_invensys_files, process_syrx_files,
                                 process_fieldserver_files, process_johnson_files, get_logger):
        nightly_process_config = MagicMock()

        nightly_process = NightlyProcess(nightly_process_config)
        nightly_process.process_vendor_data()

        process_johnson_files.assert_called_with()
        process_fieldserver_files.assert_called_with()
        process_syrx_files.assert_called_with()
        process_invensys_files.assert_called_with()
        process_siemens_files.assert_called_with()

    @patch("nightly_process.main.NightlyProcess.get_logger")
    @patch("nightly_process.main.NightlyProcess.handle_calculated_points")
    @patch("nightly_process.main.NightlyProcess.handle_numeric_points")
    def test_handle_component_data(self, handle_numeric_points, handle_calculated_points, get_logger):
        nightly_process_config = MagicMock()

        nightly_process = NightlyProcess(nightly_process_config)
        nightly_process.handle_component_data()

        handle_calculated_points.assert_called_with()
        handle_numeric_points.assert_called_with()

    @patch("nightly_process.main.NightlyProcess.get_logger")
    @patch("nightly_process.main.JohnsonFileHandler")
    def test_process_johnson_files(self, johnson_file_handler, get_logger):
        nightly_process_config = MagicMock()

        nightly_process = NightlyProcess(nightly_process_config)

        nightly_process.process_johnson_files()

        assert johnson_file_handler.return_value.johnson_grouped_folder == nightly_process_config.JOHNSON_GROUPED_FOLDER
        assert johnson_file_handler.return_value.syrx_upload_folder == nightly_process_config.SYRX_UPLOAD_FOLDER
        johnson_file_handler.return_value.run.assert_called_with()

    @patch("nightly_process.main.NightlyProcess.get_logger")
    @patch("nightly_process.main.FieldserverFileHandler")
    def test_process_fieldserver_files(self, fieldserver_file_handler, get_logger):
        nightly_process_config = MagicMock()

        nightly_process = NightlyProcess(nightly_process_config)

        nightly_process.process_fieldserver_files()

        assert fieldserver_file_handler.return_value.fieldserver_grouped_folder == nightly_process_config.FIELDSERVER_GROUPED_FOLDER
        assert fieldserver_file_handler.return_value.syrx_upload_folder == nightly_process_config.SYRX_UPLOAD_FOLDER
        fieldserver_file_handler.return_value.run.assert_called_with()

    @patch("nightly_process.main.NightlyProcess.get_logger")
    @patch("nightly_process.main.InvensysFileHandler")
    def test_process_invensys_files(self, invensys_file_handler, get_logger):
        nightly_process_config = MagicMock()

        nightly_process = NightlyProcess(nightly_process_config)

        nightly_process.process_invensys_files()

        assert invensys_file_handler.return_value.invensys_grouped_folder == nightly_process_config.INVENSYS_GROUPED_FOLDER
        assert invensys_file_handler.return_value.syrx_upload_folder == nightly_process_config.SYRX_UPLOAD_FOLDER
        invensys_file_handler.return_value.run.assert_called_with()

    @patch("nightly_process.main.NightlyProcess.get_logger")
    @patch("nightly_process.main.SiemensFileHandler")
    def test_process_siemens_files(self, siemens_file_handler, get_logger):
        nightly_process_config = MagicMock()

        nightly_process = NightlyProcess(nightly_process_config)

        nightly_process.process_siemens_files()

        assert siemens_file_handler.return_value.siemens_grouped_folder == nightly_process_config.SIEMENS_GROUPED_FOLDER
        assert siemens_file_handler.return_value.syrx_upload_folder == nightly_process_config.SYRX_UPLOAD_FOLDER
        siemens_file_handler.return_value.run.assert_called_with()

    @patch("nightly_process.main.NightlyProcess.get_logger")
    @patch("nightly_process.main.SyrxFileHandler")
    def test_process_syrx_files(self, syrx_file_handler, get_logger):
        nightly_process_config = MagicMock()

        nightly_process = NightlyProcess(nightly_process_config)

        nightly_process.process_syrx_files()

        assert syrx_file_handler.return_value.syrx_upload_folder == nightly_process_config.SYRX_UPLOAD_FOLDER
        syrx_file_handler.return_value.process_all_syrx_files.assert_called_with()

    @patch("nightly_process.main.NightlyProcess.get_logger")
    @patch("nightly_process.main.CalculatedPointHandler")
    def test_handle_calculated_points(self, calculated_point_handler, get_logger):
        nightly_process_config = MagicMock()

        nightly_process = NightlyProcess(nightly_process_config)

        nightly_process.handle_calculated_points()

        calculated_point_handler.return_value.run.assert_called_with()

    @patch("nightly_process.main.NightlyProcess.get_logger")
    @patch("nightly_process.main.NumericPointHandler")
    def test_handle_numeric_points(self, numeric_point_handler, get_logger):
        nightly_process_config = MagicMock()

        nightly_process = NightlyProcess(nightly_process_config)

        nightly_process.handle_numeric_points()

        numeric_point_handler.return_value.run.assert_called_with()

    @patch("nightly_process.main.NightlyProcess.get_logger")
    @patch("nightly_process.main.GlobalVendorPointHandler")
    def test_handle_global_vendor_point(self, global_vendor_point_handler, get_logger):
        nightly_process_config = MagicMock()
        nightly_process = NightlyProcess(nightly_process_config)

        nightly_process.handle_global_vendor_points()

        global_vendor_point_handler.return_value.process_all_global_vendor_points.assert_called_with()

    @patch("nightly_process.main.NightlyProcess.get_logger")
    @patch("nightly_process.main.NightlyProcess.handle_component_data")
    @patch("nightly_process.main.NightlyProcess.process_vendor_data")
    @patch("nightly_process.main.NightlyProcess.group_vendor_data")
    @patch("nightly_process.main.NightlyProcess.import_weather_data")
    @patch("nightly_process.main.NightlyProcess.handle_unmapped_syrx_nums")
    @patch("nightly_process.main.NightlyProcess.handle_global_vendor_points")
    def test_run(self, handle_global_vendor_points, handle_unmapped_syrx_nums, import_weather_data, group_vendor_data, process_vendor_data, handle_component_data, get_logger):
        nightly_process_config = MagicMock()

        nightly_process = NightlyProcess(nightly_process_config)
        nightly_process.run()

        handle_unmapped_syrx_nums.assert_called_with()
        import_weather_data.assert_called_with()
        group_vendor_data.assert_called_with()
        process_vendor_data.assert_called_with()
        handle_component_data.assert_called_with()
        handle_global_vendor_points.assert_called_with()
