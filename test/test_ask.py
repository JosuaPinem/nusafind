import pytest
from unittest.mock import Mock, patch, MagicMock
import mysql.connector
from service.ask import askService


class TestAskService:
    """Test cases untuk class askService"""
    
    def setup_method(self):
        """Setup method yang dipanggil sebelum setiap test"""
        self.ask_service = askService()
    
    # Tests untuk ask_service method
    @patch('service.ask.isQuery')
    @patch('service.ask.fillterQuestion')
    def test_ask_service_not_query_and_filter_false(self, mock_filter, mock_is_query):
        """Test ketika bukan query dan filter false"""
        # Setup
        mock_is_query.return_value = "Tidak"
        mock_filter.return_value = "False"
        
        # Execute
        answer, query = self.ask_service.ask_service("random question", "session123")
        
        # Assert
        expected_message = "Mohon maaf sebelumnya, permintaan yang Anda ajukan tidak dapat diproses karena tidak sesuai dengan data yang tersedia. Untuk data yang anda butuhkan silahkan hubungi Tim BIS untuk membantu Anda!."
        assert answer == expected_message
        assert query is None
        
        mock_is_query.assert_called_once_with("random question")
        mock_filter.assert_called_once_with("random question")
    
    @patch('service.ask.isQuery')
    @patch('service.ask.fillterQuestion')
    @patch('service.ask.createQuery')
    @patch('service.ask.getRawData')
    @patch('service.ask.createAnswer')
    @patch('service.ask.saveData')
    def test_ask_service_not_query_but_filter_true(self, mock_save, mock_answer, mock_raw_data, 
                                                   mock_create_query, mock_filter, mock_is_query):
        """Test ketika bukan query tapi filter true, proses dilanjutkan"""
        # Setup
        mock_is_query.return_value = "Tidak"
        mock_filter.return_value = "True"  # Filter passed
        mock_create_query.return_value = "SELECT * FROM table"
        mock_raw_data.return_value = [{"data": "test"}]
        mock_answer.return_value = "Test answer"
        mock_save.return_value = True
        
        # Execute
        answer, query = self.ask_service.ask_service("filtered question", "session123")
        
        # Assert
        assert answer == "Test answer"
        assert query == "SELECT * FROM table"
        
        mock_is_query.assert_called_once_with("filtered question")
        mock_filter.assert_called_once_with("filtered question")
        mock_create_query.assert_called_once_with("filtered question")
        mock_save.assert_called_once()
    
    @patch('service.ask.isQuery')
    @patch('service.ask.createQuery')
    def test_ask_service_create_query_returns_none(self, mock_create_query, mock_is_query):
        """Test ketika createQuery return None"""
        # Setup
        mock_is_query.return_value = "Ya"  # Is a query
        mock_create_query.return_value = None
        
        # Execute
        answer, query = self.ask_service.ask_service("query question", "session123")
        
        # Assert
        assert answer is None
        assert query is None
        
        mock_is_query.assert_called_once_with("query question")
        mock_create_query.assert_called_once_with("query question")
    
    @patch('service.ask.isQuery')
    @patch('service.ask.createQuery')
    @patch('service.ask.getRawData')
    def test_ask_service_get_raw_data_returns_none(self, mock_raw_data, mock_create_query, mock_is_query):
        """Test ketika getRawData return None"""
        # Setup
        mock_is_query.return_value = "Ya"
        mock_create_query.return_value = "SELECT * FROM table"
        mock_raw_data.return_value = None
        
        # Execute
        answer, query = self.ask_service.ask_service("query question", "session123")
        
        # Assert
        assert answer is None
        assert query is None
        
        mock_raw_data.assert_called_once_with("SELECT * FROM table")
    
    @patch('service.ask.isQuery')
    @patch('service.ask.createQuery')
    @patch('service.ask.getRawData')
    @patch('service.ask.createAnswer')
    def test_ask_service_create_answer_returns_none(self, mock_answer, mock_raw_data, 
                                                   mock_create_query, mock_is_query):
        """Test ketika createAnswer return None"""
        # Setup
        mock_is_query.return_value = "Ya"
        mock_create_query.return_value = "SELECT * FROM table"
        mock_raw_data.return_value = [{"data": "test"}]
        mock_answer.return_value = None
        
        # Execute
        answer, query = self.ask_service.ask_service("query question", "session123")
        
        # Assert
        assert answer is None
        assert query is None
        
        mock_answer.assert_called_once_with([{"data": "test"}], "SELECT * FROM table", "query question")
    
    @patch('service.ask.isQuery')
    @patch('service.ask.createQuery')
    @patch('service.ask.getRawData')
    @patch('service.ask.createAnswer')
    @patch('service.ask.saveData')
    def test_ask_service_save_data_returns_false(self, mock_save, mock_answer, mock_raw_data,
                                                 mock_create_query, mock_is_query):
        """Test ketika saveData return False"""
        # Setup
        mock_is_query.return_value = "Ya"
        mock_create_query.return_value = "SELECT * FROM table"
        mock_raw_data.return_value = [{"data": "test"}]
        mock_answer.return_value = "Test answer"
        mock_save.return_value = False
        
        # Execute
        answer, query = self.ask_service.ask_service("query question", "session123")
        
        # Assert
        assert answer == "Mohon maaf data tidak berhasil disimpan."
        assert query == ""
        
        mock_save.assert_called_once_with("session123", "query question", "SELECT * FROM table", 
                                         [{"data": "test"}], "Test answer")
    
    @patch('service.ask.isQuery')
    @patch('service.ask.createQuery')
    @patch('service.ask.getRawData')
    @patch('service.ask.createAnswer')
    @patch('service.ask.saveData')
    def test_ask_service_success_flow(self, mock_save, mock_answer, mock_raw_data,
                                     mock_create_query, mock_is_query):
        """Test happy path - semua step berhasil"""
        # Setup
        mock_is_query.return_value = "Ya"
        mock_create_query.return_value = "SELECT * FROM users WHERE active = 1"
        mock_raw_data.return_value = [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]
        mock_answer.return_value = "Found 2 active users: John and Jane"
        mock_save.return_value = True
        
        # Execute
        answer, query = self.ask_service.ask_service("Show me active users", "session456")
        
        # Assert
        assert answer == "Found 2 active users: John and Jane"
        assert query == "SELECT * FROM users WHERE active = 1"
        
        # Verify all functions called in correct order
        mock_is_query.assert_called_once_with("Show me active users")
        mock_create_query.assert_called_once_with("Show me active users")
        mock_raw_data.assert_called_once_with("SELECT * FROM users WHERE active = 1")
        mock_answer.assert_called_once_with(
            [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}],
            "SELECT * FROM users WHERE active = 1",
            "Show me active users"
        )
        mock_save.assert_called_once_with(
            "session456", 
            "Show me active users", 
            "SELECT * FROM users WHERE active = 1",
            [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}],
            "Found 2 active users: John and Jane"
        )


