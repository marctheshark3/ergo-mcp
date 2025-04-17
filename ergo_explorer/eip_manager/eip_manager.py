"""
Ergo Improvement Proposals (EIPs) manager.
"""

import logging
import os
import re
import shutil
import tempfile
import threading
import time
from typing import Dict, List, Optional, Tuple, Union

import git
import markdown
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class EIPSummary(BaseModel):
    """Basic information about an EIP."""
    number: int
    title: str
    status: str = "Unknown"


class EIPDetail(EIPSummary):
    """Detailed information about an EIP."""
    content: str


class EIPManager:
    """
    Manager for Ergo Improvement Proposals (EIPs).
    
    This class is responsible for fetching, parsing, and providing information
    about Ergo Improvement Proposals (EIPs) from the official GitHub repository.
    """
    
    EIP_REPO_URL = "https://github.com/ergoplatform/eips.git"
    EIP_FILE_PATTERN = r"eip-(\d+)\.md"
    
    def __init__(self, repo_url: str = EIP_REPO_URL, local_dir: Optional[str] = None,
                 update_interval_hours: float = 24.0):
        """
        Initialize the EIP manager.
        
        Args:
            repo_url: The URL of the EIP repository.
            local_dir: The local directory to clone the repository into.
                       If None, a temporary directory will be used.
            update_interval_hours: How often to update the EIPs, in hours.
        """
        self.repo_url = repo_url
        self.local_dir = local_dir or os.path.join(tempfile.gettempdir(), "ergo_eips")
        self.update_interval_hours = update_interval_hours
        self.eip_cache: Dict[int, EIPDetail] = {}
        self.repo = None
        self._update_thread = None
        self._stop_event = threading.Event()
    
    def _fetch_repo(self) -> None:
        """
        Fetch or update the EIP repository.
        
        If the repository doesn't exist locally, it will be cloned.
        If it already exists, it will be updated with a pull.
        """
        try:
            if not os.path.exists(self.local_dir):
                logger.info(f"Cloning EIP repository from {self.repo_url} to {self.local_dir}")
                self.repo = git.Repo.clone_from(self.repo_url, self.local_dir)
            else:
                logger.info(f"Using existing EIP repository at {self.local_dir}")
                self.repo = git.Repo(self.local_dir)
                logger.info("Pulling latest changes from remote repository")
                self.repo.remotes.origin.pull()
            logger.info("Successfully fetched EIP repository")
        except git.GitCommandError as e:
            logger.error(f"Failed to fetch EIP repository: {e}")
            # If the repo is in a bad state, remove it and try again
            if os.path.exists(self.local_dir):
                shutil.rmtree(self.local_dir, ignore_errors=True)
                logger.info(f"Removed corrupted repository at {self.local_dir}")
                logger.info(f"Recloning EIP repository from {self.repo_url}")
                self.repo = git.Repo.clone_from(self.repo_url, self.local_dir)
    
    def _parse_eip_file(self, file_path: str) -> Tuple[str, str, str]:
        """
        Parse an EIP file to extract its title and content.
        
        Args:
            file_path: The path to the EIP file.
            
        Returns:
            A tuple containing the title, status, and content of the EIP.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract the title from the first # heading
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else "Unknown Title"
            
            # Extract the status if available
            status_match = re.search(r'^\|\s*Status\s*\|\s*(.+?)\s*\|', content, re.MULTILINE)
            status = status_match.group(1) if status_match else "Unknown"
            
            # Convert Markdown to HTML for better presentation
            html_content = markdown.markdown(content)
            
            return title, status, html_content
        except Exception as e:
            logger.error(f"Failed to parse EIP file {file_path}: {e}")
            return "Unknown Title", "Unknown", f"Error parsing EIP: {str(e)}"
    
    def _parse_eips(self) -> None:
        """
        Parse all EIP files in the repository.
        """
        try:
            for root, _, files in os.walk(self.local_dir):
                for file in files:
                    match = re.match(self.EIP_FILE_PATTERN, file)
                    if match:
                        eip_number = int(match.group(1))
                        file_path = os.path.join(root, file)
                        
                        title, status, content = self._parse_eip_file(file_path)
                        
                        self.eip_cache[eip_number] = EIPDetail(
                            number=eip_number,
                            title=title,
                            status=status,
                            content=content
                        )
                        logger.debug(f"Parsed EIP-{eip_number}: {title}")
        except Exception as e:
            logger.error(f"Failed to parse EIPs: {e}")
    
    def _update_cache(self) -> None:
        """
        Update the EIP cache by fetching and parsing the EIPs.
        """
        self._fetch_repo()
        self._parse_eips()
        logger.info(f"Updated EIP cache with {len(self.eip_cache)} EIPs")
    
    def _update_loop(self) -> None:
        """
        Background loop to periodically update the EIPs.
        """
        while not self._stop_event.is_set():
            try:
                self._update_cache()
                # Sleep for the specified interval, but check the stop event
                # every 60 seconds to allow for clean shutdown
                for _ in range(int(self.update_interval_hours * 60)):
                    if self._stop_event.is_set():
                        break
                    time.sleep(60)
            except Exception as e:
                logger.error(f"Error in EIP update loop: {e}")
                # Still sleep before retrying
                time.sleep(60)
    
    def load_or_update_eips(self) -> None:
        """
        Load or update the EIPs.
        
        This should be called when the server starts.
        """
        self._update_cache()
        
        # Start background thread for periodic updates
        if self._update_thread is None or not self._update_thread.is_alive():
            self._stop_event.clear()
            self._update_thread = threading.Thread(
                target=self._update_loop,
                daemon=True
            )
            self._update_thread.start()
            logger.info(f"Started background EIP update thread (interval: {self.update_interval_hours} hours)")
    
    def stop(self) -> None:
        """
        Stop the background update thread.
        
        This should be called when the server is shutting down.
        """
        if self._update_thread and self._update_thread.is_alive():
            logger.info("Stopping EIP update thread")
            self._stop_event.set()
            self._update_thread.join(timeout=5.0)
            logger.info("EIP update thread stopped")
    
    def get_all_eips(self) -> List[EIPSummary]:
        """
        Get a list of all EIPs.
        
        Returns:
            A list of EIPSummary objects.
        """
        return [
            EIPSummary(number=eip.number, title=eip.title, status=eip.status)
            for eip in self.eip_cache.values()
        ]
    
    def get_eip_details(self, eip_number: int) -> Optional[EIPDetail]:
        """
        Get detailed information about a specific EIP.
        
        Args:
            eip_number: The EIP number.
            
        Returns:
            An EIPDetail object if the EIP exists, None otherwise.
        """
        return self.eip_cache.get(eip_number) 