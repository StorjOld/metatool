#! /usr/bin/env python3
"""
Metadisc api util

Takes following parameters:
    :param audit: get audit data for given data_hash and challenge_seed
        Example:
            `python3 metadisk.py audit data_hash challenge_seed`
    :param download: download file and save it in current directory by given file_hash
        Example:
            `python3 metadisk.py download file_hash`
        also have two attributes `--decryption_key decryption_key` and `--rename_file new_file_name`
            --decryption_key - download decrypted file using given key
            --rename_file - download file with given new name
        Examples:
            `python3 metadisk.py download file_hash --decryption_key some_key`
            `python3 metadisk.py download file_hash --rename_file new_file_name`
    :param files: get available list of files hashes
        Example:
            `python3 metadisk.py files`

    :param info: return information about node
        Example:
            `python3 metadisk.py info`
    :param upload: upload given file to node
        Example:
            `python3 metadisk.py upload path/to/file`
        also have argument `--file_role`
            --file_role - set file role on node by default 001
        Example:
            `python3 metadisk.py upload path/to/file --file_role 002`
"""
import sys
import os.path
import argparse
import requests

from hashlib import sha256
from btctxstore import BtcTxStore
from urllib.parse import urljoin


url_base = 'http://localhost:5000'

parser = argparse.ArgumentParser()
parser.add_argument('action',
                    choices=['audit', 'download', 'files', 'info', 'upload'])

btctx_api = BtcTxStore(testnet=True, dryrun=True)
sender_key = btctx_api.create_key()
sender_address = btctx_api.get_address(sender_key)


def _show_data(response):
    """
    Method to show data in console
    :param response: response from BtcTxStore node
    :return: None
    """
    print(response.status_code)
    print(response.text)


def action_audit():
    """
    Action method for audit command
    :return: None
    """
    parser.add_argument('file_hash', type=str, help="file hash")
    parser.add_argument('seed', type=str, help="challenge seed")
    args = parser.parse_args()

    signature = btctx_api.sign_unicode(sender_key, args.file_hash)

    response = requests.post(
        urljoin(url_base, '/api/audit/'),
        data={
            'data_hash': args.file_hash,
            'challenge_seed': args.seed,
        },
        headers={
            'sender-address': sender_address,
            'signature': signature,
        }
    )
    _show_data(response)


def action_download():
    """
    Action method for download command
    :return: None
    """
    parser.add_argument('file_hash', type=str, help="file hash")
    parser.add_argument('--decryption_key', type=str, help="decryption key")
    parser.add_argument('--rename_file', type=str, help="rename file")

    args = parser.parse_args()

    signature = btctx_api.sign_unicode(sender_key, args.file_hash)
    params = {}

    if args.decryption_key:
        params['decryption_key'] = args.decryption_key

    if args.rename_file:
        params['file_alias'] = args.rename_file

    response = requests.get(
        urljoin(url_base, '/api/files/' + args.file_hash),
        params=params,
        headers={
            'sender-address': sender_address,
            'signature': signature,
        }
    )

    if response.status_code == 200:
        file_name = os.path.join(os.path.dirname(__file__),
                                 response.headers['X-Sendfile'])
        with open(file_name, 'wb') as fp:
            fp.write(response.content)
    else:
        _show_data(response)


def action_upload():
    """
    Action method for upload command
    :return: None
    """
    parser.add_argument('file', type=argparse.FileType('rb'),
                        help="path to file")
    parser.add_argument('-r', '--file_role', type=str, default='001',
                        help="set file role")
    args = parser.parse_args()
    files = {'file_data': args.file}
    data_hash = sha256(args.file.read()).hexdigest()
    args.file.seek(0)
    signature = btctx_api.sign_unicode(sender_key, data_hash)

    response = requests.post(
        urljoin(url_base, '/api/files/'),
        data={
            'data_hash': data_hash,
            'file_role': args.file_role,
        },
        files=files,
        headers={
            'sender-address': sender_address,
            'signature': signature,
        }
    )
    _show_data(response)


def action_files():
    """
    Action method for files command
    :return: None
    """
    response = requests.get(urljoin(url_base, '/api/files/'))
    _show_data(response)


def action_info():
    """
    Action method for info command
    :return: None
    """
    response = requests.get(urljoin(url_base, '/api/nodes/me/'))
    _show_data(response)


getattr(sys.modules[__name__], 'action_{}'.format(sys.argv[1]))()


