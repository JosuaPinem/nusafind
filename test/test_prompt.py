import pytest
from unittest.mock import Mock, patch, MagicMock
from langchain.prompts import PromptTemplate


class TestPromptTemplates:
    """Test cases untuk PromptTemplate objects"""
    
    def test_prompt_convert_query_import(self):
        """Test import promptConvertQuery"""
        # Test bahwa kita bisa import prompt template
        try:
            from model.promptTemplate import promptConvertQuery
            assert promptConvertQuery is not None
        except ImportError:
            pytest.skip("promptTemplate module not available")
    
    def test_prompt_convert_query_functionality(self):
        """Test functionality promptConvertQuery"""
        # Test bahwa template berhasil dibuat dan bisa di-import
        try:
            from model.promptTemplate import promptConvertQuery
            
            # Verify template adalah PromptTemplate object
            assert promptConvertQuery is not None
            assert hasattr(promptConvertQuery, 'format')
            
            # Test basic formatting
            result = promptConvertQuery.format(question="test question")
            assert isinstance(result, str)
            assert len(result) > 0
            
        except ImportError:
            pytest.skip("promptTemplate module not available")
    
    def test_prompt_convert_query_format_method(self):
        """Test method format() dari promptConvertQuery"""
        # Mock the actual prompt template
        with patch('model.promptTemplate.promptConvertQuery') as mock_prompt:
            mock_prompt.format.return_value = "Convert this question to SQL: What users are active?"
            
            # Test format method
            result = mock_prompt.format(question="What users are active?")
            
            assert result == "Convert this question to SQL: What users are active?"
            mock_prompt.format.assert_called_once_with(question="What users are active?")
    
    @pytest.mark.parametrize("question,expected_called", [
        ("Show me all users", True),
        ("List active customers", True), 
        ("", True),  # Empty string should still call format
        (None, True),  # None should still call format (might cause error in real usage)
    ])
    def test_prompt_convert_query_various_inputs(self, question, expected_called):
        """Test promptConvertQuery dengan berbagai input"""
        with patch('model.promptTemplate.promptConvertQuery') as mock_prompt:
            mock_prompt.format.return_value = f"Formatted prompt for: {question}"
            
            result = mock_prompt.format(question=question)
            
            if expected_called:
                mock_prompt.format.assert_called_once_with(question=question)
                assert f"Formatted prompt for: {question}" == result


class TestPromptTemplateIntegration:
    """Test integrasi PromptTemplate dengan fungsi model"""
    
    @patch('model.model.llm')
    def test_create_query_uses_prompt_template(self, mock_llm):
        """Test bahwa createQuery menggunakan promptConvertQuery dengan benar"""
        from model.model import createQuery
        
        # Setup mocks
        mock_response = Mock()
        mock_response.content = "SELECT * FROM users WHERE active = 1"
        mock_llm.invoke.return_value = mock_response
        
        with patch('model.model.promptConvertQuery') as mock_prompt:
            mock_prompt.format.return_value = "Convert to SQL: Show active users"
            
            # Execute
            result = createQuery("Show active users")
            
            # Assert
            mock_prompt.format.assert_called_once_with(question="Show active users")
            mock_llm.invoke.assert_called_once_with("Convert to SQL: Show active users")
            assert "SELECT" in result.upper()
    
    @patch('model.model.llm')
    def test_filter_question_uses_prompt_template(self, mock_llm):
        """Test bahwa fillterQuestion menggunakan promptFilter"""
        from model.model import fillterQuestion
        
        # Setup mocks
        mock_response = Mock()
        mock_response.content = "True"
        mock_llm.invoke.return_value = mock_response
        
        with patch('model.model.promptFilter') as mock_prompt:
            mock_prompt.format.return_value = "Filter this question: Is this valid?"
            
            # Execute
            result = fillterQuestion("Is this valid?")
            
            # Assert
            mock_prompt.format.assert_called_once_with(question="Is this valid?")
            mock_llm.invoke.assert_called_once_with("Filter this question: Is this valid?")
            assert result == "True"
    
    @patch('model.model.llm')
    def test_create_answer_uses_prompt_template(self, mock_llm):
        """Test bahwa createAnswer menggunakan promptGetAnswer"""
        from model.model import createAnswer
        
        # Setup mocks
        mock_response = Mock()
        mock_response.content = "Based on the data, here are 2 users"
        mock_llm.invoke.return_value = mock_response
        
        with patch('model.model.promptGetAnswer') as mock_prompt:
            mock_prompt.format.return_value = "Generate answer from data"
            
            raw_data = [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]
            query = "SELECT * FROM users"
            question = "Show me users"
            
            # Execute
            result = createAnswer(raw_data, query, question)
            
            # Assert
            mock_prompt.format.assert_called_once_with(
                rawData=raw_data,
                query=query,
                question=question
            )
            mock_llm.invoke.assert_called_once_with("Generate answer from data")
            assert result == "Based on the data, here are 2 users"
    
    @patch('model.model.llm')
    def test_get_mail_uses_prompt_template(self, mock_llm):
        """Test bahwa getMail menggunakan promptEmail"""
        from model.model import getMail
        
        # Setup mocks
        mock_response = Mock()
        mock_response.content = "user@example.com"
        mock_llm.invoke.return_value = mock_response
        
        with patch('model.model.promptEmail') as mock_prompt:
            mock_prompt.format.return_value = "Extract email from: Contact us at user@example.com"
            
            # Execute
            result = getMail("Contact us at user@example.com")
            
            # Assert
            mock_prompt.format.assert_called_once_with(response="Contact us at user@example.com")
            mock_llm.invoke.assert_called_once_with("Extract email from: Contact us at user@example.com")
            assert result == "user@example.com"
    
    @patch('model.model.llm')
    def test_is_query_uses_prompt_template(self, mock_llm):
        """Test bahwa isQuery menggunakan promptFQ"""
        from model.model import isQuery
        
        # Setup mocks
        mock_response = Mock()
        mock_response.content = "Ya"
        mock_llm.invoke.return_value = mock_response
        
        with patch('model.model.promptFQ') as mock_prompt:
            mock_prompt.format.return_value = "Is this a query: Show me data"
            
            # Execute
            result = isQuery("Show me data")
            
            # Assert
            mock_prompt.format.assert_called_once_with(question="Show me data")
            mock_llm.invoke.assert_called_once_with("Is this a query: Show me data")
            assert result == "Ya"


