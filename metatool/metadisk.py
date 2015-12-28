#! /usr/bin/env python3
"""\
===========================================
welcome to the metatool help information
===========================================

usage:
metatool [--url URL_ADDR] <action> [ appropriate | arguments | for actions ]

"metatool" expect the main first positional argument <action> which define
the action of the program. Must be one of:

    files | info | upload | download | audit

Each of actions expect an appropriate set of arguments after it. They are
separately described below.
Example:

    metatool upload ~/path/to/file.txt --file_role 002

The "--url" optional argument define url address of the target server.
In example:

    metatool --url http://dev.storj.anvil8.com info

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
            This action purposed for checking out the existence of files on the
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

        <file_hash> - string which represents the "file hash".

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


def action_audit(url_base, sender_key, btctx_api, file_hash, seed):
    """
    It performs an request to the server with a view of calculating
    the SHA-256 hash of a file plus some seed.
    It will return the response object with information about the server-error
    when such has occurred.

    :param url_base:  (str) URL string which defines the server will be used.
    :param sender_key: (str) unique secret key which will be used for the
                        generating credentials required by the access to the
                        server.
    :param btctx_api:  instance of the BtcTxStore class from btctxstore module.
                        It will be used to generate credentials for server
                        access. (https://pypi.python.org/pypi/btctxstore/4.6.0)
    :param file_hash:  (str) hash-name of the file you are going to audit.
    :param seed: (str) should be a SHA-256 hash of that you would like to add
                        to the file data to generate a challenge response.
    :return: response: (<class 'requests.models.Response'>) response instance
                        with the results of challenge or with information about
                        the server issue.
    """
    signature = btctx_api.sign_unicode(sender_key, file_hash)
    sender_address = btctx_api.get_address(sender_key)
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


def action_download(url_base, sender_key, btctx_api, file_hash,
                    rename_file=None, decryption_key=None, link=False):
    """
    It performs the downloading of the file from the server
    by the given "file_hash".
    If "link=True" will return GET-request URL-string instead of performing the
    download, so you can use it like a simple URL address and download it
    through the browser.
        None: The "link=True" case implies non-authenticated access to the
        file, available only for files with such values of "roles": 101, 001

    Will return the response object with information about the server-error
    when such has occurred.

    :param url_base:  (str) URL string which defines the server will be used.
    :param sender_key: (str) unique secret key which will be used for the
                        generating credentials required by the access to the
                        server.
    :param btctx_api:  instance of the BtcTxStore class from btctxstore module.
                        It will be used to generate credentials for server
                        access. (https://pypi.python.org/pypi/btctxstore/4.6.0)
    :param file_hash:  (str) hash-name of the file on the remote server.
    :param rename_file:  (str) defines new name of the file after downloading.
    :param decryption_key:  (str)  key value which will be used to decrypt file
                            on the server before the downloading (if allowed by
                            the role).
    :param link: (boll) If True is given, function will generate and return
                        the appropriate GET URL-string instead of performing
                        the downloading process.
    :return:
        <file_path>: (str) will return full path to the file if downloaded
                            done successfully.
        <GET URL-string>: (str) if "link=True" will return GET-request
                            URL-string, instead of processing the downloading.
        response_object: (<class 'requests.models.Response'>) with information
                            about the occurred error on the server while
                            the downloading.
    """
    url_for_requests = urljoin(url_base, '/api/files/' + file_hash)

    params = {}
    if decryption_key:
        params['decryption_key'] = decryption_key

    if rename_file:
        params['file_alias'] = rename_file

    data_for_requests = dict(params=params)
    if link:
        request = requests.Request('GET', url_for_requests,
                                   **data_for_requests)
        request_string = request.prepare()
        return request_string.url

    signature = btctx_api.sign_unicode(sender_key, file_hash)
    sender_address = btctx_api.get_address(sender_key)

    data_for_requests['headers'] = {
        'sender-address': sender_address,
        'signature': signature,
    }

    response = requests.get(
        url_for_requests,
        **data_for_requests
    )

    if response.status_code == 200:
        file_name = os.path.join(os.getcwd(),
                                 response.headers['X-Sendfile'])

        with open(file_name, 'wb') as fp:
            fp.write(response.content)
        return file_name
    else:
        return response


def action_upload(url_base, sender_key, btctx_api, file, file_role):
    """
    Core method of the METATOOL API which uploads local file to the server.
    Max size of file is determined by the server. In the most of cases it is
    restricted by the 128 MB.
    Will return the response object with information about the server-error
    when such has occurred.

    :param url_base:  (str) URL string which defines the server will be used.
    :param sender_key: (str) unique secret key which will be used for the
                        generating credentials required by the access to the
                        server.
    :param btctx_api:  instance of the BtcTxStore class from btctxstore module.
                        It will be used to generate credentials for server
                        access. (https://pypi.python.org/pypi/btctxstore/4.6.0)
    :param file:  file object opened in the 'rb' mode,
                        which will be uploaded to the server.
    :param file_role:  (str)  three numbers string which define future
                        behavior of the file on the server. See more about
                        it in the documentation.
    :return: response: (<class 'requests.models.Response'>) response instance.
    """
    files = {'file_data': file}
    data_hash = sha256(file.read()).hexdigest()
    file.seek(0)
    sender_address = btctx_api.get_address(sender_key)
    signature = btctx_api.sign_unicode(sender_key, data_hash)
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
    """
    It executes a request to the "Node" server and returns response object
    with json-string - the list of hashes of downloaded files.

    :param url_base: (str) URL string which defines the server
                        that will be used.
    :return: response object
    """
    response = requests.get(urljoin(url_base, '/api/files/'))
    return response


def action_info(url_base):
    """
    It executes a request to the "Node" server and returns response object
    with json-string - the information about server state.

    :param url_base: (str) URL string which defines the server
                        that will be used.
    """
    response = requests.get(urljoin(url_base, '/api/nodes/me/'))
    return response


def parse():
    """
    Set of the parsing logic for the METATOOL.
    It doesn't perform parsing, just fills the parser object with arguments.

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


def show_data(data):
    """
    Method used to show a data in the console.
    :param data: <response obj> / <str>
    :return: None
    """
    if isinstance(data, requests.Response):
        print(data.status_code)
        print(data.text)
    else:
        print(data)


def args_prepare(required_args, parsed_args):
    """

    :param required_args:
    :param parsed_args:
    :return:
    """
    prepared_args = {}
    args_base = dict(
        sender_key=BTCTX_API.create_key(),
        btctx_api=BTCTX_API,
    )
    for required_arg in required_args:
        try:
            prepared_args[required_arg] = getattr(parsed_args, required_arg)
        except AttributeError:
            prepared_args[required_arg] = args_base[required_arg]
    return prepared_args


def get_all_func_args(function):
    """
    It finds out all available arguments of the given function.
    :param function: function object to inspect.
    :return: <list object>: with names of all available arguments.
    """
    return function.__code__.co_varnames[:function.__code__.co_argcount]


def main():
    """
    METATOOL main logic.
    """
    redirect_error_status = (400, 404, 500, 503)
    if len(sys.argv) == 1:
        parse().print_help()
        return
    args = parse().parse_args()
    used_args = args_prepare(get_all_func_args(args.execute_case), args)

    # Get the url from the environment variable 
    # or from the "--url" parsed argument
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
    show_data(result)


if __name__ == '__main__':
    main()
