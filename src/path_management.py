import os
from pathlib import Path
import subprocess
from typing import List

class PathManager:
    def __init__(self):
        self.paths = os.environ.get('PATH', '').split(':')
        self.zsh_files = [
            Path.home() / '.zshrc',
            Path.home() / '.sinrc',
            Path.home() / '.zshenv',
            Path.home() / '.zprofile',
            Path.home() / '.zlogin',
            Path.home() / '.profile',
            Path.home() / '.bash_profile',
            Path.home() / '.bashrc',
            Path('/etc/zshrc'),
            Path('/etc/zshenv'),
            Path('/etc/zprofile'),
            Path('/etc/profile'),
            Path.home() / '.config/zsh/.zshrc',
            Path('/opt/homebrew/bin/brew'),  # Homebrew might modify PATH here
            Path.home() / '.nvm/nvm.sh',     # NVM initialization
            Path.home() / '.rbenv/version'    # rbenv initialization
        ]

    def display_paths(self):
        print("\nCurrent PATH (in order of precedence):")
        for i, path in enumerate(self.paths, 1):
            print(f"{i}. {path}")
        print()

    def swap_paths(self):
        try:
            first = int(input("Enter number of first path: ")) - 1
            second = int(input("Enter number of second path: ")) - 1
            
            if 0 <= first < len(self.paths) and 0 <= second < len(self.paths):
                self.paths[first], self.paths[second] = self.paths[second], self.paths[first]
                print("\nPaths swapped successfully!")
            else:
                print("\nInvalid path numbers!")
        except ValueError:
            print("\nPlease enter valid numbers!")

    def delete_path(self):
        try:
            num = int(input("Enter number of path to delete: ")) - 1
            if 0 <= num < len(self.paths):
                deleted = self.paths.pop(num)
                print(f"\nDeleted: {deleted}")
            else:
                print("\nInvalid path number!")
        except ValueError:
            print("\nPlease enter a valid number!")

    def add_path(self):
        new_path = input("Enter new path: ").strip()
        if not new_path:
            print("\nNo path entered!")
            return
            
        try:
            position = int(input("Enter number after which to add (0 for start): ")) - 1
            if position == -1:
                self.paths.insert(0, new_path)
            elif 0 <= position < len(self.paths):
                self.paths.insert(position + 1, new_path)
            else:
                print("\nInvalid position!")
                return
            print(f"\nAdded: {new_path}")
        except ValueError:
            print("\nPlease enter a valid number!")

    def find_path_modifications(self):
        print("\nSearching for PATH modifications in zsh initialization files...")
        found_any = False
        
        # Common PATH modification patterns
        patterns = [
            'PATH=', 
            'export PATH', 
            'path+=', 
            'PATH+=',
            'path=(',
            'PATH=(',
            '$PATH',
            '${PATH}',
            'typeset.*PATH'
        ]
        
        for file_path in self.zsh_files:
            if not file_path.exists():
                continue
                
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                
                file_has_mods = False
                for i, line in enumerate(lines, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):  # Skip comments
                        if any(pattern in line for pattern in patterns):
                            if not file_has_mods:
                                print(f"\nChecking {file_path}:")
                                file_has_mods = True
                            print(f"line {i}: {line}")
                            found_any = True
                            
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        if not found_any:
            print("\nNo PATH modifications found in standard zsh initialization files.")
            print("There might be modifications in other files or through commands/scripts.")

    def get_current_path(self) -> str:
        return ':'.join(self.paths)
        
    def export_path(self):
        new_path = self.get_current_path()
        print("\nAbout to launch new shell with this PATH:")
        for i, path in enumerate(self.paths, 1):
            print(f"{i}. {path}")
        print("\nLaunching new shell with updated PATH...")
        os.environ['PATH'] = new_path
        
        shell = os.environ.get('SHELL', '/bin/zsh')
        # exec replaces the current process with a new shell
        os.execl(shell, shell)

    def run(self):
        while True:
            self.display_paths()
            print("Commands:")
            print("s - Swap two paths")
            print("d - Delete a path")
            print("a - Add a path")
            print("f - Find PATH modifications in zsh files")
            print("e - Export current PATH")
            print("q - Quit")
            
            choice = input("\nEnter command: ").lower().strip()
            
            if choice == 'q':
                break
            elif choice == 's':
                self.swap_paths()
            elif choice == 'd':
                self.delete_path()
            elif choice == 'a':
                self.add_path()
            elif choice == 'f':
                self.find_path_modifications()
            elif choice == 'e':
                self.export_path()
            else:
                print("\nInvalid command!")

def main():
    manager = PathManager()
    manager.run()
    
    # Print the final PATH as a list
    print("\nFinal PATH (in order):")
    for i, path in enumerate(manager.paths, 1):
        print(f"{i}. {path}")
    
    print("\nTo apply this PATH, you can run:")
    print("export PATH=\"" + manager.get_current_path() + "\"")

if __name__ == "__main__":
    main()