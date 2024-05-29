import unittest
from unittest.mock import patch, MagicMock
from auth import check_credentials, register_user
from database import get_db_connection, USER_TABLE

class TestAuth(unittest.TestCase):

    @patch('database.get_db_connection')
    def test_check_credentials(self, mock_get_db_connection):
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = True
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db_connection.return_value = mock_conn

        result = check_credentials('test_user', 'test_pass')
        self.assertTrue(result)
        mock_cursor.execute.assert_called_once_with(
            f"SELECT * FROM {USER_TABLE} WHERE login = ? AND password = ?", ('test_user', 'test_pass'))

    @patch('database.get_db_connection')
    def test_register_user(self, mock_get_db_connection):
        # Mock database connection for a new user
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db_connection.return_value = mock_conn

        result = register_user('new_user', 'new_pass')
        self.assertTrue(result)
        mock_cursor.execute.assert_called_with(
            f"INSERT INTO {USER_TABLE} (login, password) VALUES (?, ?)", ('new_user', 'new_pass'))

        # Mock database connection for an existing user
        mock_cursor.fetchone.return_value = True
        result = register_user('existing_user', 'existing_pass')
        self.assertFalse(result)
        mock_cursor.execute.assert_called_with(
            f"SELECT * FROM {USER_TABLE} WHERE login = ?", ('existing_user',))

if __name__ == '__main__':
    unittest.main()
