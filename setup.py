from distutils.core import setup
setup(
  name = 'YOURPACKAGENAME',         # How you named your package folder (MyLib)
  packages = ['e5'],   # Chose the same as "name"
  version = '1.0.9',      # Start with a small number and increase it with every change you make
  license = 'GNU',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Configurable data entry program for archaeology',   # Give a short description about your library
  author = 'Shannon McPherron',                   # Type in your name
  author_email = 'shannon.mcpherron@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/surf3s/E5',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/surf3s/E5/archive/v1.0.9.tar.gz',    # I explain this later on
  keywords = ['archaeology', 'data entry'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'logging',
		  'kivy',
		  'tinydb',
          'plyer',
      ],
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Users',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: GNU',   # Again, pick a license
    'Programming Language :: Python :: 3.6',
  ],
)