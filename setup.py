#!/usr/bin/env python3

# python setup.py sdist --format=zip,gztar

from setuptools import setup
import os
import sys
import platform
import imp
import argparse

version = imp.load_source('version', 'lib/version.py')

if sys.version_info[:3] < (3, 4, 0):
    sys.exit("Error: Electron Cash requires Python version >= 3.4.0...")

data_files = []

if platform.system() in ['Linux', 'FreeBSD', 'DragonFly']:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root=', dest='root_path', metavar='dir', default='/')
    opts, _ = parser.parse_known_args(sys.argv[1:])
    usr_share = os.path.join(sys.prefix, "share")
    if not os.access(opts.root_path + usr_share, os.W_OK) and \
       not os.access(opts.root_path, os.W_OK):
        if 'XDG_DATA_HOME' in os.environ.keys():
            usr_share = os.environ['XDG_DATA_HOME']
        else:
            usr_share = os.path.expanduser('~/.local/share')
    data_files += [
        (os.path.join(usr_share, 'applications/'), ['bitcoinnano.desktop']),
        (os.path.join(usr_share, 'pixmaps/'), ['icons/bicoinnano.png'])
    ]

setup(
    name="Bitcoin Nano",
    version=version.ELECTRUM_VERSION,
    install_requires=[
        'pyaes>=0.1a1',
        'ecdsa>=0.9',
        'pbkdf2',
        'requests',
        'qrcode',
        'protobuf',
        'dnspython',
        'jsonrpclib-pelix',
        'PySocks>=1.6.6',
    ],
    packages=[
        'bitcoinnano',
        'bitcoinnano_gui',
        'bitcoinnano_gui.qt',
        'bitcoinnano_plugins',
        'bitcoinnano_plugins.audio_modem',
        'bitcoinnano_plugins.cosigner_pool',
        'bitcoinnano_plugins.email_requests',
        'bitcoinnano_plugins.hw_wallet',
        'bitcoinnano_plugins.keepkey',
        'bitcoinnano_plugins.labels',
        'bitcoinnano_plugins.ledger',
        'bitcoinnano_plugins.trezor',
        'bitcoinnano_plugins.digitalbitbox',
        'bitcoinnano_plugins.virtualkeyboard',
    ],
    package_dir={
        'bitcoinnano': 'lib',
        'bitcoinnano_gui': 'gui',
        'bitcoinnano_plugins': 'plugins',
    },
    package_data={
        'bitcoinnano': [
            'servers.json',
            'servers_testnet.json',
            'currencies.json',
            'www/index.html',
            'wordlist/*.txt',
            'locale/*/LC_MESSAGES/electrum.mo',
        ]
    },
    scripts=['bitcoinnano'],
    data_files=data_files,
    description="Lightweight Bitcoin Cash Wallet",
    author="Jonald Fyookball",
    author_email="jonf@bitcoinnano.org",
    license="MIT Licence",
    url="http://www.btcnano.org",
    long_description="""Lightweight Bitcoin Cash Wallet"""
)
