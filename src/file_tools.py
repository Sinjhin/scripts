import os
import shutil
from pathlib import Path
import subprocess
from datetime import datetime
from typing import List, Dict, Set, Optional
import logging
import argparse

class FileTools:
    """Because sometimes you need to clean house, and your house is full of code."""
    
    COMMON_IGNORED_DIRS = {
        'node_modules',
        'dist',
        'build',
        '__pycache__',
        '.pytest_cache',
        'target',      # Rust
        'vendor',      # Go
        '.gradle',     # Gradle
        'bin',
        'obj',        # .NET
        '.dart_tool',  # Dart
        'venv',
        '.venv',
        'env',
    }

    def __init__(self):
        self.current_dir = os.environ.get('CURRENT_DIR', os.getcwd())
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger('FileTools')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _get_dir_size(self, path: Path) -> int:
        """Calculate directory size in bytes."""
        return sum(f.stat().st_size for f in path.glob('**/*') if f.is_file())

    def _format_size(self, size: int) -> str:
        """Convert bytes to human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"

    def list_subdirs(self, max_depth: int = 2) -> None:
        """List all subdirectories up to specified depth with their sizes, sorted by size (descending)."""
        root = Path(self.current_dir)
        
        def get_dir_info(path: Path) -> tuple[int, str]:
            """Get directory size and name as a sortable tuple."""
            return (self._get_dir_size(path), path.name)
        
        def print_tree(path: Path, depth: int = 0) -> None:
            if depth > max_depth:
                return
            
            if path.is_dir() and not path.name.startswith('.'):
                size = self._get_dir_size(path)
                indent = "  " * depth
                prefix = "└──" if depth > 0 else ""
                self.logger.info(f"{indent}{prefix} {path.name}/ ({self._format_size(size)})")
                
                # Get all subdirectories and their sizes
                subdirs = [
                    (p, get_dir_info(p)) 
                    for p in path.iterdir() 
                    if p.is_dir() and not p.name.startswith('.')
                ]
                
                # Sort by size descending, then name ascending for same sizes
                sorted_subdirs = sorted(
                    subdirs,
                    key=lambda x: (-x[1][0], x[1][1])  # -size for descending, name for ties
                )
                
                for subdir, _ in sorted_subdirs:
                    print_tree(subdir, depth + 1)

        self.logger.info(f"\nDirectory Tree (max depth: {max_depth}, sorted by size):")
        print_tree(root)

    def find_ignored_dirs(self, dry_run: bool = True) -> None:
        """Find all commonly ignored directories."""
        root = Path(self.current_dir)
        found_dirs: List[Path] = []

        for ignored_dir in self.COMMON_IGNORED_DIRS:
            found_dirs.extend(root.glob(f'**/{ignored_dir}'))

        total_size = sum(self._get_dir_size(d) for d in found_dirs)
        
        self.logger.info("\nFound potentially removable directories:")
        for dir_path in sorted(found_dirs):
            size = self._get_dir_size(dir_path)
            self.logger.info(f"- {dir_path} ({self._format_size(size)})")
        
        self.logger.info(f"\nTotal space used: {self._format_size(total_size)}")
        
        if not dry_run:
            self.logger.info("\nDeleting directories...")
            for dir_path in found_dirs:
                try:
                    shutil.rmtree(dir_path)
                    self.logger.info(f"✓ Deleted {dir_path}")
                except Exception as e:
                    self.logger.error(f"✗ Failed to delete {dir_path}: {str(e)}")

    def find_uncommitted_changes(self) -> Dict[str, str]:
        """Find all git repositories with uncommitted changes."""
        root = Path(self.current_dir)
        repos_with_changes: Dict[str, str] = {}

        for git_dir in root.glob('**/.git'):
            repo_path = git_dir.parent
            try:
                # Check for changes
                result = subprocess.run(
                    ['git', 'status', '--porcelain'],
                    cwd=repo_path,
                    capture_output=True,
                    text=True
                )
                
                if result.stdout.strip():
                    repos_with_changes[str(repo_path)] = result.stdout
                    self.logger.info(f"\nFound changes in {repo_path}:")
                    self.logger.info(result.stdout)
            
            except subprocess.SubprocessError as e:
                self.logger.error(f"Error checking {repo_path}: {str(e)}")

        return repos_with_changes

    def commit_all_changes(self) -> None:
        """Commit all changes in repositories with uncommitted work."""
        repos_with_changes = self.find_uncommitted_changes()
        
        if not repos_with_changes:
            self.logger.info("No repositories with uncommitted changes found.")
            return

        date_str = datetime.now().strftime('%Y%m%d')
        commit_msg = f"{date_str} commit for transfer"

        for repo_path in repos_with_changes:
            try:
                # Add all changes
                subprocess.run(['git', 'add', '-A'], cwd=repo_path, check=True)
                
                # Commit changes
                subprocess.run(
                    ['git', 'commit', '-m', commit_msg],
                    cwd=repo_path,
                    check=True
                )
                
                self.logger.info(f"✓ Committed changes in {repo_path}")
            
            except subprocess.SubprocessError as e:
                self.logger.error(f"✗ Failed to commit changes in {repo_path}: {str(e)}")

def main():
    """CLI entry point for our file management salvation."""
    parser = argparse.ArgumentParser(
        description="File management tools that spark joy (and free up disk space)"
    )
    parser.add_argument(
        '--tree', 
        action='store_true', 
        help='List subdirectories in tree format with sizes'
    )
    parser.add_argument(
        '--depth', 
        type=int, 
        default=2,
        help='Maximum depth for directory tree (default: 2)'
    )
    parser.add_argument(
        '--find-ignored', 
        action='store_true', 
        help='Find commonly ignored directories (dry run)'
    )
    parser.add_argument(
        '--delete-ignored', 
        action='store_true', 
        help='Delete commonly ignored directories (careful now!)'
    )
    parser.add_argument(
        '--find-uncommitted', 
        action='store_true', 
        help='Find repositories with uncommitted changes'
    )
    parser.add_argument(
        '--commit-all', 
        action='store_true', 
        help='Commit all changes with timestamp message'
    )
    
    args = parser.parse_args()
    tools = FileTools()
    
    if not any(vars(args).values()):
        parser.print_help()
        return

    if args.tree:
        tools.list_subdirs(max_depth=args.depth)
    
    if args.find_ignored:
        tools.find_ignored_dirs(dry_run=True)
    
    if args.delete_ignored:
        tools.find_ignored_dirs(dry_run=False)
    
    if args.find_uncommitted:
        tools.find_uncommitted_changes()
    
    if args.commit_all:
        tools.commit_all_changes()

if __name__ == '__main__':
    main()