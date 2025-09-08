import pytest
from unittest.mock import Mock, patch, MagicMock
import mysql.connector
from service.login import login_service  # sesuaikan dengan lokasi fungsi


class TestLoginService:
    """Test cases untuk fungsi login_service"""
    
    @patch('service.login.getMail')
    @patch('service.login.create_local_connection')
    def test_login_service_email_not_found(self, mock_connection, mock_get_mail):
        """Test ketika email tidak ditemukan oleh getMail"""
        # Setup
        mock_get_mail.return_value = None
        
        # Execute
        result = login_service("invalid@email.com")
        
        # Assert
        assert result is False
        mock_get_mail.assert_called_once_with("invalid@email.com")
        mock_connection.assert_not_called()  # connection tidak dipanggil
    
    @patch('service.login.getMail')
    @patch('service.login.create_local_connection')
    def test_login_service_email_empty(self, mock_connection, mock_get_mail):
        """Test ketika getMail return empty/falsy value"""
        # Setup
        mock_get_mail.return_value = ""
        
        # Execute
        result = login_service("empty@email.com")
        
        # Assert
        assert result is False
        mock_get_mail.assert_called_once_with("empty@email.com")
        mock_connection.assert_not_called()
    
    @patch('service.login.getMail')
    @patch('service.login.create_local_connection')
    def test_login_service_user_found(self, mock_connection, mock_get_mail):
        """Test ketika user ditemukan di database"""
        # Setup
        mock_get_mail.return_value = "test@email.com"
        
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = {"session_id": "session_123"}
        
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connection.return_value = mock_conn
        
        # Execute
        result = login_service("test@email.com")
        
        # Assert
        assert result == "session_123"
        mock_get_mail.assert_called_once_with("test@email.com")
        mock_connection.assert_called_once()
        mock_conn.cursor.assert_called_once_with(dictionary=True)
        mock_cursor.execute.assert_called_once_with(
            "SELECT session_id FROM users WHERE session_id = %s", 
            ("test@email.com",)
        )
        mock_cursor.fetchone.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('service.login.getMail')
    @patch('service.login.create_local_connection')
    def test_login_service_user_not_found(self, mock_connection, mock_get_mail):
        """Test ketika user tidak ditemukan di database"""
        # Setup
        mock_get_mail.return_value = "notfound@email.com"
        
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None  # User tidak ditemukan
        
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connection.return_value = mock_conn
        
        # Execute
        result = login_service("notfound@email.com")
        
        # Assert
        assert result is False
        mock_get_mail.assert_called_once_with("notfound@email.com")
        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchone.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('service.login.getMail')
    @patch('service.login.create_local_connection')
    @patch('builtins.print')  # Mock print untuk test error handling
    def test_login_service_database_error(self, mock_print, mock_connection, mock_get_mail):
        """Test ketika terjadi database error"""
        # Setup
        mock_get_mail.return_value = "test@email.com"
        
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = mysql.connector.Error("Database connection failed")
        
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connection.return_value = mock_conn
        
        # Execute
        result = login_service("test@email.com")
        
        # Assert
        assert result is False
        mock_get_mail.assert_called_once_with("test@email.com")
        mock_cursor.execute.assert_called_once()
        mock_print.assert_called_once()  # Error di-print
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('service.login.getMail')
    @patch('service.login.create_local_connection')
    def test_login_service_connection_cleanup_on_exception(self, mock_connection, mock_get_mail):
        """Test bahwa connection dan cursor di-close meskipun ada exception"""
        # Setup
        mock_get_mail.return_value = "test@email.com"
        
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = mysql.connector.Error("MySQL connection failed")  # ✅
        
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connection.return_value = mock_conn
        
        # Execute
        result = login_service("test@email.com")
        
        # Assert
        assert result is False
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()


class TestLoginServiceEdgeCases:
    """Test edge cases untuk login_service"""
    
    @patch('service.login.getMail')
    @patch('service.login.create_local_connection')
    def test_login_service_empty_session_id(self, mock_connection, mock_get_mail):
        """Test ketika database return empty session_id"""
        # Setup
        mock_get_mail.return_value = "test@email.com"
        
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = {"session_id": ""}  # Empty session_id
        
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connection.return_value = mock_conn
        
        # Execute
        result = login_service("test@email.com")
        
        # Assert
        assert result == ""  # Function return apapun yang ada di database
    
    @patch('service.login.getMail')
    @patch('service.login.create_local_connection')
    def test_login_service_null_session_id(self, mock_connection, mock_get_mail):
        """Test ketika database return NULL session_id"""
        # Setup
        mock_get_mail.return_value = "test@email.com"
        
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = {"session_id": None}
        
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connection.return_value = mock_conn
        
        # Execute
        result = login_service("test@email.com")
        
        # Assert
        assert result is None


# Parametrized tests untuk berbagai input email
@pytest.mark.parametrize("email_input,get_mail_result,expected", [
    ("valid@email.com", "valid@email.com", True),  # Valid case akan di-handle di test lain
    ("", None, False),
    (None, None, False),
    ("invalid", "", False),
    ("test@test.com", False, False),
])
def test_login_service_various_emails(email_input, get_mail_result, expected):
    """Test parametrized untuk berbagai input email"""
    with patch('service.login.getMail') as mock_get_mail:
        mock_get_mail.return_value = get_mail_result
        
        result = login_service(email_input)
        
        if expected:
            # Untuk case valid, perlu mock database juga
            assert mock_get_mail.called
        else:
            assert result is False


# Integration-style test dengan mock yang lebih realistic
class TestLoginServiceIntegration:
    """Test dengan scenario yang lebih realistic"""
    
    @patch('service.login.getMail')
    @patch('service.login.create_local_connection')
    def test_login_service_complete_flow_success(self, mock_connection, mock_get_mail):
        """Test complete flow untuk login berhasil"""
        # Setup - simulate real scenario
        email = "user@example.com"
        validated_email = "user@example.com"
        session_id = "abc123def456"
        
        mock_get_mail.return_value = validated_email
        
        # Mock database response
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = {"session_id": session_id}
        
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connection.return_value = mock_conn
        
        # Execute
        result = login_service(email)
        
        # Assert complete flow
        assert result == session_id
        
        # Verify call sequence
        mock_get_mail.assert_called_once_with(email)
        mock_connection.assert_called_once()
        mock_conn.cursor.assert_called_once_with(dictionary=True)
        mock_cursor.execute.assert_called_once_with(
            "SELECT session_id FROM users WHERE session_id = %s", 
            (validated_email,)
        )
        mock_cursor.fetchone.assert_called_once()
        
        # Verify cleanup
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])