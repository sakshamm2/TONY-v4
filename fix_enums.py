import os
import re

# Dictionary of Regex patterns to upgrade PySide6/PyQt5 enums to PyQt6
MIGRATIONS = [
    # Alignments
    (r'Qt\.Align(Center|Left|Right|Top|Bottom|VCenter|HCenter|Justify)', r'Qt.AlignmentFlag.Align\1'),
    # Cursors
    (r'Qt\.(PointingHandCursor|OpenHandCursor|ClosedHandCursor|ArrowCursor|IBeamCursor|CrossCursor)', r'Qt.CursorShape.\1'),
    # Widget Attributes
    (r'Qt\.WA_([a-zA-Z0-9_]+)', r'Qt.WidgetAttribute.WA_\1'),
    # Timers
    (r'Qt\.(PreciseTimer|CoarseTimer|VeryCoarseTimer)', r'Qt.TimerType.\1'),
    # Connections
    (r'Qt\.([a-zA-Z0-9_]*Connection)', r'Qt.ConnectionType.\1'),
    # Window Hints / Flags
    (r'Qt\.([a-zA-Z0-9_]*WindowHint)', r'Qt.WindowType.\1'),
    (r'Qt\.Tool', r'Qt.WindowType.Tool'),
    # Scrollbars
    (r'Qt\.ScrollBar(AlwaysOff|AlwaysOn|AsNeeded)', r'Qt.ScrollBarPolicy.ScrollBar\1'),
    # Keys
    (r'Qt\.Key_([a-zA-Z0-9_]+)', r'Qt.Key.Key_\1')
]

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()

    original_content = content
    for pattern, replacement in MIGRATIONS:
        content = re.sub(pattern, replacement, content)

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Updated: {filepath}")

def run_migration(directory):
    print(f"Scanning directory: {directory} for PySide6 -> PyQt6 Enum Migrations...\n")
    for root, dirs, files in os.walk(directory):
        # Skip cache and hidden environments
        if '__pycache__' in root or '.venv' in root or '.git' in root:
            continue
            
        for file in files:
            if file.endswith('.py') and file != 'fix_enums.py':
                process_file(os.path.join(root, file))
    print("\nMigration Complete! You can now run main.py")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    run_migration(current_dir)