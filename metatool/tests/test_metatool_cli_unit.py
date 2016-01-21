from __future__ import print_function
import os
import sys
import unittest
from argparse import Namespace

from requests.models import Response

from metatool.cli import (show_data, parse, get_all_func_args, args_prepare,
                          main, CORE_NODES_URL)
from metatool import core

if sys.version_info.major == 3:
    from io import StringIO
    from unittest.mock import patch, Mock, call, mock_open
else:
    from io import BytesIO as StringIO
    from mock import patch, Mock, call, mock_open


class TestCliShowDataFunction(unittest.TestCase):
    """
    Test case of the metatool.__main__.show_data() function.
    """

    def test_show_data_string_type(self):
        test_string = 'test string value'
        expected_printed_string = test_string + '\n'
        with patch('sys.stdout', new_callable=StringIO) as mock_print:
            show_data(test_string)
            real_printed_string = mock_print.getvalue()
        self.assertEqual(
            real_printed_string,
            expected_printed_string,
            'problem with printing out str type in the "show_data" method!'
        )

    def test_show_data_response_type(self):
        attrs = dict(text='text string', status_code='status code string')
        mock_response = Mock(
            __class__=Response,
            **attrs
        )
        expected_printed_string = '{status_code}\n{text}\n'.format(**attrs)
        with patch('sys.stdout', new_callable=StringIO) as mock_print:
            show_data(mock_response)
            real_printed_string = mock_print.getvalue()
        self.assertEqual(
            expected_printed_string,
            real_printed_string,
            'unexpected set of print() calls in the "show_data" method!'
        )


