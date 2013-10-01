import os
import pkg_resources
import shutil
import subprocess
import tempfile
import time

try:
    import httplib
except ImportError: # pragma: no cover
    import http.client as httplib

from pyramid.scaffolds.tests import TemplateTest

class SubstanceDTemplateTest(TemplateTest):
    # Override to avoid pyramid-specific stuff
    def install(self, tmpl_name): # pragma: no cover
        try:
            self.old_cwd = os.getcwd()
            self.directory = tempfile.mkdtemp()
            self.make_venv(self.directory)
            os.chdir(pkg_resources.get_distribution('substanced').location)
            subprocess.check_call(
                [os.path.join(self.directory, 'bin', 'python'),
                 'setup.py', 'develop'])
            os.chdir(self.directory)
            subprocess.check_call(['bin/pcreate', '-s', tmpl_name, 'Dingle'])
            os.chdir('Dingle')
            py = os.path.join(self.directory, 'bin', 'python')
            subprocess.check_call([py, 'setup.py', 'install'])
            subprocess.check_call([py, 'setup.py', 'test'])
            pserve = os.path.join(self.directory, 'bin', 'pserve')
            for ininame, hastoolbar in (('development.ini', True),
                                        ('production.ini', False)):
                proc = subprocess.Popen([pserve, ininame])
                try:
                    time.sleep(5)
                    proc.poll()
                    if proc.returncode is not None:
                        raise RuntimeError('%s didnt start' % ininame)
                    conn = httplib.HTTPConnection('localhost:6543')
                    conn.request('GET', '/')
                    resp = conn.getresponse()
                    assert resp.status == 200, ininame
                    data = resp.read()
                    toolbarchunk = b'<div id="pDebug"'
                    if hastoolbar:
                        assert toolbarchunk in data, ininame
                    else:
                        assert not toolbarchunk in data, ininame
                finally:
                    proc.terminate()
        finally:
            shutil.rmtree(self.directory)
            os.chdir(self.old_cwd)


if __name__ == '__main__':     # pragma: no cover
    test = SubstanceDTemplateTest()
    test.install('substanced')
