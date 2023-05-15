del dist\*.whl
del dist\*.gz
python -m build
twine upload dist/*
