import glob
import shutil
import os

# Get the name of the .gz file in the dist directory
gz_files = glob.glob('dist/*.gz')
if not gz_files:
    raise FileNotFoundError("No .gz file found in the dist directory")

gz_file = gz_files[0]

# Define the destination path
destination = os.path.join('..', 'e5_test', 'e5_test.tar.gz')

# Copy the .gz file to the destination
shutil.copy(gz_file, destination)

print(f"Copied {gz_file} to {destination}")