"""
Workspace Cleanup Script
------------------------
Cleans up old workspace sessions to free up disk space.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from utils.file_manager import file_manager


def main():
    """Clean up old workspace sessions."""
    print("🧹 Cleaning up old workspace sessions...")
    
    # Clean sessions older than 7 days
    removed = file_manager.cleanup_old_sessions(keep_days=7)
    
    print(f"✅ Removed {removed} old sessions")
    
    # Show current session
    summary = file_manager.get_session_summary()
    if summary.get("active"):
        print(f"\n📁 Current session: {summary['session_path']}")
        print(f"   Files: {summary['file_count']}")
        print(f"   Size: {summary['total_size_mb']} MB")


if __name__ == "__main__":
    main()