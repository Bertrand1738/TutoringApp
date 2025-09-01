"""
Run migrations and save output to a file.
"""
import os
import sys
import subprocess

def main():
    """Run the migration and save output to a file."""
    # Set the command
    command = ["python", "manage.py", "migrate"]
    
    # Run the command and capture output
    process = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Write the output to a file
    with open("migration_output.txt", "w") as f:
        f.write("STDOUT:\n")
        f.write(process.stdout)
        f.write("\n\nSTDERR:\n")
        f.write(process.stderr)
        f.write("\n\nExit code: " + str(process.returncode))
    
    print(f"Migration completed with exit code {process.returncode}")
    print("See migration_output.txt for details")

if __name__ == "__main__":
    main()
