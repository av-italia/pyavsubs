tests:
	python -m unittest discover -s tests -p "test_*.py"

build:
	python3 -m build
