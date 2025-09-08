import pytest
from unittest.mock import Mock, patch, MagicMock
import mysql.connector
from model.model import (
    clean_sql, fillterQuestion, createQuery, getRawData, 
    createAnswer, getMail, saveData, isQuery
)


class TestCleanSql:
    """Test cases untuk fungsi clean_sql"""
    
    def test_clean_sql_with_sql_code_blocks(self):
        """Test membersihkan SQL dengan code blocks"""
        input_sql = """```sql
        SELECT * FROM users WHERE active = 1
        ```"""
        
        result = clean_sql(input_sql)
        
        # Should contain formatted SQL
        assert "SELECT" in result.upper()
        assert "FROM" in result.upper()
        assert "WHERE" in result.upper()
        assert "```" not in result  # Code blocks removed
    
    def test_clean_sql_with_generic_code_blocks(self):
        """Test dengan generic code blocks (tanpa sql tag)"""
        input_sql = """```
        select id, name from products
        ```"""
        
        result = clean_sql(input_sql)
        
        assert "SELECT" in result.upper()
        assert "FROM" in result.upper()
        assert "```" not in result
    
    def test_clean_sql_without_code_blocks(self):
        """Test SQL tanpa code blocks"""
        input_sql = "select id, name from users where active=1"
        
        result = clean_sql(input_sql)
        
        assert "SELECT" in result.upper()
        assert "FROM" in result.upper()
        assert "WHERE" in result.upper()
    
    def test_clean_sql_with_escaped_newlines(self):
        """Test SQL dengan escaped newlines"""
        input_sql = "SELECT *\\nFROM users\\nWHERE active = 1"
        
        result = clean_sql(input_sql)
        
        # Should convert \\n to actual newlines and format properly
        assert "SELECT" in result.upper()
        assert "\n" in result  # Real newlines
        assert "\\n" not in result  # No escaped newlines
    
    def test_clean_sql_empty_string(self):
        """Test dengan string kosong"""
        result = clean_sql("")
        assert result == ""
    
    def test_clean_sql_complex_query(self):
        """Test dengan complex SQL query"""
        input_sql = """```sql
        SELECT i.cid, i.csid, i.description,
               (CASE WHEN i.paid = 1 THEN i.amount ELSE i.amount * 1.1 END) AS total_amount
        FROM invoice i JOIN service_internet si ON i.csid = si.csid
        WHERE MONTH(i.created_at) = 3 AND YEAR(i.created_at) = 2025
        ORDER BY total_amount DESC LIMIT 5;
        ```"""
        
        result = clean_sql(input_sql)
        
        assert "SELECT" in result
        assert "FROM" in result
        assert "JOIN" in result
        assert "WHERE" in result
        assert "ORDER BY" in result
        assert "LIMIT" in result