class TestAskServiceGetChatHis:
    """Test cases untuk method getChatHis"""
    
    def setup_method(self):
        """Setup method yang dipanggil sebelum setiap test"""
        self.ask_service = askService()
    
    @patch('service.ask.create_local_connection')
    def test_get_chat_his_success(self, mock_connection):
        """Test getChatHis berhasil mengambil data"""
        # Setup
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            {"id": 1, "session_id": "session123", "question": "Q1", "answer": "A1", "time": "2025-01-01"},
            {"id": 2, "session_id": "session123", "question": "Q2", "answer": "A2", "time": "2025-01-02"}
        ]
        
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connection.return_value = mock_conn
        
        # Execute
        result = self.ask_service.getChatHis("session123")
        
        # Assert
        assert len(result) == 2
        assert result[0]["question"] == "Q1"
        assert result[1]["question"] == "Q2"
        
        mock_connection.assert_called_once()
        mock_conn.cursor.assert_called_once_with(dictionary=True)
        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM log WHERE session_id = %s ORDER BY time DESC LIMIT 4",
            ("session123",)
        )
        mock_cursor.fetchall.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('service.ask.create_local_connection')
    def test_get_chat_his_empty_result(self, mock_connection):
        """Test getChatHis dengan hasil kosong"""
        # Setup
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = []
        
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connection.return_value = mock_conn
        
        # Execute
        result = self.ask_service.getChatHis("nonexistent_session")
        
        # Assert
        assert result == []
        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM log WHERE session_id = %s ORDER BY time DESC LIMIT 4",
            ("nonexistent_session",)
        )
    
    @patch('service.ask.create_local_connection')
    @patch('builtins.print')
    def test_get_chat_his_database_error(self, mock_print, mock_connection):
        """Test getChatHis dengan database error"""
        # Setup
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = mysql.connector.Error("Database connection failed")
        
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connection.return_value = mock_conn
        
        # Execute
        result = self.ask_service.getChatHis("session123")
        
        # Assert
        assert result is None
        mock_cursor.execute.assert_called_once()
        mock_print.assert_called_once()  # Error message printed
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('service.ask.create_local_connection')
    def test_get_chat_his_connection_cleanup(self, mock_connection):
        """Test bahwa connection cleanup terjadi meskipun ada error"""
        # Setup
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = mysql.connector.Error("Connection lost")
        
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connection.return_value = mock_conn
        
        # Execute
        result = self.ask_service.getChatHis("session123")
        
        # Assert cleanup happened
        assert result is None
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()


