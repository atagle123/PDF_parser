import subprocess
import sys
import os

from setuptools import setup, find_packages

# Function to create conda environment and install packages from environment YAML
def setup_conda_environment():
    env_yml = 'environment.yml'

    # Check if conda is available
    try:
        subprocess.run(['conda', '--version'], check=True, stdout=subprocess.PIPE)
    except subprocess.CalledProcessError:
        print("Error: Conda not found. Please install Anaconda or Miniconda.")
        sys.exit(1)

    # Create conda environment from environment.yml
    print(f"Creating conda environment ")
    create_env_command = f"conda env create  -f {env_yml}"
    subprocess.run(create_env_command, shell=True, check=True)

    # Activate the created environment
    activate_env_command = f"conda activate pdf_parser"
    subprocess.run(activate_env_command, shell=True, check=True)

# Function to install your package
def install_package():
    setup(
        name='pdf_extractor',
        version='0.1',
        packages=find_packages(),
        # Add any additional setup options as needed
    )

# Main setup process
if __name__ == '__main__':
    setup_conda_environment()
    install_package()
