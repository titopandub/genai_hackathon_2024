from ddtrace import tracer
import dotenv
from src.config import config
import sys

tracer.enabled = False

dotenv.load_dotenv()

import src.monkey_patch
from alembic.config import Config
from alembic import command

from unittest.case import TestCase

config['slow_timeout'] = 120

if 'unittest' in sys.modules.keys():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

def assertIn(self, member, container, msg=None):
    """Just like self.assertTrue(a in b), but with a nicer default message."""
    if member not in container:
        standardMsg = '%s not found ' % (member)
        print(container)
        self.fail(self._formatMessage(msg, standardMsg))

TestCase.assertIn = assertIn        