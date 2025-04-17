"""Tests for the EIP Manager."""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from ergo_explorer.eip_manager.eip_manager import EIPManager, EIPDetail, EIPSummary


@pytest.fixture
def mock_git():
    """Mock the git module."""
    with patch("ergo_explorer.eip_manager.eip_manager.git") as mock_git:
        # Mock the repo
        mock_repo = MagicMock()
        mock_git.Repo.return_value = mock_repo
        mock_git.Repo.clone_from.return_value = mock_repo
        
        # Mock the remote
        mock_remote = MagicMock()
        mock_repo.remotes.origin = mock_remote
        
        yield mock_git


@pytest.fixture
def mock_eip_file():
    """Create a mock EIP file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        eip_content = """# Test EIP Title
        
| Status | Draft |

## Abstract

This is a test EIP.

## Motivation

Testing the EIP manager.
"""
        eip_path = os.path.join(temp_dir, "eip-123.md")
        with open(eip_path, "w") as f:
            f.write(eip_content)
        
        yield temp_dir, eip_path


def test_eip_manager_init():
    """Test EIPManager initialization."""
    manager = EIPManager()
    assert manager.repo_url == EIPManager.EIP_REPO_URL
    assert "ergo_eips" in manager.local_dir
    assert manager.eip_cache == {}
    assert manager.repo is None


@patch("ergo_explorer.eip_manager.eip_manager.os.path.exists")
def test_fetch_repo_clone(mock_exists, mock_git):
    """Test fetching the EIP repository when it doesn't exist locally."""
    mock_exists.return_value = False
    
    manager = EIPManager()
    manager._fetch_repo()
    
    mock_git.Repo.clone_from.assert_called_once_with(manager.repo_url, manager.local_dir)


@patch("ergo_explorer.eip_manager.eip_manager.os.path.exists")
def test_fetch_repo_pull(mock_exists, mock_git):
    """Test fetching the EIP repository when it exists locally."""
    mock_exists.return_value = True
    
    manager = EIPManager()
    manager._fetch_repo()
    
    mock_git.Repo.assert_called_once_with(manager.local_dir)
    mock_git.Repo.return_value.remotes.origin.pull.assert_called_once()


def test_parse_eip_file(mock_eip_file):
    """Test parsing an EIP file."""
    temp_dir, eip_path = mock_eip_file
    
    manager = EIPManager()
    title, status, content = manager._parse_eip_file(eip_path)
    
    assert title == "Test EIP Title"
    assert status == "Draft"
    assert "This is a test EIP" in content


@patch("ergo_explorer.eip_manager.eip_manager.os.walk")
def test_parse_eips(mock_walk, mock_eip_file):
    """Test parsing EIPs."""
    temp_dir, eip_path = mock_eip_file
    mock_walk.return_value = [(temp_dir, [], ["eip-123.md"])]
    
    manager = EIPManager()
    manager.local_dir = temp_dir
    manager._parse_eips()
    
    assert 123 in manager.eip_cache
    assert manager.eip_cache[123].title == "Test EIP Title"
    assert manager.eip_cache[123].status == "Draft"


def test_get_all_eips():
    """Test getting all EIPs."""
    manager = EIPManager()
    manager.eip_cache = {
        1: EIPDetail(number=1, title="EIP 1", status="Final", content="Content 1"),
        2: EIPDetail(number=2, title="EIP 2", status="Draft", content="Content 2"),
    }
    
    eips = manager.get_all_eips()
    
    assert len(eips) == 2
    assert eips[0].number == 1
    assert eips[0].title == "EIP 1"
    assert eips[0].status == "Final"
    assert eips[1].number == 2
    assert eips[1].title == "EIP 2"
    assert eips[1].status == "Draft"


def test_get_eip_details():
    """Test getting EIP details."""
    manager = EIPManager()
    manager.eip_cache = {
        1: EIPDetail(number=1, title="EIP 1", status="Final", content="Content 1"),
    }
    
    eip = manager.get_eip_details(1)
    
    assert eip is not None
    assert eip.number == 1
    assert eip.title == "EIP 1"
    assert eip.status == "Final"
    assert eip.content == "Content 1"
    
    # Test getting a non-existent EIP
    eip = manager.get_eip_details(999)
    assert eip is None 