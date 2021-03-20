default: venv submodule
	./venv/bin/python setup.py bdist_wheel

venv:
	python3 -m virtualenv venv

submodule:
	git submodule update --init --recursive

clean:
	# TODO: figure out how to dynamically populate the 0.0.1 based on the version
	rm -rf build/ dist/ test_finder-0.0.1.dist-info test_finder.egg-info