class TestAskServiceEdgeCases:
    """Test edge cases untuk askService"""
    
    def setup_method(self):
        self.ask_service = askService()
    
    @patch('service.ask.isQuery')
    def test_ask_service_empty_question(self, mock_is_query):
        """Test dengan question kosong"""
        mock_is_query.return_value = "Tidak"
        
        with patch('service.ask.fillterQuestion') as mock_filter:
            mock_filter.return_value = "False"
            
            answer, query = self.ask_service.ask_service("", "session123")
            
            expected_message = "Mohon maaf sebelumnya, permintaan yang Anda ajukan tidak dapat diproses karena tidak sesuai dengan data yang tersedia. Untuk data yang anda butuhkan silahkan hubungi Tim BIS untuk membantu Anda!."
            assert answer == expected_message
            assert query is None
    
    @patch('service.ask.create_local_connection')
    def test_get_chat_his_empty_session_id(self, mock_connection):
        """Test getChatHis dengan session_id kosong"""
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = []
        
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connection.return_value = mock_conn
        
        result = self.ask_service.getChatHis("")
        
        assert result == []
        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM log WHERE session_id = %s ORDER BY time DESC LIMIT 4",
            ("",)
        )


# Parametrized tests
@pytest.mark.parametrize("is_query_result,filter_result,should_continue", [
    ("Ya", None, True),      # Is query, no filter check needed
    ("Tidak", "True", True), # Not query but filter passed
    ("Tidak", "False", False), # Not query and filter failed
])
def test_ask_service_flow_control(is_query_result, filter_result, should_continue):
    """Test parametrized untuk flow control logic"""
    ask_service = askService()
    
    with patch('service.ask.isQuery') as mock_is_query, \
         patch('service.ask.fillterQuestion') as mock_filter:
        
        mock_is_query.return_value = is_query_result
        if filter_result:
            mock_filter.return_value = filter_result
        
        if should_continue:
            # Mock remaining functions for successful flow
            with patch('service.ask.createQuery') as mock_create_query, \
                 patch('service.ask.getRawData') as mock_raw_data, \
                 patch('service.ask.createAnswer') as mock_answer, \
                 patch('service.ask.saveData') as mock_save:
                
                mock_create_query.return_value = "SELECT 1"
                mock_raw_data.return_value = [{"test": "data"}]
                mock_answer.return_value = "Test answer"
                mock_save.return_value = True
                
                answer, query = ask_service.ask_service("test question", "session123")
                
                assert answer == "Test answer"
                assert query == "SELECT 1"
        else:
            answer, query = ask_service.ask_service("test question", "session123")
            
            expected_message = "Mohon maaf sebelumnya, permintaan yang Anda ajukan tidak dapat diproses karena tidak sesuai dengan data yang tersedia. Untuk data yang anda butuhkan silahkan hubungi Tim BIS untuk membantu Anda!."
            assert answer == expected_message
            assert query is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])