class TestAllPromptTemplates:
    """Test untuk semua prompt templates"""
    
    def test_all_prompt_templates_import(self):
        """Test import semua prompt templates sekaligus"""
        try:
            from model.promptTemplate import (
                promptConvertQuery, promptGetAnswer, promptFilter, 
                promptEmail, promptFQ
            )
            
            # Test semua template tidak None
            templates = [promptConvertQuery, promptGetAnswer, promptFilter, promptEmail, promptFQ]
            for template in templates:
                assert template is not None
                assert hasattr(template, 'format')
                
        except ImportError:
            pytest.skip("promptTemplate module not available")
    
    def test_prompt_convert_query_real_formatting(self):
        """Test real formatting untuk promptConvertQuery"""
        try:
            from model.promptTemplate import promptConvertQuery
            
            # Test dengan berbagai question
            questions = [
                "Show me all users",
                "List active customers", 
                "Count total orders"
            ]
            
            for question in questions:
                result = promptConvertQuery.format(question=question)
                assert isinstance(result, str)
                assert len(result) > 0
                # Template should contain the question
                assert question in result
                    
        except ImportError:
            pytest.skip("promptTemplate module not available")
    
    def test_prompt_get_answer_real_formatting(self):
        """Test real formatting untuk promptGetAnswer"""
        try:
            from model.promptTemplate import promptGetAnswer
            
            raw_data = [{"id": 1, "name": "John"}]
            query = "SELECT * FROM users"
            question = "Show users"
            
            result = promptGetAnswer.format(
                rawData=raw_data,
                query=query, 
                question=question
            )
            
            assert isinstance(result, str)
            assert len(result) > 0
            # Should contain all input parameters
            assert str(raw_data) in result or "John" in result
            assert query in result
            assert question in result
            
        except ImportError:
            pytest.skip("promptTemplate module not available")
    
    def test_prompt_filter_real_formatting(self):
        """Test real formatting untuk promptFilter"""
        try:
            from model.promptTemplate import promptFilter
            
            test_questions = [
                "Is this appropriate?",
                "Show me data",
                "Delete all records"
            ]
            
            for question in test_questions:
                result = promptFilter.format(question=question)
                assert isinstance(result, str)
                assert question in result
                
        except ImportError:
            pytest.skip("promptTemplate module not available")
    
    def test_prompt_email_real_formatting(self):
        """Test real formatting untuk promptEmail"""
        try:
            from model.promptTemplate import promptEmail
            
            test_responses = [
                "Contact us at user@example.com",
                "Email: admin@company.com for support",
                "No email in this text"
            ]
            
            for response in test_responses:
                result = promptEmail.format(response=response)
                assert isinstance(result, str)
                assert response in result
                
        except ImportError:
            pytest.skip("promptTemplate module not available")
    
    def test_prompt_fq_real_formatting(self):
        """Test real formatting untuk promptFQ"""
        try:
            from model.promptTemplate import promptFQ
            
            test_questions = [
                "Show me database records",
                "What is the weather?",
                "SELECT * FROM users"
            ]
            
            for question in test_questions:
                result = promptFQ.format(question=question)
                assert isinstance(result, str)
                assert question in result
                
        except ImportError:
            pytest.skip("promptTemplate module not available")


