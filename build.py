import os
import shutil
import sys

def create_exe():
    # Create dist directory if it doesn't exist
    if not os.path.exists('dist'):
        os.makedirs('dist')
    
    # Copy templates directory
    if os.path.exists('dist/templates'):
        shutil.rmtree('dist/templates')
    shutil.copytree('templates', 'dist/templates')
    
    # Copy settings.json
    shutil.copy2('settings.json', 'dist/settings.json')
    
    # Create the executable using PyInstaller
    os.system('pyinstaller --noconfirm --onefile --console --name "Forza Telemetry" --add-data "templates;templates" --add-data "settings.json;." server.py')
    
    print("\nBuild complete! You can find the executable in the 'dist' folder.")
    print("Make sure to copy the 'templates' folder and 'settings.json' alongside the executable.")

if __name__ == '__main__':
    create_exe() 