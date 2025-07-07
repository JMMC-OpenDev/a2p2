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
	read -p "Press enter to deploy on Pypi or ctrl^C to abort" doit
	python -m twine upload dist/*


