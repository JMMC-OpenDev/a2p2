#
# minimalist Makefile to launch most common commands
#

install:
	pip install .

clean:
	rm -rf build dist

deploy_pypi:
	rm -rf build dist
	python -m build
	python -m twine upload dist/*


