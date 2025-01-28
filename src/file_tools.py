import os
import shutil
from pathlib import Path
import subprocess
from datetime import datetime
from typing import List, Dict, Set, Optional
import logging
import argparse

class Colors:
    """Because ANSI codes are just spicy strings."""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'

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

    # Size thresholds for color coding (in bytes)
    SIZE_THRESHOLDS = {
        1_000_000_000: (Colors.RED, "😱"),      # 1GB+
        500_000_000: (Colors.MAGENTA, "😰"),    # 500MB+
        100_000_000: (Colors.YELLOW, "😅"),     # 100MB+
        50_000_000: (Colors.CYAN, "😌"),        # 50MB+
        0: (Colors.GREEN, "😊"),                # Everything else
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

    def _get_size_color(self, size: int) -> tuple[str, str]:
        """Get the appropriate color and emoji for a given size."""
        for threshold, (color, emoji) in sorted(self.SIZE_THRESHOLDS.items(), reverse=True):
            if size >= threshold:
                return color, emoji
        return Colors.CYAN, "😊"  # Default

    def _format_size(self, size: int) -> str:
        """Convert bytes to human readable format with color."""
        color, emoji = self._get_size_color(size)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{color}{size:.1f}{unit} {emoji}{Colors.RESET}"
            size /= 1024
        return f"{color}{size:.1f}TB {emoji}{Colors.RESET}"

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
                prefix = f"{Colors.BLUE}└──{Colors.RESET}" if depth > 0 else ""
                name_color = Colors.CYAN if depth == 0 else Colors.WHITE
                self.logger.info(f"{indent}{prefix} {name_color}{path.name}/{Colors.RESET} ({self._format_size(size)})")
                
                subdirs = [
                    (p, get_dir_info(p)) 
                    for p in path.iterdir() 
                    if p.is_dir() and not p.name.startswith('.')
                ]
                
                sorted_subdirs = sorted(
                    subdirs,
                    key=lambda x: (-x[1][0], x[1][1])  # -size for descending, name for ties
                )
                
                for subdir, _ in sorted_subdirs:
                    print_tree(subdir, depth + 1)

        self.logger.info(f"\n{Colors.GREEN}Directory Tree{Colors.RESET} (max depth: {max_depth}, sorted by size):")
        print_tree(root)

    def find_ignored_dirs(self, dry_run: bool = True) -> None:
        """Find all commonly ignored directories."""
        root = Path(self.current_dir)
        found_dirs: List[Path] = []

        for ignored_dir in self.COMMON_IGNORED_DIRS:
            found_dirs.extend(root.glob(f'**/{ignored_dir}'))

        total_size = sum(self._get_dir_size(d) for d in found_dirs)
        
        self.logger.info(f"\n{Colors.YELLOW}Found potentially removable directories:{Colors.RESET}")
        for dir_path in sorted(found_dirs):
            size = self._get_dir_size(dir_path)
            self.logger.info(f"{Colors.BLUE}•{Colors.RESET} {dir_path} ({self._format_size(size)})")
        
        self.logger.info(f"\n{Colors.MAGENTA}Total space used: {self._format_size(total_size)}{Colors.RESET}")
        
        if not dry_run:
            self.logger.info(f"\n{Colors.RED}Deleting directories...{Colors.RESET}")
            for dir_path in found_dirs:
                try:
                    shutil.rmtree(dir_path)
                    self.logger.info(f"{Colors.GREEN}✓{Colors.RESET} Deleted {dir_path}")
                except Exception as e:
                    self.logger.error(f"{Colors.RED}✗{Colors.RESET} Failed to delete {dir_path}: {str(e)}")

    def find_uncommitted_changes(self) -> Dict[str, str]:
        """Find all git repositories with uncommitted changes."""
        root = Path(self.current_dir)
        repos_with_changes: Dict[str, str] = {}

        self.logger.info(f"\n{Colors.YELLOW}Scanning for uncommitted changes...{Colors.RESET}")
        
        for git_dir in root.glob('**/.git'):
            repo_path = git_dir.parent
            try:
                result = subprocess.run(
                    ['git', 'status', '--porcelain'],
                    cwd=repo_path,
                    capture_output=True,
                    text=True
                )
                
                if result.stdout.strip():
                    repos_with_changes[str(repo_path)] = result.stdout
                    self.logger.info(f"{Colors.RED}•{Colors.RESET} Changes found in: {Colors.CYAN}{repo_path}{Colors.RESET}")
            
            except subprocess.SubprocessError as e:
                self.logger.error(f"{Colors.RED}Error checking {repo_path}: {str(e)}{Colors.RESET}")

        if not repos_with_changes:
            self.logger.info(f"{Colors.GREEN}No uncommitted changes found. You're squeaky clean! 🧼{Colors.RESET}")
            
        return repos_with_changes

    def commit_all_changes(self) -> None:
        """Commit all changes in repositories with uncommitted work."""
        repos_with_changes = self.find_uncommitted_changes()
        
        if not repos_with_changes:
            return

        date_str = datetime.now().strftime('%Y%m%d')
        commit_msg = f"{date_str} commit for transfer"

        self.logger.info(f"\n{Colors.YELLOW}Committing changes...{Colors.RESET}")
        
        for repo_path in repos_with_changes:
            try:
                subprocess.run(['git', 'add', '-A'], cwd=repo_path, check=True)
                subprocess.run(['git', 'commit', '-m', commit_msg], cwd=repo_path, check=True)
                self.logger.info(f"{Colors.GREEN}✓{Colors.RESET} Committed changes in {Colors.CYAN}{repo_path}{Colors.RESET}")
            
            except subprocess.SubprocessError as e:
                self.logger.error(f"{Colors.RED}✗ Failed to commit changes in {repo_path}: {str(e)}{Colors.RESET}")

def main():
    """CLI entry point for our file management salvation."""
    parser = argparse.ArgumentParser(
        description=f"{Colors.CYAN}File management tools that spark joy (and free up disk space){Colors.RESET}"
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