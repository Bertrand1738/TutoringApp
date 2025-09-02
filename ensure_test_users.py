"""
Check for and run setup_test_users.py to ensure test users are created in the database
"""
import os
import importlib.util
import sys
import subprocess

def setup_and_check_test_users():
    print("Looking for setup_test_users.py...")
    
    # Check if setup_test_users.py exists
    setup_script = os.path.join(os.path.dirname(__file__), 'setup_test_users.py')
    if os.path.exists(setup_script):
        print(f"Found setup script at: {setup_script}")
        
        # Run the setup script to create test users
        print("Running setup_test_users.py to create test users...")
        result = subprocess.run([sys.executable, setup_script], capture_output=True, text=True)
        print("Setup script output:")
        print(result.stdout)
        
        if result.stderr:
            print("Setup script errors:")
            print(result.stderr)
    else:
        print("setup_test_users.py not found.")
        
    # Check if check_users.py exists
    check_script = os.path.join(os.path.dirname(__file__), 'check_users.py')
    if os.path.exists(check_script):
        print("\nRunning check_users.py to verify test users...")
        result = subprocess.run([sys.executable, check_script], capture_output=True, text=True)
        print(result.stdout)
        
        if result.stderr:
            print("Check users script errors:")
            print(result.stderr)

if __name__ == "__main__":
    setup_and_check_test_users()
