
import pytest

from nepymc import ini
from nepymc.mainloop import EmcMainLoop


@pytest.fixture(scope='module')
def mainloop():
    ini.setup_defaults()
    return EmcMainLoop()
