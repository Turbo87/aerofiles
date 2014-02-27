import pytest

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from aerofiles.flarmcfg import Writer


@pytest.fixture()
def output():
    return StringIO()


@pytest.fixture()
def writer(output):
    return Writer(output)


def test_write_line(writer):
    writer.write_line('line')
    assert writer.fp.getvalue() == 'line\r\n'


def test_write_config(writer):
    writer.write_config('ID', '4B3E60')
    assert writer.fp.getvalue() == '$PFLAC,S,ID,4B3E60\r\n'


def test_write_pilot(writer):
    writer.write_pilot('FTV Spandau')
    assert writer.fp.getvalue() == '$PFLAC,S,PILOT,FTV Spandau\r\n'


def test_write_copilot(writer):
    writer.write_copilot('John Doe')
    assert writer.fp.getvalue() == '$PFLAC,S,COPIL,John Doe\r\n'


def test_write_glider_type(writer):
    writer.write_glider_type('Astir CS')
    assert writer.fp.getvalue() == '$PFLAC,S,GLIDERTYPE,Astir CS\r\n'


def test_write_glider_id(writer):
    writer.write_glider_id('D-8551')
    assert writer.fp.getvalue() == '$PFLAC,S,GLIDERID,D-8551\r\n'


def test_write_competition_id(writer):
    writer.write_competition_id('75')
    assert writer.fp.getvalue() == '$PFLAC,S,COMPID,75\r\n'


def test_write_competition_class(writer):
    writer.write_competition_class('Club')
    assert writer.fp.getvalue() == '$PFLAC,S,COMPCLASS,Club\r\n'


def test_write_logger_interval(writer):
    writer.write_logger_interval(4)
    assert writer.fp.getvalue() == '$PFLAC,S,LOGINT,4\r\n'


def test_write_task_declaration(writer):
    writer.write_task_declaration('My Task')
    assert writer.fp.getvalue() == '$PFLAC,S,NEWTASK,My Task\r\n'


def test_write_default_task_declaration(writer):
    writer.write_task_declaration()
    assert writer.fp.getvalue() == '$PFLAC,S,NEWTASK,\r\n'
