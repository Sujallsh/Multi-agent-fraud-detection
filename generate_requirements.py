#!/usr/bin/env python3
"""
Script to generate requirements.txt with pinned versions for reproducibility.
This ensures the exact same package versions are installed across different environments.
"""

import subprocess
import sys
import os

def generate_requirements_txt(output_file='requirements.txt'):
    """
    Generate requirements.txt with currently installed package versions.
    """
    try:
        # Get list of installed packages with versions
        result = subprocess.run([sys.executable, '-m', 'pip', 'freeze'],
                              capture_output=True, text=True, check=True)

        requirements = result.stdout.strip()

        # Write to file
        with open(output_file, 'w') as f:
            f.write("# Auto-generated requirements.txt with pinned versions\n")
            f.write("# Generated for reproducibility\n\n")
            f.write(requirements)
            f.write("\n")

        print(f"Successfully generated {output_file} with {len(requirements.splitlines())} packages")

    except subprocess.CalledProcessError as e:
        print(f"Error generating requirements.txt: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_requirements_txt()