import os
from pathlib import Path

current_dir = os.environ.get('CURRENT_DIR')

print(f"This is running from: {os.getcwd()}")
print(f"But lives in: {Path(__file__).parent}")
print(f"And was ACTUALLY summoned from: {current_dir}")

# Now we're cooking with gas!
for item in os.listdir(current_dir):
    print(item)