from setuptools import setup, find_packages


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="e5",
    version="1.0.903",
    description = 'Configurable data entry program for archaeology',
	author = 'Shannon McPherron',
	author_email = 'shannon.mcpherron@gmail.com',
	url = 'https://github.com/surf3s/E5',   
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages = find_packages(exclude=["*.backup", "*.build_installs"]),
    classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: End Users/Desktop',	
    'Intended Audience :: Developers',    
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Programming Language :: Python :: 3.6',
    ],
    package_data={
        # If any package contains *.txt files, include them:
        '': ['*.kv','requirements.txt'],
        # And include any *.dat files found in the 'data' subdirectory
        # of the 'mypkg' package, also:
        'e5': ['cfgs/*.cfg'],
    },
    install_requires=[
		'tinydb>=3.11.1',
		'plyer>=1.4.0'
    ],
    python_requires='>=3.6',
)
