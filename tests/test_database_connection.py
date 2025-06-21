import pytest
import psycopg2
from data.ban_word_data import GetWord, AddWord

#I don't know how or why this works, but it does.
@pytest.fixture
def mock_db_connection(monkeypatch):
    class MockCursor:
        def __init__(self):
            self.mock_data = {
                'TESTWORD': [(1, 'TESTWORD')],
                'NONEXISTENTWORD': []
            }
        
        def execute(self, query, params=None):
            self.last_params = params
            
        def fetchall(self):
            if self.last_params:
                return self.mock_data.get(self.last_params[0], [])
            return []
            
        def __enter__(self):
            return self
            
        def __exit__(self, *args):
            pass

    class MockConnection:
        def cursor(self):
            return MockCursor()
            
        def commit(self):
            pass
            
        def __enter__(self):
            return self
            
        def __exit__(self, *args):
            pass

    def mock_connect(*args, **kwargs):
        return MockConnection()

    monkeypatch.setattr(psycopg2, "connect", mock_connect)

def test_GetWord(mock_db_connection):
    # Test getting an existing word
    result = GetWord("TESTWORD")
    assert result is not None
    assert len(result) == 1
    assert result[0][1] == "TESTWORD"
    
    # Test getting a non-existent word
    non_existent = GetWord("NONEXISTENTWORD")
    assert len(non_existent) == 0
