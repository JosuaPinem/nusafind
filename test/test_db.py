import pytest
from unittest.mock import Mock, patch, MagicMock
import mysql.connector
import os
from db.connection import create_connection, create_local_connection


class TestCreateConnection:
    """Test cases untuk fungsi create_connection"""
    
    @patch('db.connection.os.getenv')
    @patch('db.connection.mysql.connector.connect')
    def test_create_connection_success(self, mock_connect, mock_getenv):
        """Test create_connection berhasil membuat koneksi"""
        # Setup environment variables
        env_vars = {
            'DB_HOST': 'localhost',
            'DB_USERNAME': 'testuser',
            'DB_PASSWORD': 'testpass',
            'DB_NAME': 'testdb'
        }
        mock_getenv.side_effect = lambda key: env_vars.get(key)
        
        # Setup mock connection
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        # Execute
        result = create_connection()
        
        # Assert
        assert result == mock_conn
        mock_connect.assert_called_once_with(
            host='localhost',
            user='testuser',
            password='testpass',
            database='testdb'
        )
        
        # Verify all environment variables were accessed
        expected_calls = ['DB_HOST', 'DB_USERNAME', 'DB_PASSWORD', 'DB_NAME']
        for env_var in expected_calls:
            mock_getenv.assert_any_call(env_var)
    
    @patch('db.connection.os.getenv')
    @patch('db.connection.mysql.connector.connect')
    @patch('builtins.print')
    def test_create_connection_mysql_error(self, mock_print, mock_connect, mock_getenv):
        """Test create_connection ketika terjadi MySQL error"""
        # Setup environment variables
        env_vars = {
            'DB_HOST': 'invalid_host',
            'DB_USERNAME': 'testuser',
            'DB_PASSWORD': 'wrongpass',
            'DB_NAME': 'testdb'
        }
        mock_getenv.side_effect = lambda key: env_vars.get(key)
        
        # Setup mock error
        error_msg = "Access denied for user 'testuser'@'invalid_host'"
        mock_connect.side_effect = mysql.connector.Error(error_msg)
        
        # Execute
        result = create_connection()
        
        # Assert
        assert result is None
        mock_connect.assert_called_once_with(
            host='invalid_host',
            user='testuser',
            password='wrongpass',
            database='testdb'
        )
        mock_print.assert_called_once_with(f"Error: {error_msg}")
    
    @patch('db.connection.os.getenv')
    @patch('db.connection.mysql.connector.connect')
    def test_create_connection_with_none_env_vars(self, mock_connect, mock_getenv):
        """Test create_connection dengan environment variables None"""
        # Setup environment variables sebagai None
        mock_getenv.return_value = None
        
        # Setup mock connection
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        # Execute
        result = create_connection()
        
        # Assert
        assert result == mock_conn
        mock_connect.assert_called_once_with(
            host=None,
            user=None,
            password=None,
            database=None
        )
    
    @patch('db.connection.os.getenv')
    @patch('db.connection.mysql.connector.connect')
    def test_create_connection_with_empty_env_vars(self, mock_connect, mock_getenv):
        """Test create_connection dengan environment variables kosong"""
        # Setup environment variables sebagai empty string
        mock_getenv.return_value = ""
        
        # Setup mock connection
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        # Execute
        result = create_connection()
        
        # Assert
        assert result == mock_conn
        mock_connect.assert_called_once_with(
            host="",
            user="",
            password="",
            database=""
        )


