#!/usr/bin/env python

from setuptools import setup, find_packages

# from pip.req import parse_requirements

PROJECT = 'escli'
VERSION = '1.0'

try:
    long_description = open('README.rst', 'rt').read()
except IOError:
    long_description = ''

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name=PROJECT,
    version=VERSION,

    description='Escli is CLI for Elasticsearch',
    long_description=long_description,

    author='Jérôme Pin',
    author_email='jpin@wuha.io',

    maintainer='Jérôme Pin',
    maintainer_email='jpin@wuha.io',

    url='https://github.com/wuha-team/escli',

    keywords=['elasticsearch', 'es'],

    classifiers=['Development Status :: 3 - Beta',
                 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.2',
                 'Intended Audience :: Developers',
                 'Intended Audience :: System Administrators',
                 'Environment :: Console'
    ],

    platforms=['Any'],

    scripts=[],

    provides=[],
    install_requires=requirements,

    namespace_packages=[],
    packages=find_packages(),
    include_package_data=True,

    entry_points={
        'console_scripts': [
            'escli = escli.main:main'
        ],
        'escli': [
            'alias create = escli.alias:AliasCreate',
            'alias delete = escli.alias:AliasDelete',
            'alias list = escli.alias:AliasList',
            'cat allocation = escli.cat:CatAllocation',
            'cat shards = escli.cat:CatShards',
            'cluster allocation explain = escli.cluster:ClusterAllocationExplain',
            'cluster health = escli.cluster:ClusterHealth',
            'cluster reroute retry= escli.cluster_reroute:ClusterRerouteRetry',
            'cluster routing allocation enable = escli.cluster:ClusterRoutingAllocationEnable',
            'cluster stats = escli.cluster:ClusterStats',
            'cluster settings get = escli.cluster:ClusterSettingsGet',
            'cluster settings reset = escli.cluster:ClusterSettingsReset',
            'cluster settings set = escli.cluster:ClusterSettingsSet',
            'config context list = escli.config:ConfigContextList',
            'index close = escli.index:IndexClose',
            'index create = escli.index:IndexCreate',
            'index delete = escli.index:IndexDelete',
            'index list = escli.index:IndexList',
            'index open = escli.index:IndexOpen',
            'index settings get = escli.index:IndexSettingsGet',
            'index settings reset = escli.index:IndexSettingsReset',
            'index settings set = escli.index:IndexSettingsSet',
            'index slowlog threshold = escli.index:IndexSlowlogThreshold',
            'logging get = escli.logging:LoggingGet',
            'logging reset = escli.logging:LoggingReset',
            'logging set = escli.logging:LoggingSet',
            'node decommission = escli.node:NodeDecommission',
            'node hot-threads = escli.node:NodeHotThreads',
            'node list = escli.node:NodeList',
            'node recommission = escli.node:NodeRecommission',
            'query search = escli.query:QuerySearch',
            'repository list = escli.backup:RepositoryList',
            'repository show = escli.backup:RepositoryShow',
            'repository verify = escli.backup:RepositoryVerify',
            'snapshot create = escli.backup:SnapshotCreate',
            'snapshot delete = escli.backup:SnapshotDelete',
            'snapshot list = escli.backup:SnapshotList',
            'snapshot restore = escli.backup:SnapshotRestore',
            'snapshot show = escli.backup:SnapshotShow',
        ]
    },

    zip_safe=False,
)
