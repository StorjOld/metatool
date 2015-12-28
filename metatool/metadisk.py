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
                                                [--link]
            This action fetch desired file from the server by the "hash name".
            Return nothing if the file downloaded successful.

        <file_hash> - string with represent the "file hash".

        [--link] - will return the url GET request string instead of
                executing the downloading.

        [--decryption_key KEY] - Optional argument. When is defined the file
                downloading from the server in decrypted state (if allowed for
                this file).

            !!!WARNING!!! - will rewrite existed files with the same name!
        [--rename_file NEW_NAME] - Optional argument which define the NAME for
                storing file on your disk. You can indicate an relative and
                full path to the directory with this name as well.
"""
import sys
import os
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

CORE_NODES_URL = ('http://node2.metadisk.org/', 'http://node3.metadisk.org/')
BTCTX_API = BtcTxStore(testnet=True, dryrun=True)


def action_audit(sender_key, file_hash, seed, url_base, btcx_api):
    """
    Action method for audit command
    :return: None
    """
    signature = btcx_api.sign_unicode(sender_key, file_hash)
    sender_address = btcx_api.get_address(sender_key)
    response = requests.post(
        urljoin(url_base, '/api/audit/'),
        data={
            'data_hash': file_hash,
            'challenge_seed': seed,
        },
        headers={
            'sender-address': sender_address,
            'signature': signature,
        }
    )
    return response


def action_download(file_hash, url_base, sender_key, btcx_api,
                    rename_file=None, decryption_key=None, link=False):
    """
    Action method for download command
    :return: response obj
    """
    url_for_requests = urljoin(url_base, '/api/files/' + file_hash)

    params = {}
    if decryption_key:
        params['decryption_key'] = decryption_key

    if rename_file:
        params['file_alias'] = rename_file

    if link:
        data_for_requests = dict(
            params=params
        )
        request = requests.Request('GET', url_for_requests,
                                   **data_for_requests)
        request_string = request.prepare()
        return request_string.url

    signature = btcx_api.sign_unicode(sender_key, file_hash)
    sender_address = btcx_api.get_address(sender_key)

    data_for_requests = dict(
        params=params,
        headers={
            'sender-address': sender_address,
            'signature': signature,
        }
    )

    response = requests.get(
        url_for_requests,
        **data_for_requests
    )

    if response.status_code == 200:
        file_name = os.path.join(os.getcwd(),
                                 response.headers['X-Sendfile'])

        with open(file_name, 'wb') as fp:
            fp.write(response.content)
        return 'saved as {}'.format(file_name)
    else:
        return response


def action_upload(file, sender_key, btcx_api, url_base, file_role):
    """
    Action method for upload command
    :return: response object
    """
    files = {'file_data': file}
    data_hash = sha256(file.read()).hexdigest()
    file.seek(0)
    sender_address = btcx_api.get_address(sender_key)
    signature = btcx_api.sign_unicode(sender_key, data_hash)
    response = requests.post(
        urljoin(url_base, '/api/files/'),
        data={
            'data_hash': data_hash,
            'file_role': file_role,
        },
        files=files,
        headers={
            'sender-address': sender_address,
            'signature': signature,
        }
    )
    return response


def action_files(url_base):
    """Action method for the "files" command.

    Return json-string which is the list of hashes of downloaded files.

    :param url_base: (str) URL string which defines the server will be used.
    :return: response object
    """
    response = requests.get(urljoin(url_base, '/api/files/'))
    return response


def action_info(url_base):
    """Action method for the info" command.

    Return json-string which is the list of hashes of downloaded files.

    :param url_base: (str) URL string which defines the server will be used.
    :return: response object
    """
    response = requests.get(urljoin(url_base, '/api/nodes/me/'))
    return response


def get_all_func_args(function):
    return function.__code__.co_varnames[:function.__code__.co_argcount]


def url_normalize(url_string):
    """
    It puts the URL string into required format.

    :param url_string: (str) URL string which defines the server will be used.

    :return: string obj in http://<net location>
    """
    url_string = url_string.lstrip('/')
    url_string = url_string.split('//')[-1]
    url_string = url_string.lstrip('/')
    url_string = url_string.split('/')[0]
    return 'http://' + url_string


def parse():
    """Set parsing logic for the METATOOL.
    Doesn't perform parsing, just fills the parser object with arguments.

    :return: argparse.ArgumentParser instance
    """
    # create the top-level parser
    main_parser = argparse.ArgumentParser(prog='METATOOL')
    main_parser.add_argument('--url', type=str, dest='url_base')
    subparsers = main_parser.add_subparsers(help='sub-command help')

    # Create the parser for the "audit" command.
    parser_audit = subparsers.add_parser('audit', help='define audit purpose!')
    parser_audit.add_argument('file_hash', type=str, help="file hash")
    parser_audit.add_argument('seed', type=str, help="challenge seed")
    parser_audit.set_defaults(execute_case=action_audit)

    # Create the parser for the "download" command.
    parser_download = subparsers.add_parser('download',
                                            help='define download purpose!')
    parser_download.add_argument('file_hash', type=str, help="file hash")
    parser_download.add_argument('--decryption_key', type=str,
                                 help="decryption key")
    parser_download.add_argument('--rename_file', type=str, help="rename file")
    parser_download.add_argument('--link', action='store_true',
                                 help='will return rust url for man. request')
    parser_download.set_defaults(execute_case=action_download)

    # create the parser for the "upload" command.
    parser_upload = subparsers.add_parser('upload',
                                          help='define upload purpose!')
    parser_upload.add_argument('file', type=argparse.FileType('rb'),
                               help="path to file")
    parser_upload.add_argument('-r', '--file_role', type=str, default='001',
                               help="set file role")
    parser_upload.set_defaults(execute_case=action_upload)

    # create the parser for the "files" command.
    parser_files = subparsers.add_parser('files', help='define files purpose!')
    parser_files.set_defaults(execute_case=action_files)

    # create the parser for the "info" command.
    parser_info = subparsers.add_parser('info', help='define info purpose!')
    parser_info.set_defaults(execute_case=action_info)

    # parse the commands
    return main_parser


def _show_data(data):
        """
        Method to show data in console
        :param response: response from BtcTxStore node
        :return: None
        """
        if isinstance(data, requests.Response):
            print(data.status_code)
            print(data.text)
        else:
            print(data)


def args_preparator(required_args, parsed_args):
    prepared_args = {}
    args_base = dict(
        sender_key=BTCTX_API.create_key(),
        btcx_api=BTCTX_API,
    )
    for required_arg in required_args:
        current_item = getattr(parsed_args, required_arg, 'must be generated!')
        if current_item == 'must be generated!':
            prepared_args[required_arg] = args_base[required_arg]
        else:
            prepared_args[required_arg] = getattr(parsed_args, required_arg)
    return prepared_args


def main():
    """
    METATOOL
    """
    redirect_error_status = (400, 404, 500, 503)
    if len(sys.argv) == 1:
        parse().print_help()
        return
    args = parse().parse_args()
    used_args = args_preparator(get_all_func_args(args.execute_case), args)

    # Get the url from environment variable or from the "--url" parsed argument
    env_node = os.getenv('MEATADISKSERVER', None)
    used_nodes = (env_node,) if env_node else CORE_NODES_URL
    used_nodes = (args.url_base,) if args.url_base else used_nodes
    result = "Sorry, nothing has done."
    for url_base in used_nodes:
        used_args['url_base'] = url_base
        result = args.execute_case(**used_args)
        if isinstance(result, str):
            break
        if result.status_code not in redirect_error_status:
            break
    _show_data(result)


if __name__ == '__main__':
    main()
