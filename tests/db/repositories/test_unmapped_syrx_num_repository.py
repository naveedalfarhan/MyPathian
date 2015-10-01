import unittest
from db.repositories.unmapped_syrx_num_repository import UnmappedSyrxNumRepository
from mock import Mock, MagicMock, patch

__author__ = 'badams'


class TestUnmappedSyrxNumRepository(unittest.TestCase):
    def setUp(self):
        self.uow = MagicMock()
        self.repo = UnmappedSyrxNumRepository(self.uow)

    def test_get_all(self):
        table_mock = self.uow.tables.unmapped_syrx_nums
        rv = self.repo.get_all()
        self.uow.run_list.assert_called_with(table_mock)
        self.assertEqual(self.uow.run_list.return_value, rv)

    def test_get_by_syrx_num(self):
        syrx_num = Mock()
        table_mock = self.uow.tables.unmapped_syrx_nums

        rv = self.repo.get_by_syrx_num(syrx_num)

        table_mock.get_all.assert_called_with(syrx_num, index='syrx_num')
        return_value = table_mock.get_all.return_value

        self.uow.run_list.assert_called_with(return_value)
        self.assertEqual(self.uow.run_list.return_value, rv)

    @patch("db.repositories.unmapped_syrx_num_repository.UnmappedSyrxNumRepository.get_by_syrx_num")
    def test_add_syrx_num(self, get_by_syrx_num):
        syrx_num = {'syrx_num': Mock()}
        table_mock = self.uow.tables.unmapped_syrx_nums
        get_by_syrx_num.return_value = []

        self.repo.add_syrx_num(syrx_num)

        get_by_syrx_num.assert_called_with(syrx_num['syrx_num'])

        # table.insert()
        table_mock.insert.assert_called_with(syrx_num)
        return_value = table_mock.insert.return_value

        self.uow.run.assert_called_with(return_value)

    def test_remove_syrx_num(self):
        syrx_num = Mock()
        table_mock = self.uow.tables.unmapped_syrx_nums

        self.repo.remove_syrx_num(syrx_num)

        # table.get_all()
        table_mock.get_all.assert_called_with(syrx_num, index="syrx_num")
        return_value = table_mock.get_all.return_value

        # table.get_all().delete()
        return_value.delete.assert_called_with()
        return_value = return_value.delete.return_value

        self.uow.run.assert_called_with(return_value)