class TestCliParseFunction(unittest.TestCase):
    """
    Test case of the metatool.__main__.parse() function.
    """
    def test_url_argument(self):
        """
        Test of presence and correct processing of the `--url` argument,
        inherited by all subparsers.
        """
        actions = (
            'audit FILE_HASH SEED',
            'download FILE_HASH',
            'upload {}'.format(os.path.abspath(__file__)),
            'files',
            'info',
        )
        # get `builtins` module name with respect to python version
        builtin_module_names = ('', '', '__builtin__', 'builtins')
        version_name = builtin_module_names[sys.version_info.major]

        with patch('{}.open'.format(version_name), mock_open(), create=False):
            for action in actions:
                # testing of parsing "url_base" value by default
                args_default = parse().parse_args('{}'.format(action).split())
                self.assertIsNone(args_default.url_base)

                # testing of parsing given "url_base" value
                args_passed_url = parse().parse_args(
                        '{} --url TEST_URL_STR'.format(action).split()
                )
                self.assertEqual(args_passed_url.url_base, 'TEST_URL_STR')

    def test_audit_argument(self):
        # testing of raising exception when required arguments are not given
        with patch('sys.stderr', new_callable=StringIO):
            with self.assertRaises(SystemExit):
                parse().parse_args('audit'.split())

        # testing of correct parse of all given arguments
        args_list = 'audit FILE_HASH CHALLENGE_SEED'.split()
        expected_args_dict = {
            'execute_case': core.audit,
            'file_hash': args_list[1],
            'seed': args_list[2],
            'url_base': None
        }
        parsed_args = parse().parse_args(args_list)
        real_parsed_args_dict = dict(parsed_args._get_kwargs())
        self.assertDictEqual(
            real_parsed_args_dict,
            expected_args_dict
        )

    def test_download_arguments(self):
        """
        Test for all features of the `download` subparser.
        """
        # testing of raising exception when required arguments are not given
        with patch('sys.stderr', new_callable=StringIO):
            with self.assertRaises(SystemExit):
                parse().parse_args('download'.split())

        # test on correctly parsing only "file_hash" argument.
        # Expect correct default values of optional arguments.
        args_list = 'download FILE_HASH'.split()
        expected_args_dict = {
            'decryption_key': None,
            'execute_case': core.download,
            'file_hash': args_list[1],
            'link': False,
            'rename_file': None,
            'url_base': None
        }
        parsed_args = parse().parse_args(args_list)
        real_parsed_args_dict = dict(parsed_args._get_kwargs())
        self.assertDictEqual(
            real_parsed_args_dict,
            expected_args_dict
        )

        # test on correctly parsing of full set of available arguments
        args_list = 'download FILE_HASH ' \
                    '--decryption_key TEST_DECRYPTION_KEY ' \
                    '--rename_file TEST_RENAME_FILE ' \
                    '--link'.split()
        expected_args_dict = {
            'file_hash': args_list[1],
            'decryption_key': args_list[3],
            'rename_file': args_list[5],
            'link': True,
            'execute_case': core.download,
            'url_base': None
        }
        parsed_args = parse().parse_args(args_list)
        real_parsed_args_dict = dict(parsed_args._get_kwargs())
        self.assertDictEqual(
            real_parsed_args_dict,
            expected_args_dict
        )

    def test_upload_arguments(self):
        """

        """
        # Test fixture
        full_file_path = os.path.join(os.path.dirname(__file__),
                                      'temporary_test_file')
        self.addCleanup(os.unlink, full_file_path)
        # Testing of raising exception when required arguments are not given
        with patch('sys.stderr', new_callable=StringIO):
            with self.assertRaises(SystemExit):
                parse().parse_args('upload'.split())

        # Test to the right opening file logic
        test_file_content = [b'test data 1', b'test data 2']
        with open(full_file_path, 'wb') as temp_file:
            parsed_args = parse().parse_args(['upload', full_file_path])
            temp_file.write(test_file_content[0])
            temp_file.flush()
            read_data = [parsed_args.file.read(), ]
            temp_file.seek(0)
            temp_file.truncate()
            temp_file.write(test_file_content[1])
            temp_file.flush()
            parsed_args.file.seek(0)
            read_data.append(parsed_args.file.read())
            parsed_args.file.close()
        self.assertListEqual(read_data, test_file_content)
        self.assertEqual(parsed_args.file.mode, 'rb')

        # Test on correctly parsing only "file" argument.
        # Expect correct default values of optional arguments.
        args_list = 'upload {}'.format(full_file_path).split()
        parsed_args = parse().parse_args(args_list)
        real_parsed_args_dict = dict(parsed_args._get_kwargs())
        expected_args_dict = {
            'file': parsed_args.file,
            'file_role': '001',
            'url_base': None,
            'execute_case': core.upload,
        }
        self.assertDictEqual(
            real_parsed_args_dict,
            expected_args_dict,
        )
        parsed_args.file.close()

        # test on correctly parsing of full set of available arguments
        args_list = 'upload {} ' \
                    '--url TEST_URL ' \
                    '--file_role TEST_FILE_ROLE'.format(full_file_path).split()
        parsed_args = parse().parse_args(args_list)
        real_parsed_args_dict = dict(parsed_args._get_kwargs())
        expected_args_dict = {
            'file': parsed_args.file,
            'file_role': args_list[5],
            'url_base': args_list[3],
            'execute_case': core.upload,
        }
        self.assertDictEqual(
            real_parsed_args_dict,
            expected_args_dict
        )
        parsed_args.file.close()

        # test "-r" optional argument
        args_list = 'upload {} ' \
                    '-r TEST_FILE_ROLE'.format(full_file_path).split()
        parsed_args = parse().parse_args(args_list)
        self.assertEqual(parsed_args.file_role, args_list[3])
        parsed_args.file.close()

    def test_info_argument(self):
        """
        Test of parsing appropriate default "core function".
        """
        parsed_args = parse().parse_args('info'.split())
        self.assertEqual(parsed_args.execute_case, core.info)

    def test_files_argument(self):
        # test of parsing appropriate default "core function"
        parsed_args = parse().parse_args('files'.split())
        self.assertEqual(parsed_args.execute_case, core.files)


class TestCliArgumentsPreparation(unittest.TestCase):
    def test_get_all_func_args(self):
        """
        Test of accurate discovery of required arguments of the function.
        """
        expected_args_set = ('arg_1', 'arg_2', 'arg_3')

        self.assertTupleEqual(
            get_all_func_args(lambda arg_1, arg_2, arg_3=True: None),
            expected_args_set,
            '"get_all_func_args" must return tuple like "expected_args_set" !'
        )

        # definition of the tested function
        def test_function(one, two=True, *args, **kwargs):
            local_variable = None
        expected_args_set = ('one', 'two')
        self.assertTupleEqual(
            get_all_func_args(test_function),
            expected_args_set,
            '"get_all_func_args" must return tuple like "expected_args_set" !'
        )

    @patch('metatool.cli.BtcTxStore')
    def test_args_prepare(self, mock_btctx_store):
        """
        Test on accurate setting-up all omitted required arguments
        to the core function.
        """
        mock_btctx_api = mock_btctx_store.return_value
        mock_btctx_api.create_key.return_value = 'TEST_SENDER_KEY'
        # testing for minimal providing arguments
        expected_args_dict = dict(
            one='TEST 1',
            two='TEST 2'
        )
        given_required_names = ['one', 'two']
        given_namespace = Namespace(
            one='TEST 1',
            two='TEST 2',
            three='TEST 3'
        )
        self.assertDictEqual(
            args_prepare(given_required_names, given_namespace),
            expected_args_dict,
            "Should provide only `one` and `two` arguments"
        )

        # test of max providing omitted arguments
        expected_args_dict['sender_key'] = 'TEST_SENDER_KEY'
        expected_args_dict['btctx_api'] = mock_btctx_api
        given_required_names += ['sender_key', 'btctx_api']

        self.assertDictEqual(
            args_prepare(given_required_names, given_namespace),
            expected_args_dict,
            "The `args_prepare()` should provide the full set of arguments!"
        )


