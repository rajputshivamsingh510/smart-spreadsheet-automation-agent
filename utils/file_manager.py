"""
File Manager for Agent Workspace
--------------------------------
Centralized file management that creates session-based directories for
each conversation thread, keeping files organized and easy to find.
"""
import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class FileManager:
    """Centralized file management for the agent with session-based organization."""
    
    def __init__(self, base_dir: str = "workspace"):
        """
        Initialize the file manager.
        
        Args:
            base_dir: Root directory for all agent files
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        self.current_session: Optional[Path] = None
        self.current_thread_id: Optional[str] = None
        self.file_registry: Dict[str, Dict[str, Any]] = {}
        logger.info(f"📁 FileManager initialized at: {self.base_dir.absolute()}")
    
    def create_session(self, thread_id: str = "default") -> Path:
        """
        Create a new session directory for a thread.
        
        Args:
            thread_id: Unique identifier for the conversation thread
            
        Returns:
            Path to the created session directory
        """
        # Clean thread_id for filesystem
        safe_thread_id = "".join(c for c in thread_id if c.isalnum() or c in "-_")
        if not safe_thread_id:
            safe_thread_id = "default"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_name = f"{safe_thread_id}_{timestamp}"
        self.current_session = self.base_dir / session_name
        self.current_session.mkdir(parents=True, exist_ok=True)
        self.current_thread_id = thread_id
        
        # Create subdirectories for different file types
        (self.current_session / "csv").mkdir(exist_ok=True)
        (self.current_session / "excel").mkdir(exist_ok=True)
        (self.current_session / "ods").mkdir(exist_ok=True)
        (self.current_session / "logs").mkdir(exist_ok=True)
        
        logger.info(f"📁 Created session: {self.current_session}")
        return self.current_session
    
    def get_session_path(self) -> Path:
        """
        Get current session path, creating one if needed.
        
        Returns:
            Path to the current session directory
        """
        if not self.current_session:
            self.create_session()
        return self.current_session
    
    def get_file_path(self, filename: str, subdir: str = "", create_dirs: bool = True) -> Path:
        """
        Get full path for a file in the current session.
        
        Args:
            filename: Name of the file
            subdir: Subdirectory within session (e.g., "csv", "excel")
            create_dirs: Whether to create directories if they don't exist
            
        Returns:
            Full path to the file
        """
        session = self.get_session_path()
        
        if subdir:
            file_path = session / subdir / filename
        else:
            # Auto-detect subdirectory based on extension
            ext = Path(filename).suffix.lower()
            if ext in ['.csv']:
                file_path = session / "csv" / filename
            elif ext in ['.xlsx', '.xls']:
                file_path = session / "excel" / filename
            elif ext in ['.ods']:
                file_path = session / "ods" / filename
            else:
                file_path = session / filename
        
        if create_dirs:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        
        return file_path
    
    def register_file(self, filepath: str, metadata: Dict[str, Any] = None) -> Path:
        """
        Track a file that was created or modified.
        
        Args:
            filepath: Path to the file (can be string or Path)
            metadata: Additional metadata about the file
            
        Returns:
            Path object for the registered file
        """
        file_path = Path(filepath)
        
        # If it's not absolute, make it relative to session
        if not file_path.is_absolute():
            file_path = self.get_file_path(file_path.name)
        
        # Ensure the file exists
        if not file_path.exists():
            logger.warning(f"⚠️ Registering non-existent file: {file_path}")
        
        self.file_registry[str(file_path)] = {
            "path": str(file_path),
            "filename": file_path.name,
            "session": str(self.current_session) if self.current_session else None,
            "created": datetime.now().isoformat(),
            "size": file_path.stat().st_size if file_path.exists() else 0,
            "metadata": metadata or {}
        }
        logger.info(f"📄 Registered file: {file_path}")
        return file_path
    
    def get_registered_files(self, pattern: str = None) -> List[Dict[str, Any]]:
        """
        Get all registered files, optionally filtered by pattern.
        
        Args:
            pattern: Optional glob pattern to filter files
            
        Returns:
            List of file information dictionaries
        """
        files = list(self.file_registry.values())
        if pattern:
            import fnmatch
            files = [f for f in files if fnmatch.fnmatch(f["filename"], pattern)]
        return files
    
    def list_files(self, pattern: str = "*", recursive: bool = True) -> List[Path]:
        """
        List all files in the current session.
        
        Args:
            pattern: Glob pattern to match files
            recursive: Whether to search recursively
            
        Returns:
            List of file paths
        """
        session = self.get_session_path()
        if recursive:
            return list(session.rglob(pattern))
        else:
            return list(session.glob(pattern))
    
    def get_file_metadata(self, filepath: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a registered file.
        
        Args:
            filepath: Path to the file
            
        Returns:
            Metadata dictionary if found, None otherwise
        """
        return self.file_registry.get(str(filepath))
    
    def cleanup_old_sessions(self, keep_days: int = 7) -> int:
        """
        Clean up session directories older than specified days.
        
        Args:
            keep_days: Number of days to keep sessions
            
        Returns:
            Number of sessions cleaned up
        """
        cutoff = datetime.now().timestamp() - (keep_days * 86400)
        removed_count = 0
        
        for session_dir in self.base_dir.iterdir():
            if session_dir.is_dir():
                # Check if it's a session directory (has timestamp pattern)
                if "_" in session_dir.name:
                    try:
                        # Extract timestamp from session name
                        parts = session_dir.name.split("_")
                        if len(parts) >= 2:
                            timestamp_str = parts[-1]
                            # Check if timestamp is valid
                            if len(timestamp_str) == 15:  # YYYYMMDD_HHMMSS
                                if session_dir.stat().st_mtime < cutoff:
                                    shutil.rmtree(session_dir)
                                    removed_count += 1
                                    logger.info(f"🧹 Removed old session: {session_dir}")
                    except Exception as e:
                        logger.warning(f"⚠️ Error cleaning up {session_dir}: {e}")
        
        return removed_count
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get summary of files in the current session.
        
        Returns:
            Dictionary with session summary information
        """
        if not self.current_session:
            return {
                "active": False,
                "message": "No active session"
            }
        
        files = self.list_files(recursive=True)
        file_types = {}
        total_size = 0
        
        for f in files:
            ext = f.suffix.lower()
            if ext:
                file_types[ext] = file_types.get(ext, 0) + 1
            total_size += f.stat().st_size if f.exists() else 0
        
        return {
            "active": True,
            "session_path": str(self.current_session),
            "thread_id": self.current_thread_id,
            "file_count": len(files),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_types": file_types,
            "registered_files": len(self.file_registry)
        }
    
    def get_file_url(self, filename: str) -> Optional[str]:
        """
        Generate a file URL for download (for frontend integration).
        
        Args:
            filename: Name of the file to get URL for
            
        Returns:
            URL string if file exists, None otherwise
        """
        file_path = self.get_file_path(filename)
        if file_path.exists():
            # For local development, serve from workspace directory
            # In production, this would be a proper file server URL
            return f"/files/{self.current_thread_id}_{datetime.now().strftime('%Y%m%d')}/{file_path.name}"
        return None

    def ensure_session_exists(self, thread_id: str = "default") -> Path:
        """
        Ensure a session exists for the given thread.
        If there's already a session with the same thread_id within the last hour,
        reuse it. Otherwise create a new one.
        
        Args:
            thread_id: Unique identifier for the conversation thread
            
        Returns:
            Path to the session directory
        """
        # Clean thread_id for filesystem
        safe_thread_id = "".join(c for c in thread_id if c.isalnum() or c in "-_")
        if not safe_thread_id:
            safe_thread_id = "default"
        
        # Look for existing session for this thread within the last hour
        one_hour_ago = datetime.now() - timedelta(hours=1)
        
        for session_dir in self.base_dir.iterdir():
            if session_dir.is_dir() and session_dir.name.startswith(f"{safe_thread_id}_"):
                try:
                    # Extract timestamp from session name
                    timestamp_str = session_dir.name.split("_")[-1]
                    if len(timestamp_str) == 15:  # YYYYMMDD_HHMMSS
                        session_time = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                        if session_time > one_hour_ago:
                            # Reuse existing session
                            self.current_session = session_dir
                            self.current_thread_id = thread_id
                            logger.info(f"♻️ Reusing existing session: {session_dir}")
                            return session_dir
                except Exception:
                    pass
        
        # No recent session found, create new one
        return self.create_session(thread_id)


# Global instance
file_manager = FileManager()