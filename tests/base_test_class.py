from unittest import TestCase
from unittest.mock import patch

import escli.main


class EscliTestCase(TestCase):
    def _setUp(self):
        self.patcher = patch('escli.cluster.Escli')
        self.MockClass = self.patcher.start()
        self.app = escli.main.Escli()

    def mock(self, method_to_mock):
        self.MockClass._es.__setattr__(
            str(method_to_mock) + '.return_value',
            self.fixture()
        )

    def fixture(self):
        raise NotImplementedError()