class TestLLMBasedFunctions:
    """Test functions yang menggunakan LLM"""
    
    @patch('model.model.llm')
    @patch('model.model.promptFilter')
    def test_fillter_question_success(self, mock_prompt, mock_llm):
        """Test fillterQuestion berhasil"""
        # Setup
        mock_prompt.format.return_value = "formatted prompt"
        mock_response = Mock()
        mock_response.content = "True"
        mock_llm.invoke.return_value = mock_response
        
        # Execute
        result = fillterQuestion("Is this a valid question?")
        
        # Assert
        assert result == "True"
        mock_prompt.format.assert_called_once_with(question="Is this a valid question?")
        mock_llm.invoke.assert_called_once_with("formatted prompt")
    
    @patch('model.model.llm')
    @patch('model.model.promptConvertQuery')
    @patch('model.model.clean_sql')
    def test_create_query_success(self, mock_clean_sql, mock_prompt, mock_llm):
        """Test createQuery berhasil"""
        # Setup
        mock_prompt.format.return_value = "formatted prompt"
        mock_response = Mock()
        mock_response.content = "SELECT * FROM users"
        mock_llm.invoke.return_value = mock_response
        mock_clean_sql.return_value = "SELECT * FROM users;"
        
        # Execute
        result = createQuery("Show me all users")
        
        # Assert
        assert result == "SELECT * FROM users;"
        mock_prompt.format.assert_called_once_with(question="Show me all users")
        mock_llm.invoke.assert_called_once_with("formatted prompt")
        mock_clean_sql.assert_called_once_with("SELECT * FROM users")
    
    def test_create_query_empty_question(self):
        """Test createQuery dengan question kosong"""
        result = createQuery("")
        assert result is None
        
        result = createQuery(None)
        assert result is None
    
    @patch('model.model.llm')
    @patch('model.model.promptGetAnswer')
    def test_create_answer_success(self, mock_prompt, mock_llm):
        """Test createAnswer berhasil"""
        # Setup
        mock_prompt.format.return_value = "formatted prompt"
        mock_response = Mock()
        mock_response.content = "Here is your answer based on the data"
        mock_llm.invoke.return_value = mock_response
        
        raw_data = [{"id": 1, "name": "John"}]
        query = "SELECT * FROM users"
        question = "Show me users"
        
        # Execute
        result = createAnswer(raw_data, query, question)
        
        # Assert
        assert result == "Here is your answer based on the data"
        mock_prompt.format.assert_called_once_with(
            rawData=raw_data,
            query=query,
            question=question
        )
        mock_llm.invoke.assert_called_once_with("formatted prompt")
    
    @patch('model.model.llm')
    @patch('model.model.promptEmail')
    def test_get_mail_valid_email(self, mock_prompt, mock_llm):
        """Test getMail dengan email valid"""
        # Setup
        mock_prompt.format.return_value = "formatted prompt"
        mock_response = Mock()
        mock_response.content = "user@example.com"
        mock_llm.invoke.return_value = mock_response
        
        # Execute
        result = getMail("Please contact user@example.com")
        
        # Assert
        assert result == "user@example.com"
        mock_prompt.format.assert_called_once_with(response="Please contact user@example.com")
        mock_llm.invoke.assert_called_once_with("formatted prompt")
    
    @patch('model.model.llm')
    @patch('model.model.promptEmail')
    def test_get_mail_not_email(self, mock_prompt, mock_llm):
        """Test getMail bukan email"""
        # Setup
        mock_prompt.format.return_value = "formatted prompt"
        mock_response = Mock()
        mock_response.content = "Bukan Email"
        mock_llm.invoke.return_value = mock_response
        
        # Execute
        result = getMail("This is just a regular text")
        
        # Assert
        assert result is None
        mock_prompt.format.assert_called_once_with(response="This is just a regular text")
        mock_llm.invoke.assert_called_once_with("formatted prompt")
    
    @patch('model.model.llm')
    @patch('model.model.promptEmail')
    def test_get_mail_with_whitespace(self, mock_prompt, mock_llm):
        """Test getMail dengan whitespace"""
        # Setup
        mock_prompt.format.return_value = "formatted prompt"
        mock_response = Mock()
        mock_response.content = "  user@test.com  "
        mock_llm.invoke.return_value = mock_response
        
        # Execute
        result = getMail("Contact   user@test.com  ")
        
        # Assert
        assert result == "user@test.com"  # Should be stripped
    
    @patch('model.model.llm')
    @patch('model.model.promptFQ')
    def test_is_query_success(self, mock_prompt, mock_llm):
        """Test isQuery berhasil"""
        # Setup
        mock_prompt.format.return_value = "formatted prompt"
        mock_response = Mock()
        mock_response.content = "Ya"
        mock_llm.invoke.return_value = mock_response
        
        # Execute
        result = isQuery("Show me all users in the database")
        
        # Assert
        assert result == "Ya"
        mock_prompt.format.assert_called_once_with(question="Show me all users in the database")
        mock_llm.invoke.assert_called_once_with("formatted prompt")


class TestGetRawData:
    """Test untuk fungsi getRawData"""
    
    @patch('model.model.create_connection')
    def test_get_raw_data_success(self, mock_connection):
        """Test getRawData berhasil"""
        # Setup
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            {"id": 1, "name": "John"},
            {"id": 2, "name": "Jane"}
        ]
        
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connection.return_value = mock_conn
        
        # Execute
        result = getRawData("SELECT * FROM users")
        
        # Assert
        assert len(result) == 2
        assert result[0]["name"] == "John"
        assert result[1]["name"] == "Jane"
        
        mock_connection.assert_called_once()
        mock_conn.cursor.assert_called_once_with(dictionary=True)
        mock_cursor.execute.assert_called_once_with("SELECT * FROM users")
        mock_cursor.fetchall.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('model.model.create_connection')
    def test_get_raw_data_connection_none(self, mock_connection):
        """Test getRawData ketika connection None"""
        # Setup
        mock_connection.return_value = None
        
        # Execute
        result = getRawData("SELECT * FROM users")
        
        # Assert
        assert result is None
        mock_connection.assert_called_once()
    
    @patch('model.model.create_connection')
    @patch('builtins.print')
    def test_get_raw_data_mysql_error(self, mock_print, mock_connection):
        """Test getRawData dengan MySQL error"""
        # Setup
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = mysql.connector.Error("Table doesn't exist")
        
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connection.return_value = mock_conn
        
        # Execute
        result = getRawData("SELECT * FROM nonexistent_table")
        
        # Assert
        assert result is None
        mock_cursor.execute.assert_called_once_with("SELECT * FROM nonexistent_table")
        mock_print.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('model.model.create_connection')
    def test_get_raw_data_empty_result(self, mock_connection):
        """Test getRawData dengan hasil kosong"""
        # Setup
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = []
        
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connection.return_value = mock_conn
        
        # Execute
        result = getRawData("SELECT * FROM users WHERE id = 999")
        
        # Assert
        assert result == []
        mock_cursor.fetchall.assert_called_once()


