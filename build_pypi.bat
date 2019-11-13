del dist\*.gz
del e5.egg-info\SOURCES.txt
del e5.egg-info\requires.txt
python -m setup sdist
twine upload dist/*
