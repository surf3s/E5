# Windows distribution without installing Python

The dist folder here contains a one file executable of the E5 program (E5py.exe).  On Windows, download this file to a folder for the program, and it should run without the need to install Python or Python packages.  It works fine on my own Windows 10 computer.  If someone runs it on Windows 11, please let me know the results.

At times the source code might get ahead of this executable, but I will do my best to update it when major changes occur.

If you are developer, you can use the E5py.spec file included here to rebuild a distribution of E5py.exe.  The file build_windows.bat contains the proper syntax (python -m PyInstaller E5py.spec).  Note that this command assumes that your are in a virtual environment with all the packages installed to run E5py.  Note also that I was unable to make it work with the latest version of PyInstaller.  I recommend instead using pip install pyinstaller==4.10.  This version of PyInstaller worked fine for me.