class TestCreateLocalConnection:
    """Test cases untuk fungsi create_local_connection"""
    
    @patch('db.connection.os.getenv')
    @patch('db.connection.mysql.connector.connect')
    def test_create_local_connection_success(self, mock_connect, mock_getenv):
        """Test create_local_connection berhasil membuat koneksi"""
        # Setup environment variables
        env_vars = {
            'DB_HOST_LOCAL': '127.0.0.1',
            'DB_USERNAME_LOCAL': 'localuser',
            'DB_PASSWORD_LOCAL': 'localpass',
            'DB_NAME_LOCAL': 'localdb'
        }
        mock_getenv.side_effect = lambda key: env_vars.get(key)
        
        # Setup mock connection
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        # Execute
        result = create_local_connection()
        
        # Assert
        assert result == mock_conn
        mock_connect.assert_called_once_with(
            host='127.0.0.1',
            user='localuser',
            password='localpass',
            database='localdb'
        )
        
        # Verify all environment variables were accessed
        expected_calls = ['DB_HOST_LOCAL', 'DB_USERNAME_LOCAL', 'DB_PASSWORD_LOCAL', 'DB_NAME_LOCAL']
        for env_var in expected_calls:
            mock_getenv.assert_any_call(env_var)
    
    @patch('db.connection.os.getenv')
    @patch('db.connection.mysql.connector.connect')
    @patch('builtins.print')
    def test_create_local_connection_mysql_error(self, mock_print, mock_connect, mock_getenv):
        """Test create_local_connection ketika terjadi MySQL error"""
        # Setup environment variables
        env_vars = {
            'DB_HOST_LOCAL': 'localhost',
            'DB_USERNAME_LOCAL': 'localuser',
            'DB_PASSWORD_LOCAL': 'wrongpass',
            'DB_NAME_LOCAL': 'localdb'
        }
        mock_getenv.side_effect = lambda key: env_vars.get(key)
        
        # Setup mock error
        error_msg = "Connection refused"
        mock_connect.side_effect = mysql.connector.Error(error_msg)
        
        # Execute
        result = create_local_connection()
        
        # Assert
        assert result is None
        mock_connect.assert_called_once_with(
            host='localhost',
            user='localuser',
            password='wrongpass',
            database='localdb'
        )
        mock_print.assert_called_once_with(f"Error: {error_msg}")
    
    @patch('db.connection.os.getenv')
    @patch('db.connection.mysql.connector.connect')
    def test_create_local_connection_with_none_env_vars(self, mock_connect, mock_getenv):
        """Test create_local_connection dengan environment variables None"""
        # Setup environment variables sebagai None
        mock_getenv.return_value = None
        
        # Setup mock connection
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        # Execute
        result = create_local_connection()
        
        # Assert
        assert result == mock_conn
        mock_connect.assert_called_once_with(
            host=None,
            user=None,
            password=None,
            database=None
        )


class TestConnectionComparison:
    """Test perbandingan antara kedua fungsi connection"""
    
    @patch('db.connection.os.getenv')
    @patch('db.connection.mysql.connector.connect')
    def test_both_connections_use_different_env_vars(self, mock_connect, mock_getenv):
        """Test bahwa kedua fungsi menggunakan environment variables yang berbeda"""
        # Setup environment variables untuk kedua fungsi
        env_vars = {
            'DB_HOST': 'remote_host',
            'DB_USERNAME': 'remote_user',
            'DB_PASSWORD': 'remote_pass',
            'DB_NAME': 'remote_db',
            'DB_HOST_LOCAL': 'local_host',
            'DB_USERNAME_LOCAL': 'local_user',
            'DB_PASSWORD_LOCAL': 'local_pass',
            'DB_NAME_LOCAL': 'local_db'
        }
        mock_getenv.side_effect = lambda key: env_vars.get(key)
        
        # Setup mock connections
        mock_conn1 = Mock()
        mock_conn2 = Mock()
        mock_connect.side_effect = [mock_conn1, mock_conn2]
        
        # Execute both functions
        result1 = create_connection()
        result2 = create_local_connection()
        
        # Assert
        assert result1 == mock_conn1
        assert result2 == mock_conn2
        assert result1 != result2
        
        # Verify correct parameters were passed
        expected_calls = [
            ((), {'host': 'remote_host', 'user': 'remote_user', 'password': 'remote_pass', 'database': 'remote_db'}),
            ((), {'host': 'local_host', 'user': 'local_user', 'password': 'local_pass', 'database': 'local_db'})
        ]
        
        assert mock_connect.call_count == 2
        actual_calls = mock_connect.call_args_list
        for i, (expected_args, expected_kwargs) in enumerate(expected_calls):
            actual_args, actual_kwargs = actual_calls[i]
            assert actual_args == expected_args
            assert actual_kwargs == expected_kwargs


