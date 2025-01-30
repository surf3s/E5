del dist\*.whl
del dist\*.gz
python -m build
python -m rename_copy