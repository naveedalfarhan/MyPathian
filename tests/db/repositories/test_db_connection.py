import unittest
from db.uow import UoW
from mock import patch, Mock

__author__ = 'badams'


class TestDbConnection(unittest.TestCase):
    @patch("rethinkdb.connect")
    def test_connection_in_uow(self, rethinkdb_connect):
        uow = UoW(None)
        rethinkdb_connect.assert_called_with("104.236.87.217", 28015)