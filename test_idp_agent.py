import sys
import os
import json
import pytest
from unittest.mock import patch
import idp_agent

def test_missing_args(capsys):
    with patch.object(sys, 'argv', ['idp_agent.py']):
        with pytest.raises(SystemExit):
            idp_agent.main()
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["error"] == "INVALID_ARGUMENTS"

def test_missing_file(capsys):
    with patch.object(sys, 'argv', ['idp_agent.py', 'nonexistent_file.pdf']):
        with pytest.raises(SystemExit):
            idp_agent.main()
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["error"] == "UNREADABLE_DOCUMENT"
    assert "File not found" in data["message"]

def test_empty_file(capsys):
    filepath = os.path.join("test_inputs", "empty.bin")
    if not os.path.exists("test_inputs"):
        os.makedirs("test_inputs")
    with open(filepath, "wb"):
        pass  # Ensure it is exactly 0 bytes
        
    with patch.object(sys, 'argv', ['idp_agent.py', filepath]):
        with pytest.raises(SystemExit):
            idp_agent.main()
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["error"] == "UNREADABLE_DOCUMENT"
    assert "could not be processed" in data["message"]
