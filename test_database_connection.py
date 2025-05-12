
import pytest
import psycopg2
from database_connection import GetWord, AddWord

def test_GetWord():
    # Test getting an existing word
    test_word = "TESTWORD"
    
    # First add the test word
    AddWord(test_word)
    
    # Test retrieving the word
    result = GetWord(test_word)
    assert result is not None
    assert len(result) == 1
    assert result[0][1] == test_word
    
    # Test getting a non-existent word
    non_existent = GetWord("NONEXISTENTWORD")
    assert len(non_existent) == 0
