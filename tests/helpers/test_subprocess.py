from src.helpers.run_subprocess import run_subprocess
import os


def test_success():
    assert run_subprocess(['echo', 'hello']) == (0, 'hello')


def test_cwd():
    assert run_subprocess(['touch', 'test.txt'], cwd='/tmp') == (0, '')
    assert os.path.isfile('/tmp/test.txt')
    os.remove('/tmp/test.txt')


def test_error():
    assert run_subprocess(['ls', 'nonexistent']) == (2, "ls: cannot access 'nonexistent': No such file or directory")