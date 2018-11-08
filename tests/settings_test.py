from unittest import TestCase
from unittest.mock import patch

import escli.settings


class TestClusterSettings(TestCase):
    def setUp(self):
        self.patcher = patch('escli.settings.Escli')
        self.MockClass = self.patcher.start()
        self.MockClass._es.cluster.get_settings.return_value = self.cluster_settings_fixture()

    def cluster_settings_fixture(self):
        return {
            "persistent": {
                "cluster.routing.allocation.node_concurrent_recoveries": "12",
                "cluster.routing.allocation.enable": "none"
            },
            "transient": {
                "cluster.routing.allocation.node_concurrent_recoveries": "6",
                "cluster.routing.allocation.enable": "ALL"
            }
        }

    def test_get(self):
        cluster_settings = escli.settings.ClusterSettings()
        self.assertEqual(
            cluster_settings.get(
                'cluster.routing.allocation.node_concurrent_recoveries',
                persistency='transient'
            ),
            "6"
        )
        self.assertEqual(
            cluster_settings.get(
                'cluster.routing.allocation.node_concurrent_recoveries',
                persistency='persistent'
            ),
            "12"
        )
        self.assertEqual(
            cluster_settings.get(
                'cluster.routing.allocation.enable',
                persistency='persistent'
            ),
            "NONE"
        )
        self.assertEqual(
            cluster_settings.get(
                'cluster.routing.allocation.enable',
                persistency='transient'
            ),
            "ALL"
        )
        self.assertEqual(
            cluster_settings.get(
                'cluster.routing.allocation.foobar',
                persistency='transient'
            ),
            None
        )