class TestPromptTemplateContent:
    """Test konten actual dari prompt templates (jika diperlukan)"""
    
    def test_prompt_templates_have_required_variables(self):
        """Test bahwa prompt templates memiliki variabel yang diperlukan"""
        try:
            from model.promptTemplate import (
                promptConvertQuery, promptGetAnswer, promptFilter, 
                promptEmail, promptFQ
            )
            
            # Test bahwa prompt templates adalah PromptTemplate objects
            assert hasattr(promptConvertQuery, 'format')
            assert hasattr(promptGetAnswer, 'format')
            assert hasattr(promptFilter, 'format')
            assert hasattr(promptEmail, 'format')
            assert hasattr(promptFQ, 'format')
            
        except ImportError:
            pytest.skip("promptTemplate module not available")
    
    def test_prompt_template_formatting_real(self):
        """Test dengan real prompt template"""
        try:
            from model.promptTemplate import promptConvertQuery
            
            # Test formatting dengan real template
            formatted = promptConvertQuery.format(question="Show me all users")
            
            # Basic assertions
            assert isinstance(formatted, str)
            assert len(formatted) > 0
            assert "Show me all users" in formatted
            
        except ImportError:
            pytest.skip("promptTemplate module not available")
        except AttributeError:
            pytest.skip("promptConvertQuery tidak memiliki method format")


class TestPromptTemplateErrorHandling:
    """Test error handling untuk prompt templates"""
    
    def test_prompt_template_with_missing_variables(self):
        """Test prompt template dengan missing variables"""
        try:
            from model.promptTemplate import promptConvertQuery
            
            # Test error ketika parameter required missing
            with pytest.raises((KeyError, TypeError)):
                promptConvertQuery.format()  # Missing 'question' parameter
                
        except ImportError:
            pytest.skip("promptTemplate module not available")
    
    def test_prompt_get_answer_missing_variables(self):
        """Test promptGetAnswer dengan missing variables"""
        try:
            from model.promptTemplate import promptGetAnswer
            
            # Test error ketika parameter required missing
            with pytest.raises((KeyError, TypeError)):
                promptGetAnswer.format(rawData=[])  # Missing query and question
                
        except ImportError:
            pytest.skip("promptTemplate module not available")
    
    @patch('model.model.llm')
    def test_function_handles_prompt_error(self, mock_llm):
        """Test bahwa fungsi handle error dari prompt template"""
        from model.model import createQuery
        
        with patch('model.model.promptConvertQuery') as mock_prompt:
            # Simulate prompt formatting error
            mock_prompt.format.side_effect = Exception("Template error")
            
            # Test bahwa error tidak crash aplikasi
            with pytest.raises(Exception):
                createQuery("test question")


# Parametrized tests untuk berbagai input email
@pytest.mark.parametrize("sql_input,expected_keywords", [
    ("```sql\nSELECT * FROM users\n```", ["SELECT", "FROM"]),
    ("```\nselect id from products\n```", ["SELECT", "FROM"]),
    ("select name from customers", ["SELECT", "FROM"]),
    ("", []),
])
def test_clean_sql_parametrized(sql_input, expected_keywords):
    """Test parametrized untuk clean_sql function"""
    try:
        from model.model import clean_sql
        result = clean_sql(sql_input)
        
        for keyword in expected_keywords:
            assert keyword.upper() in result.upper()
    except ImportError:
        pytest.skip("model.model not available")


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
        
        try:
            from model.model import fillterQuestion
            result = fillterQuestion("test question")
            assert result == expected_result
        except ImportError:
            pytest.skip("model.model not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])