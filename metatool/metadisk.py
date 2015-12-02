#! /usr/bin/env python3
"""\
===========================================
welcome to the metatool help information
===========================================

usage:
metatool <action> [ appropriate | arguments | for actions ] [--url URL_ADDR]

"metatool" expect the main first positional argument <action> which define
the action of the program. Must be one of:

    files | info | upload | download | audit

Each of actions expect an appropriate set of arguments after it. They are
separately described below.
Example:

    metatool upload ~/path/to/file.txt --file_role 002

The "--url" optional argument define url address of the target server.
In example:

    metatool info --url http://dev.storj.anvil8.com

But by default the server is "http://dev.storj.anvil8.com/" as well :)
You can either set an system environment variable "MEATADISKSERVER" to
provide target server instead of using the "--url" opt. argument.
------------------------------------------------------------------------------
SPECIFICATION THROUGH ALL OF ACTIONS
Each action return response status as a first line and appropriate data for
a specific action.
When an error is occur whilst the response it will be shown instead of
the success result.

... files
            Return the list of hash-codes of files uploaded at the server or
            return an empty list in the files absence case.

... info
            Return a json file with an information about the data usage of
            the node.

... upload <path_to_file> [-r | --file_role <FILE_ROLE>]
            Upload file to the server.

        <path_to_file> - Name of the file from the working directory
                         or a full/related path to the file.

        [-r | --file_role <FILE_ROLE>]  -  Key "-r" or "--file_role" purposed
                for the setting desired "file role". 001 by default.

            Return a json file with two fields of the information about
            the downloaded file.

... audit <data_hash> <challenge_seed>
            This action purposed for checkout the existence of files on the
            server (in opposite to plain serving hashes of files).
            Return a json file of three files with the response data:
                {
                  "challenge_response": ... ,
                  "challenge_seed": ... ,
                  "data_hash": ... ,
                }

... download <file_hash> [--decryption_key KEY] [--rename_file NEW_NAME]
            This action fetch desired file from the server by the "hash name".
            Return nothing if the file downloaded successful.

        <file_hash> - string with represent the "file hash".

        [--decryption_key KEY] - Optional argument. When is defined the file
                downloading from the server in decrypted state (if allowed for
                this file).

            !!!WARNING!!! - will rewrite existed files with the same name!
        [--rename_file NEW_NAME] - Optional argument which define the NAME for
                storing file on your disk. You can indicate an relative and
                full path to the directory with this name as well.
"""
import sys
import os.path
import argparse
import requests

from hashlib import sha256
from btctxstore import BtcTxStore
# 2.x/3.x compliance logic
if sys.version_info.major == 3:
    from urllib.parse import urljoin
else:
    from urlparse import urljoin


# Get the url from environment variable
url_base = os.getenv('MEATADISKSERVER', 'http://dev.storj.anvil8.com/')

parser = argparse.ArgumentParser()
parser.add_argument('action',
                    choices=['audit', 'download', 'files', 'info', 'upload'])
parser.add_argument('--url', type=str, dest='url_base',
                    default=url_base)

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
        urljoin(args.url_base, '/api/audit/'),
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
        urljoin(args.url_base, '/api/files/' + args.file_hash),
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
        urljoin(args.url_base, '/api/files/'),
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
    args = parser.parse_args()
    response = requests.get(urljoin(args.url_base, '/api/files/'))
    _show_data(response)


def action_info():
    """
    Action method for info command
    :return: None
    """
    args = parser.parse_args()
    response = requests.get(urljoin(args.url_base, '/api/nodes/me/'))
    _show_data(response)


def main():
    if (len(sys.argv) == 1) or (sys.argv[1] in ['-h', '-help', '--help']):
        print(__doc__)
    else:
        getattr(sys.modules[__name__], 'action_{}'.format(sys.argv[1]))()

if __name__ == '__main__':
    main()