class TestSaveData:
    """Test untuk fungsi saveData"""
    
    @patch('model.model.create_local_connection')
    def test_save_data_success(self, mock_connection):
        """Test saveData berhasil"""
        # Setup
        mock_cursor = Mock()
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connection.return_value = mock_conn
        
        session_id = "session123"
        question = "Show users"
        query = "SELECT * FROM users"
        raw_data = [{"id": 1, "name": "John"}]
        answer = "Found 1 user: John"
        
        # Execute
        result = saveData(session_id, question, query, raw_data, answer)
        
        # Assert
        assert result is True
        
        # Verify first INSERT (log table)
        expected_log_call = (
            "INSERT INTO log (session_id, question, query, rawData, respons, time) VALUES (%s, %s, %s, %s, %s, NOW())",
            (session_id, question, query, str(raw_data), answer)
        )
        
        # Verify second INSERT (history table)
        expected_history_call = (
            "INSERT INTO history (session_id, time, question, respons, query) VALUES (%s, NOW(), %s, %s, %s)",
            (session_id, question, answer, query)
        )
        
        # Check that both INSERTs were called
        assert mock_cursor.execute.call_count == 2
        mock_cursor.execute.assert_any_call(*expected_log_call)
        mock_cursor.execute.assert_any_call(*expected_history_call)
        
        # Check commits
        assert mock_conn.commit.call_count == 2
        
        # Check cleanup
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('model.model.create_local_connection')
    @patch('builtins.print')
    def test_save_data_mysql_error(self, mock_print, mock_connection):
        """Test saveData dengan MySQL error"""
        # Setup
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = mysql.connector.Error("Database error")
        
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connection.return_value = mock_conn
        
        # Execute
        result = saveData("session123", "question", "query", [], "answer")
        
        # Assert
        assert result is False
        mock_cursor.execute.assert_called_once()
        mock_print.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('model.model.create_local_connection')
    def test_save_data_connection_cleanup_on_error(self, mock_connection):
        """Test bahwa connection di-cleanup meski ada error"""
        # Setup
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = mysql.connector.Error("Connection lost")
        
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connection.return_value = mock_conn
        
        # Execute
        result = saveData("session123", "question", "query", [], "answer")
        
        # Assert
        assert result is False
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()


class TestModelIntegration:
    """Integration tests untuk kombinasi functions"""
    
    @patch('model.model.llm')
    @patch('model.model.create_connection')
    def test_query_flow_integration(self, mock_connection, mock_llm):
        """Test flow dari createQuery -> getRawData -> createAnswer"""
        # Setup createQuery
        mock_response1 = Mock()
        mock_response1.content = "SELECT * FROM users WHERE active = 1"
        
        # Setup createAnswer
        mock_response2 = Mock()
        mock_response2.content = "Found 2 active users"
        
        mock_llm.invoke.side_effect = [mock_response1, mock_response2]
        
        # Setup getRawData
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            {"id": 1, "name": "John", "active": 1},
            {"id": 2, "name": "Jane", "active": 1}
        ]
        
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connection.return_value = mock_conn
        
        # Execute flow
        question = "Show me active users"
        
        # Step 1: Create query
        with patch('model.model.promptConvertQuery') as mock_prompt1:
            mock_prompt1.format.return_value = "create query prompt"
            query = createQuery(question)
        
        # Step 2: Get raw data
        raw_data = getRawData(query)
        
        # Step 3: Create answer
        with patch('model.model.promptGetAnswer') as mock_prompt2:
            mock_prompt2.format.return_value = "create answer prompt"
            answer = createAnswer(raw_data, query, question)
        
        # Assert
        assert "SELECT" in query.upper()
        assert len(raw_data) == 2
        assert raw_data[0]["name"] == "John"
        assert answer == "Found 2 active users"


# Parametrized tests
@pytest.mark.parametrize("sql_input,expected_keywords", [
    ("```sql\nSELECT * FROM users\n```", ["SELECT", "FROM"]),
    ("```\nselect id from products\n```", ["SELECT", "FROM"]),
    ("select name from customers", ["SELECT", "FROM"]),
    ("", []),
])
def test_clean_sql_parametrized(sql_input, expected_keywords):
    """Test parametrized untuk clean_sql"""
    result = clean_sql(sql_input)
    
    for keyword in expected_keywords:
        assert keyword.upper() in result.upper()


@pytest.mark.parametrize("llm_response,expected_result", [
    ("True", "True"),
    ("False", "False"),
    ("Ya", "Ya"),
    ("Tidak", "Tidak"),
])
def test_filter_question_parametrized(llm_response, expected_result):
    """Test parametrized untuk fillterQuestion"""
    with patch('model.model.llm') as mock_llm, \
         patch('model.model.promptFilter') as mock_prompt:
        
        mock_prompt.format.return_value = "formatted prompt"
        mock_response = Mock()
        mock_response.content = llm_response
        mock_llm.invoke.return_value = mock_response
        
        result = fillterQuestion("test question")
        
        assert result == expected_result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])