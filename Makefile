
.PHONY:	test requirements test-requirements

requirements:
	pip install -r requirements.txt

test-requirements: requirements
	pip install -r requirements-test.txt

test-local:
	rm -rf .coverage
	python -m coverage run -m nose --with-xunit --xunit-file=unittests.xml -A 'not acceptance'

test: test-requirements develop test-local

develop: requirements develop-local

develop-local: uninstall
	python setup.py develop

uninstall:
	python setup.py clean

coverage-local: test-local
	python -m coverage html
	python -m coverage xml -o coverage.xml

	# Compute pep8 quality
	pep8 sqlite_influx > pep8.report || echo "Not pep8 clean"

	# Compute pylint quality
	pylint -f parseable sqlite_influx --msg-template "{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" > pylint.report || echo "Not pylint clean"

coverage: test coverage-local

deploy-package:
	python setup.py sdist