class TestConnectionErrorTypes:
    """Test berbagai jenis error yang mungkin terjadi"""
    
    @patch('db.connection.os.getenv')
    @patch('db.connection.mysql.connector.connect')
    @patch('builtins.print')
    def test_create_connection_database_error(self, mock_print, mock_connect, mock_getenv):
        """Test create_connection dengan DatabaseError"""
        # Setup
        mock_getenv.side_effect = lambda key: f"test_{key.lower()}"
        error_msg = "Unknown database 'test_db_name'"
        mock_connect.side_effect = mysql.connector.DatabaseError(error_msg)
        
        # Execute
        result = create_connection()
        
        # Assert
        assert result is None
        mock_print.assert_called_once_with(f"Error: {error_msg}")
    
    @patch('db.connection.os.getenv')
    @patch('db.connection.mysql.connector.connect')
    @patch('builtins.print')
    def test_create_connection_programming_error(self, mock_print, mock_connect, mock_getenv):
        """Test create_connection dengan ProgrammingError"""
        # Setup
        mock_getenv.side_effect = lambda key: f"test_{key.lower()}"
        error_msg = "Programming error in connection"
        mock_connect.side_effect = mysql.connector.ProgrammingError(error_msg)
        
        # Execute
        result = create_connection()
        
        # Assert
        assert result is None
        mock_print.assert_called_once_with(f"Error: {error_msg}")
    
    @patch('db.connection.os.getenv')
    @patch('db.connection.mysql.connector.connect')
    @patch('builtins.print')
    def test_create_local_connection_interface_error(self, mock_print, mock_connect, mock_getenv):
        """Test create_local_connection dengan InterfaceError"""
        # Setup
        mock_getenv.side_effect = lambda key: f"local_{key.lower()}"
        error_msg = "Interface error occurred"
        mock_connect.side_effect = mysql.connector.InterfaceError(error_msg)
        
        # Execute
        result = create_local_connection()
        
        # Assert
        assert result is None
        mock_print.assert_called_once_with(f"Error: {error_msg}")


class TestEnvironmentVariableHandling:
    """Test handling environment variables secara detail"""
    
    @patch('db.connection.mysql.connector.connect')
    def test_create_connection_missing_load_dotenv(self, mock_connect):
        """Test create_connection tanpa load_dotenv (menggunakan system env vars)"""
        # Setup mock connection
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        # Setup system environment variables
        with patch.dict(os.environ, {
            'DB_HOST': 'system_host',
            'DB_USERNAME': 'system_user',
            'DB_PASSWORD': 'system_pass',
            'DB_NAME': 'system_db'
        }, clear=False):
            
            # Execute
            result = create_connection()
            
            # Assert
            assert result == mock_conn
            mock_connect.assert_called_once_with(
                host='system_host',
                user='system_user',
                password='system_pass',
                database='system_db'
            )
    
    @patch('db.connection.mysql.connector.connect')
    def test_create_local_connection_with_system_env(self, mock_connect):
        """Test create_local_connection dengan system environment variables"""
        # Setup mock connection
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        # Setup system environment variables
        with patch.dict(os.environ, {
            'DB_HOST_LOCAL': 'system_local_host',
            'DB_USERNAME_LOCAL': 'system_local_user',
            'DB_PASSWORD_LOCAL': 'system_local_pass',
            'DB_NAME_LOCAL': 'system_local_db'
        }, clear=False):
            
            # Execute
            result = create_local_connection()
            
            # Assert
            assert result == mock_conn
            mock_connect.assert_called_once_with(
                host='system_local_host',
                user='system_local_user',
                password='system_local_pass',
                database='system_local_db'
            )


