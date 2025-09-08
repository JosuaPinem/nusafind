import pytest
from validation.validation import check_input


class TestCheckInput:
    """Test cases untuk fungsi check_input"""
    
    def test_check_input_with_none(self):
        """Test dengan body None"""
        result = check_input(None)
        assert result is None
    
    def test_check_input_with_empty_dict(self):
        """Test dengan dictionary kosong"""
        result = check_input({})
        assert result is None
    
    def test_check_input_with_empty_string(self):
        """Test dengan string kosong"""
        result = check_input("")
        assert result is None
    
    def test_check_input_with_empty_list(self):
        """Test dengan list kosong"""
        result = check_input([])
        assert result is None
    
    def test_check_input_without_question_key(self):
        """Test dengan body yang tidak memiliki key 'question'"""
        body = {"answer": "test", "user": "john"}
        result = check_input(body)
        assert result is None
    
    def test_check_input_with_question_key(self):
        """Test dengan body yang memiliki key 'question' (valid case)"""
        body = {"question": "What is Python?"}
        result = check_input(body)
        assert result == body
    
    def test_check_input_with_question_and_other_keys(self):
        """Test dengan body yang memiliki 'question' dan key lainnya"""
        body = {
            "question": "How to use Flask?",
            "user_id": 123,
            "timestamp": "2025-01-01"
        }
        result = check_input(body)
        assert result == body
    
    def test_check_input_with_question_empty_value(self):
        """Test dengan key 'question' tapi value kosong"""
        body = {"question": ""}
        result = check_input(body)
        assert result == body  # fungsi hanya cek keberadaan key, bukan value
    
    def test_check_input_with_question_none_value(self):
        """Test dengan key 'question' tapi value None"""
        body = {"question": None}
        result = check_input(body)
        assert result == body  # fungsi hanya cek keberadaan key, bukan value
    
    def test_check_input_with_question_as_list(self):
        """Test dengan 'question' sebagai list"""
        body = {"question": ["What is AI?", "What is ML?"]}
        result = check_input(body)
        assert result == body
    
    def test_check_input_with_question_as_number(self):
        """Test dengan 'question' sebagai number"""
        body = {"question": 123}
        result = check_input(body)
        assert result == body


# Test tambahan untuk edge cases
class TestCheckInputEdgeCases:
    """Test edge cases untuk check_input"""
    
    def test_check_input_with_false_value(self):
        """Test dengan value falsy tapi bukan None/empty"""
        result = check_input(False)
        assert result is None
    
    def test_check_input_with_zero(self):
        """Test dengan angka 0"""
        result = check_input(0)
        assert result is None
    
    def test_check_input_case_sensitive(self):
        """Test case sensitivity untuk key 'question'"""
        body_upper = {"QUESTION": "test"}
        body_title = {"Question": "test"}
        
        assert check_input(body_upper) is None
        assert check_input(body_title) is None
    
    def test_check_input_with_nested_question(self):
        """Test dengan nested object yang memiliki 'question'"""
        body = {
            "data": {"question": "nested question"},
            "question": "main question"
        }
        result = check_input(body)
        assert result == body


# Parametrized tests untuk input yang tidak valid
@pytest.mark.parametrize("invalid_input", [
    None,
    "",
    [],
    {},
    False,
    0,
    {"answer": "no question"},
    {"QUESTION": "wrong case"},
    {"quest": "not question"}
])
def test_check_input_invalid_inputs(invalid_input):
    """Test parametrized untuk berbagai input tidak valid"""
    result = check_input(invalid_input)
    assert result is None


# Parametrized tests untuk input yang valid
@pytest.mark.parametrize("valid_input", [
    {"question": "test"},
    {"question": ""},
    {"question": None},
    {"question": 123},
    {"question": "What is Flask?", "user": "john"},
    {"question": ["multiple", "questions"]},
    {"other_key": "value", "question": "main question"}
])
def test_check_input_valid_inputs(valid_input):
    """Test parametrized untuk berbagai input valid"""
    result = check_input(valid_input)
    assert result == valid_input


if __name__ == "__main__":
    pytest.main([__file__, "-v"])