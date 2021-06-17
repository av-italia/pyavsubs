tests:
	python -m unittest discover -s tests -p "test_*.py"

build:
	python3 -m build

install:
	python3 -m pip install git+https://github.com/av-italia/pyavsubs.git@main
