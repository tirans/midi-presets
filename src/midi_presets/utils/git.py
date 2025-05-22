import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
import time

from .logging import get_logger

class GitUtils:
    def __init__(self, repo_path: Optional[Path] = None):
        self.repo_path = repo_path or Path.cwd()
        self.logger = get_logger('utils.git')
        
        self.logger.debug(
            f"GitUtils initialized",
            extra={'repo_path': str(self.repo_path)}
        )
        
        # Verify git repository
        if self._is_git_repository():
            self.logger.info("Git repository detected")
        else:
            self.logger.warning("Not in a git repository or git not available")
    
    def _is_git_repository(self) -> bool:
        """Check if current directory is a git repository"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                timeout=5
            )
            is_git_repo = result.returncode == 0
            
            self.logger.debug(
                f"Git repository check: {'found' if is_git_repo else 'not found'}",
                extra={'repo_path': str(self.repo_path)}
            )
            
            return is_git_repo
            
        except Exception as e:
            self.logger.debug(
                f"Error checking git repository: {e}",
                extra={'error': str(e)}
            )
            return False
    
    def get_revision_count(self) -> int:
        """Get current git revision number"""
        start_time = time.time()
        
        self.logger.debug("Getting git revision count")
        
        try:
            result = subprocess.run(
                ['git', 'rev-list', '--count', 'HEAD'],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                timeout=10
            )
            
            duration = (time.time() - start_time) * 1000
            
            if result.returncode == 0:
                revision_count = int(result.stdout.strip())
                self.logger.info(
                    f"Git revision count: {revision_count}",
                    extra={
                        'revision_count': revision_count,
                        'duration_ms': duration
                    }
                )
                return revision_count
            else:
                self.logger.warning(
                    f"Git rev-list failed: {result.stderr}",
                    extra={
                        'return_code': result.returncode,
                        'stderr': result.stderr,
                        'duration_ms': duration
                    }
                )
                return 0
                
        except subprocess.TimeoutExpired:
            self.logger.warning("Git revision count command timed out")
            return 0
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self.logger.error(
                f"Error getting git revision count: {e}",
                extra={
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'duration_ms': duration
                }
            )
            return 0
    
    def get_current_hash(self) -> str:
        """Get current commit hash"""
        start_time = time.time()
        
        self.logger.debug("Getting current git hash")
        
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                timeout=10
            )
            
            duration = (time.time() - start_time) * 1000
            
            if result.returncode == 0:
                commit_hash = result.stdout.strip()
                self.logger.info(
                    f"Current git hash: {commit_hash[:16]}...",
                    extra={
                        'commit_hash': commit_hash,
                        'short_hash': commit_hash[:8],
                        'duration_ms': duration
                    }
                )
                return commit_hash
            else:
                self.logger.warning(
                    f"Git rev-parse failed: {result.stderr}",
                    extra={
                        'return_code': result.returncode,
                        'stderr': result.stderr,
                        'duration_ms': duration
                    }
                )
                return ""
                
        except subprocess.TimeoutExpired:
            self.logger.warning("Git hash command timed out")
            return ""
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self.logger.error(
                f"Error getting git hash: {e}",
                extra={
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'duration_ms': duration
                }
            )
            return ""
    
    def get_repository_info(self) -> Dict[str, Any]:
        """Get comprehensive repository information"""
        self.logger.info("Gathering repository information")
        
        info = {
            'revision_count': self.get_revision_count(),
            'current_hash': self.get_current_hash(),
            'branch_name': self._get_current_branch(),
            'remote_url': self._get_remote_url(),
            'has_uncommitted_changes': self._has_uncommitted_changes(),
            'last_commit_date': self._get_last_commit_date()
        }
        
        self.logger.info(
            f"Repository info gathered",
            extra={
                'info': {k: v for k, v in info.items() if k != 'current_hash'},  # Don't log full hash
                'current_hash_short': info['current_hash'][:8] if info['current_hash'] else None
            }
        )
        
        return info
    
    def _get_current_branch(self) -> str:
        """Get current branch name"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                timeout=5
            )
            
            if result.returncode == 0:
                branch = result.stdout.strip()
                self.logger.debug(f"Current branch: {branch}")
                return branch
            else:
                self.logger.debug("Could not determine current branch")
                return "unknown"
                
        except Exception as e:
            self.logger.debug(f"Error getting current branch: {e}")
            return "unknown"
    
    def _get_remote_url(self) -> str:
        """Get remote origin URL"""
        try:
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                timeout=5
            )
            
            if result.returncode == 0:
                url = result.stdout.strip()
                self.logger.debug(f"Remote URL: {url}")
                return url
            else:
                self.logger.debug("No remote origin found")
                return ""
                
        except Exception as e:
            self.logger.debug(f"Error getting remote URL: {e}")
            return ""
    
    def _has_uncommitted_changes(self) -> bool:
        """Check if repository has uncommitted changes"""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                timeout=5
            )
            
            if result.returncode == 0:
                has_changes = bool(result.stdout.strip())
                self.logger.debug(f"Has uncommitted changes: {has_changes}")
                return has_changes
            else:
                self.logger.debug("Could not check for uncommitted changes")
                return False
                
        except Exception as e:
            self.logger.debug(f"Error checking uncommitted changes: {e}")
            return False
    
    def _get_last_commit_date(self) -> str:
        """Get last commit date"""
        try:
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%ci'],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                timeout=5
            )
            
            if result.returncode == 0:
                date = result.stdout.strip()
                self.logger.debug(f"Last commit date: {date}")
                return date
            else:
                self.logger.debug("Could not get last commit date")
                return ""
                
        except Exception as e:
            self.logger.debug(f"Error getting last commit date: {e}")
            return ""
