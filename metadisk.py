#! /usr/bin/env python3

import argparse
import os.path
import sys
from hashlib import sha256
from urllib.parse import urljoin


import requests
from btctxstore import BtcTxStore


url_base = 'http://localhost:5000'

parser = argparse.ArgumentParser()
parser.add_argument('action',
                    choices=['audit', 'download', 'files', 'info', 'upload'])

btctx_api = BtcTxStore(testnet=True, dryrun=True)
sender_key = btctx_api.create_key()
sender_address = btctx_api.get_address(sender_key)


def _show_data(response):
    print(response.status_code)
    print(response.text)


def action_audit():
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
    response = requests.get(urljoin(url_base, '/api/files/'))
    _show_data(response)


def action_info():
    response = requests.get(urljoin(url_base, '/api/nodes/me/'))
    _show_data(response)


getattr(sys.modules[__name__], 'action_{}'.format(sys.argv[1]))()


