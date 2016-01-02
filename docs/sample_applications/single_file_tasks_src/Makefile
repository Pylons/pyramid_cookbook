SHELL = /bin/bash
WGET = wget

PYTHON_VERSION := $(shell python -V 2>&1)
BOOTSTRAP_PY_URL = http://svn.zope.org/*checkout*/zc.buildout/branches/2/bootstrap/bootstrap.py

run: bin/python
	bin/python tasks.py

bin/python: bin/buildout buildout.cfg
	if [[ "$(PYTHON_VERSION)" == Python\ 3* ]]; then echo "*** Python 3 ***"; bin/buildout -c buildout-py3.cfg; else echo "*** Python 2 ***"; bin/buildout; fi

run-buildout: bin/buildout buildout.cfg
	bin/buildout

bin/buildout: bootstrap.py
	python bootstrap.py

bootstrap.py:
	$(WGET) -O bootstrap.py $(BOOTSTRAP_PY_URL)

clean:
	$(RM) -r bin bootstrap.py develop-eggs eggs parts tasks.db var .installed.cfg
