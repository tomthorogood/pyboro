register: docs
	python setup.py sdist bdist egg register upload

docs:
	cp README.md docs/
	cd docs && $(MAKE) all
	cd docs && $(MAKE) clean

clean:
	rm -rf pyRex.egg-info
	rm -rf dist/
	rm -rf build/

