import pytest
from unittest.mock import patch, MagicMock
import sys
import requests

from src.main import main

@pytest.fixture
def mock_requests_get():
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.text = '<rss><channel><item><title>Test Article</title><description>Test Description</description><link>http://example.com</link></item></channel></rss>'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        yield mock_get

@pytest.fixture
def mock_process_user_feed():
    with patch('src.main.process_user_feed') as mock:
        mock.return_value = [
            {'title': 'Test Article', 'summary': 'Test Summary', 'url': 'http://example.com'}
        ]
        yield mock

@pytest.fixture
def mock_filter_feed():
    with patch('src.main.filter_feed') as mock:
        mock.return_value = [
            {'title': 'Filtered Article', 'summary': 'Filtered Summary', 'url': 'http://example.com/filtered'}
        ]
        yield mock

@pytest.fixture
def mock_translate_feed():
    with patch('src.main.translate_feed') as mock:
        mock.return_value = [
            {'title': 'Translated Article', 'summary': 'Translated Summary', 'url': 'http://example.com/translated'}
        ]
        yield mock

@pytest.fixture
def mock_apply_slang():
    with patch('src.main.apply_slang') as mock:
        mock.return_value = [
            {'title': 'Slang Article', 'summary': 'Slang Summary', 'url': 'http://example.com/slang'}
        ]
        yield mock


# edge case tests focusing on user input like empty input, special characters and even regular expresstion,etc.

def test_filter_empty_input(mock_requests_get, mock_process_user_feed, mock_filter_feed, capsys):
    sys.argv = ['main.py', 'http://example.com/rss']
    with patch('builtins.input', side_effect=['filter', '', 'exit']):
        main()
    
    captured = capsys.readouterr()
    assert "Enter a keyword to filter the feed: " in captured.out
    assert "Invalid keyword. Please try again." in captured.out

def test_filter_special_characters(mock_requests_get, mock_process_user_feed, mock_filter_feed, capsys):
    sys.argv = ['main.py', 'http://example.com/rss']
    with patch('builtins.input', side_effect=['filter', '!@#$%^&*', 'exit']):
        main()
    
    captured = capsys.readouterr()
    assert "Enter a keyword to filter the feed: " in captured.out
    # Ensure the special characters are handled properly

def test_filter_regex(mock_requests_get, mock_process_user_feed, mock_filter_feed, capsys):
    sys.argv = ['main.py', 'http://example.com/rss']
    with patch('builtins.input', side_effect=['filter', '[a-z]+', 'exit']):
        main()
    
    captured = capsys.readouterr()
    assert "Enter a keyword to filter the feed: " in captured.out
    # Ensure regex patterns are handled properly (either treated as literal strings or as regex)

def test_translate_empty_input(mock_requests_get, mock_process_user_feed, mock_translate_feed, capsys):
    sys.argv = ['main.py', 'http://example.com/rss']
    with patch('builtins.input', side_effect=['translate', '', 'exit']):
        main()
    
    captured = capsys.readouterr()
    assert "Enter the target language: " in captured.out
    assert "Invalid language. Please try again." in captured.out

def test_translate_numeric_input(mock_requests_get, mock_process_user_feed, mock_translate_feed, capsys):
    sys.argv = ['main.py', 'http://example.com/rss']
    with patch('builtins.input', side_effect=['translate', '123', 'exit']):
        main()
    
    captured = capsys.readouterr()
    assert "Enter the target language: " in captured.out
    assert "Invalid language. Please try again." in captured.out

def test_translate_long_input(mock_requests_get, mock_process_user_feed, mock_translate_feed, capsys):
    sys.argv = ['main.py', 'http://example.com/rss']
    with patch('builtins.input', side_effect=['translate', 'a'*100, 'exit']):
        main()
    
    captured = capsys.readouterr()
    assert "Enter the target language: " in captured.out
    assert "Invalid language. Please try again." in captured.out

def test_slang_empty_input(mock_requests_get, mock_process_user_feed, mock_apply_slang, capsys):
    sys.argv = ['main.py', 'http://example.com/rss']
    with patch('builtins.input', side_effect=['slang', '', 'exit']):
        main()
    
    captured = capsys.readouterr()
    assert "Enter the slang style (e.g., cyberpunk, southern belle): " in captured.out
    assert "Invalid slang style. Please try again." in captured.out

def test_slang_numeric_input(mock_requests_get, mock_process_user_feed, mock_apply_slang, capsys):
    sys.argv = ['main.py', 'http://example.com/rss']
    with patch('builtins.input', side_effect=['slang', '123', 'exit']):
        main()
    
    captured = capsys.readouterr()
    assert "Enter the slang style (e.g., cyberpunk, southern belle): " in captured.out
    # Ensure numeric input is handled properly (either rejected or treated as a valid style)

def test_slang_special_characters(mock_requests_get, mock_process_user_feed, mock_apply_slang, capsys):
    sys.argv = ['main.py', 'http://example.com/rss']
    with patch('builtins.input', side_effect=['slang', '!@#$%^&*', 'exit']):
        main()
    
    captured = capsys.readouterr()
    assert "Enter the slang style (e.g., cyberpunk, southern belle): " in captured.out
    assert "Invalid slang style. Please try again." in captured.out

def test_multiple_empty_inputs(mock_requests_get, mock_process_user_feed, capsys):
    sys.argv = ['main.py', 'http://example.com/rss']
    with patch('builtins.input', side_effect=['', '', '', 'exit']):
        main()
    
    captured = capsys.readouterr()
    assert "Invalid action. Please try again." in captured.out

def test_case_insensitive_actions(mock_requests_get, mock_process_user_feed, mock_filter_feed, capsys):
    sys.argv = ['main.py', 'http://example.com/rss']
    with patch('builtins.input', side_effect=['FILTER', 'keyword', 'Exit']):
        main()
    
    captured = capsys.readouterr()
    assert "Enter a keyword to filter the feed: " in captured.out

def test_whitespace_in_input(mock_requests_get, mock_process_user_feed, mock_filter_feed, capsys):
    sys.argv = ['main.py', 'http://example.com/rss']
    with patch('builtins.input', side_effect=['filter', '  keyword  ', 'exit']):
        main()
    
    captured = capsys.readouterr()
    assert "Enter a keyword to filter the feed: " in captured.out
    # Ensure leading/trailing whitespace is handled properly