class TestCliStarter(unittest.TestCase):

    @staticmethod
    def sys_stdout_help_run(tested_callable, etalon_callable, *args):
        """
        It's run passed callable and return their intercepted print-out.
        :note: While the running passed callable SystemExit is excepted,
        like normal exit for providing the help information.

        :param tested_callable: callable that may print help info
        :param etalon_callable: callable for the desired print-out
        :param args: argumets needed to be passed to the etalon callable
        :return: tuple of strings with first tested print and the second
        expected print
        """
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            # get tested result
            try:
                tested_callable()
            except SystemExit:
                pass
            mock_stdout.seek(0)
            tested_result = mock_stdout.read()
            # get etalon result
            mock_stdout.seek(0)
            mock_stdout.truncate()
            try:
                etalon_callable(*args)
            except SystemExit:
                pass
            mock_stdout.seek(0)
            etalon_result = mock_stdout.read()
        return tested_result, etalon_result

    def test_subtest_through_all_help_info(self):
        """
        Set of tests for providing the help information for all of terminal
        commands.
        """
        # Tuple of tuples with subtest's variant of terminal's command. The
        # first list is tested `sys.argv` value and second list is arguments
        # for the `parse().parse_args()` used like the etalon call result.
        tests_set = (
            (['', ], ['--help', ]),
            (['', '-h'], ['-h', ]),
            (['', '--help'], ['--help']),
            (['', 'info', '-h'], ['info', '-h']),
            (['', 'files', '-h'], ['files', '-h']),
            (['', 'download', '-h'], ['download', '-h']),
            (['', 'audit', '-h'], ['audit', '-h']),
            (['', 'upload', '-h'], ['upload', '-h']),
            (['', 'info', '--help'], ['info', '--help']),
            (['', 'files', '--help'], ['files', '--help']),
            (['', 'download', '--help'], ['download', '--help']),
            (['', 'audit', '--help'], ['audit', '--help']),
            (['', 'upload', '--help'], ['upload', '--help']),
        )

        for i, test_ in enumerate(tests_set, start=1):
            with patch('metatool.cli.sys.argv', test_[0]):
                main_print_info_help, manual_print_info_help = \
                    self.sys_stdout_help_run(
                        main,
                        parse().parse_args,
                        *test_[1:]
                    )
                self.assertEqual(
                    main_print_info_help,
                    manual_print_info_help,
                    'Unexpected result of the help printout with the '
                    'sys.argv={}'.format(test_[0])
                )

    @patch('requests.get', side_effect=SystemExit)
    def test_url_env_providing(self, mock_requests_get):
        """
        Test to getting the `url_base` argument from the environment variable
        `MEATADISKSERVER` if it's set.
        :param mock_requests_get: mocked argument provided by the `@patch()`
        """
        with patch('os.getenv', Mock(return_value='http://env.var.com')):
            with patch('sys.argv', ['', 'info']):
                try:
                    main()
                except SystemExit:
                    pass
                self.assertEqual(
                    mock_requests_get.call_args_list,
                    [call('http://env.var.com/api/nodes/me/')],
                    "Request should use the http://env.var.com address"
                )

    @patch('requests.get')
    def test_url_default_providing(self, mock_requests_get):
        """
        Test on default using the `url_base` argument from the CORE_NODES_URL
        list.
        :param mock_requests_get: auto-provided by the `@patch()` mocked arg
        """
        mock_response = mock_requests_get.return_value
        mock_response.status_code = 500
        expected_calls = [
            call('{}api/nodes/me/'.format(url)) for url in CORE_NODES_URL
        ]
        with patch('os.getenv', Mock(return_value=None)):
            with patch('metatool.cli.show_data'):
                with patch('sys.argv', ['', 'info']):
                    main()
        self.assertEqual(
            mock_requests_get.call_args_list,
            expected_calls,
            "Must be called in the order of `CORE_NODES_URL` list items"
        )

    @patch('requests.get', side_effect=SystemExit)
    def test_url_parser_providing(self, mock_requests_get):
        """
        Test on priority of using the `--url` provided in the terminal.
        :param mock_requests_get: auto-provided by the `@patch()` mocked arg
        """
        with patch('os.getenv', Mock(return_value='http://spam.eggs')):
            with patch('sys.argv', ['', 'info', '--url', 'http://test.url']):
                try:
                    main()
                except SystemExit:
                    pass
                self.assertEqual(
                    mock_requests_get.call_args_list,
                    [call('http://test.url/api/nodes/me/')],
                    "Request must be sent to the http://test.url/api/nodes/me/"
                )

    @staticmethod
    @patch('metatool.cli.parse')
    @patch('metatool.cli.show_data')
    @patch('metatool.cli.get_all_func_args', Mock(return_value=['url_base', ]))
    def walk_through_addresses(exit_point_result, mock_show_data, mock_parse):
        """
        This is the static method for the testing the metatool.cli.main()
        function to walking through the list of addresses.
        It forges the process of walking through default addresses until
        the acceptable result will be returned from the core function call, or
        all addresses will be used.
        It returns the list of calls of a core function, expected call-list,
        and show_data call-list in the course of executing the main() function.

        :param exit_point_result: return-value of the `core_func()` that should
            stop the walking
        :type exit_point_result: requests.models.Response object
        :type exit_point_result: string object

        :param mock_show_data: auto-provided by the `@patch()` mocked arg
        :param mock_parse: auto-provided by the `@patch()` mocked arg

        :returns: tuple of lists with calls of mocked objects to make assertion
        :rtype: tuple of lists
        """
        bad_response_result = Mock(__class__=Response, status_code=500)
        # Set up the order of the core function call's results.
        core_func = Mock(
                side_effect=[bad_response_result, bad_response_result,
                             exit_point_result, bad_response_result]
        )
        # mocking the parsing logic
        parser = mock_parse.return_value
        parser.parse_args.return_value = Namespace(execute_case=core_func,
                                                   url_base=None)
        # Mocking the list of default URL-addresses.
        # Walking should retrieve an acceptable result on the third address.
        url_list = ['first.fail.url', 'second.fail.url',
                    'third.success.stop.url', 'forth.unreached.url']
        with patch('os.getenv', Mock(return_value=None)):
            with patch('metatool.cli.CORE_NODES_URL', url_list):
                with patch('sys.argv', ['', '']):
                    main()
        # Preparing the return data
        tested_core_func_calls = core_func.call_args_list
        expected_core_func_calls = [call(url_base=url) for url in url_list[:3]]
        show_data_calls = mock_show_data.call_args_list

        return (tested_core_func_calls, expected_core_func_calls,
                show_data_calls)

    def test_stop_on_success_response(self):
        """
        Test the walking through the URL-addresses until the successful
        response will be occurred.
        """
        success_response = Mock(__class__=Response, status_code=200)
        # Getting the calls of a core function during the walking process
        real_calls, expected_calls, show_data_calls = \
            self.walk_through_addresses(success_response)
        self.assertListEqual(
            real_calls,
            expected_calls,
            "List must be called three times with expected URL-addresses!"
        )
        self.assertListEqual(
            show_data_calls,
            [call(success_response)],
            'the show_data() obj must be called once with `success_response` '
            'object!'
        )

    def test_stop_on_the_string_return(self):
        """
        Test of walking through the URL-addresses until the string object
        will be returned from a core function.
        """
        success_response = "string data, when the file downloaded successful"
        # Getting the calls of a core function during the walking process
        real_calls, expected_calls, show_data_calls = \
            self.walk_through_addresses(success_response)
        self.assertListEqual(
            real_calls,
            expected_calls,
            "List must be called three times with expected URL-addresses!"
        )
        self.assertListEqual(
            show_data_calls,
            [call(success_response)],
            'the show_data() obj must be called once with `success_response` '
            'object!'
        )