# Parametrized tests untuk berbagai skenario error
@pytest.mark.parametrize("error_class,error_message", [
    (mysql.connector.Error, "Generic MySQL error"),
    (mysql.connector.DatabaseError, "Database does not exist"),
    (mysql.connector.InterfaceError, "Connection interface error"),
    (mysql.connector.ProgrammingError, "SQL programming error"),
    (mysql.connector.OperationalError, "Operational error occurred"),
])
def test_create_connection_various_errors(error_class, error_message):
    """Test parametrized untuk berbagai jenis MySQL errors"""
    with patch('db.connection.os.getenv') as mock_getenv, \
         patch('db.connection.mysql.connector.connect') as mock_connect, \
         patch('builtins.print') as mock_print:
        
        # Setup
        mock_getenv.side_effect = lambda key: f"test_{key.lower()}"
        mock_connect.side_effect = error_class(error_message)
        
        # Execute
        result = create_connection()
        
        # Assert
        assert result is None
        mock_print.assert_called_once_with(f"Error: {error_message}")


@pytest.mark.parametrize("function_name,env_vars", [
    ("create_connection", ['DB_HOST', 'DB_USERNAME', 'DB_PASSWORD', 'DB_NAME']),
    ("create_local_connection", ['DB_HOST_LOCAL', 'DB_USERNAME_LOCAL', 'DB_PASSWORD_LOCAL', 'DB_NAME_LOCAL']),
])
def test_connection_functions_env_var_usage(function_name, env_vars):
    """Test parametrized untuk penggunaan environment variables"""
    with patch('db.connection.os.getenv') as mock_getenv, \
         patch('db.connection.mysql.connector.connect') as mock_connect:
        
        # Setup
        mock_getenv.side_effect = lambda key: f"value_for_{key}"
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        # Execute
        if function_name == "create_connection":
            result = create_connection()
        else:
            result = create_local_connection()
        
        # Assert
        assert result == mock_conn
        
        # Verify all required environment variables were accessed
        for env_var in env_vars:
            mock_getenv.assert_any_call(env_var)
        
        assert mock_getenv.call_count == len(env_vars)


class TestConnectionIntegration:
    """Integration tests untuk connection functions"""
    
    @patch('db.connection.mysql.connector.connect')
    def test_connection_returns_mysql_connector_object(self, mock_connect):
        """Test bahwa connection mengembalikan object MySQL connector yang benar"""
        # Setup realistic mock
        mock_conn = MagicMock()
        mock_conn.is_connected.return_value = True
        mock_conn.cursor.return_value = Mock()
        mock_connect.return_value = mock_conn
        
        with patch.dict(os.environ, {
            'DB_HOST': 'localhost',
            'DB_USERNAME': 'testuser',
            'DB_PASSWORD': 'testpass',
            'DB_NAME': 'testdb'
        }):
            
            # Execute
            conn = create_connection()
            
            # Assert
            assert conn is not None
            assert hasattr(conn, 'is_connected')
            assert hasattr(conn, 'cursor')
            assert conn.is_connected() is True
    
    @patch('db.connection.mysql.connector.connect')
    def test_local_connection_returns_mysql_connector_object(self, mock_connect):
        """Test bahwa local connection mengembalikan object MySQL connector yang benar"""
        # Setup realistic mock
        mock_conn = MagicMock()
        mock_conn.is_connected.return_value = True
        mock_conn.cursor.return_value = Mock()
        mock_connect.return_value = mock_conn
        
        with patch.dict(os.environ, {
            'DB_HOST_LOCAL': 'localhost',
            'DB_USERNAME_LOCAL': 'testuser',
            'DB_PASSWORD_LOCAL': 'testpass',
            'DB_NAME_LOCAL': 'testdb'
        }):
            
            # Execute
            conn = create_local_connection()
            
            # Assert
            assert conn is not None
            assert hasattr(conn, 'is_connected')
            assert hasattr(conn, 'cursor')
            assert conn.is_connected() is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])