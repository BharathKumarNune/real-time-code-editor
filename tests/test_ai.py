import pytest
from app.ai import ai_debug

def test_ai_debug():
    code = "print('Hello World')"
    response = ai_debug(code)
    assert isinstance(response, str)
