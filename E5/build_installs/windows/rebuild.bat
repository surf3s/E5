del dist
python -m PyInstaller --name e5 --noconfirm ..\..\main.py
del e5.spec
copy e5-original.spec e5.spec
python -m PyInstaller e5.spec
copy missing-dlls\*.* dist\e5
copy ..\..\e5.kv dist\e5
copy dist\e5 ..\..\installs\windows
cd ..\..\installs\windows
e5.exe
