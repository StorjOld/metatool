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
import os.path
import sys
import argparse

from btctxstore import BtcTxStore

# makes available to import package from the source directory
parent_dir = os.path.dirname(os.path.dirname(__file__))
if not parent_dir in sys.path:
    sys.path.insert(0, parent_dir)
import metatool

CORE_NODES_URL = ('http://node2.metadisk.org/', 'http://node3.metadisk.org/')
BTCTX_API = BtcTxStore(testnet=True, dryrun=True)


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
    parser_audit.set_defaults(execute_case=metatool.audit)

    # Create the parser for the "download" command.
    parser_download = subparsers.add_parser('download',
                                            help='define download purpose!')
    parser_download.add_argument('file_hash', type=str, help="file hash")
    parser_download.add_argument('--decryption_key', type=str,
                                 help="decryption key")
    parser_download.add_argument('--rename_file', type=str, help="rename file")
    parser_download.add_argument('--link', action='store_true',
                                 help='will return rust url for man. request')
    parser_download.set_defaults(execute_case=metatool.download)

    # create the parser for the "upload" command.
    parser_upload = subparsers.add_parser('upload',
                                          help='define upload purpose!')
    parser_upload.add_argument('file', type=argparse.FileType('rb'),
                               help="path to file")
    parser_upload.add_argument('-r', '--file_role', type=str, default='001',
                               help="set file role")
    parser_upload.set_defaults(execute_case=metatool.upload)

    # create the parser for the "files" command.
    parser_files = subparsers.add_parser('files', help='define files purpose!')
    parser_files.set_defaults(execute_case=metatool.files)

    # create the parser for the "info" command.
    parser_info = subparsers.add_parser('info', help='define info purpose!')
    parser_info.set_defaults(execute_case=metatool.info)

    # parse the commands
    return main_parser


def show_data(data):
    """
    Method used to show a data in the console.
    :param data: <response obj> / <str>
    :return: None
    """
    if isinstance(data, str):
        print(data)
    else:
        print(data.status_code)
        print(data.text)


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
