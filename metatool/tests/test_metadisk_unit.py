from __future__ import print_function
import os
import sys
import unittest

from metatool.cli import show_data, parse, get_all_func_args, args_prepare

from metatool import core

if sys.version_info.major == 3:
    from io import StringIO
    from unittest import mock
else:
    from io import BytesIO as StringIO
    import mock


class TestMainShowDataFunction(unittest.TestCase):
    """
    Test case of the metatool.__main__.show_data() function.
    """

    def test_show_data_string_type(self):
        test_string = 'test string value'
        expected_printed_string = test_string + '\n'
        with mock.patch('sys.stdout', new_callable=StringIO) as mock_print:
            show_data(test_string)
            real_printed_string = mock_print.getvalue()
        self.assertEqual(
            real_printed_string,
            expected_printed_string,
            'problem with printing out str type in the "show_data" method!'
        )

    def test_show_data_response_type(self):
        attrs = dict(text='text string', status_code='status code string')
        mock_response = mock.Mock(**attrs)
        expected_printed_string = '{status_code}\n{text}\n'.format(**attrs)
        with mock.patch('sys.stdout', new_callable=StringIO) as mock_print:
            show_data(mock_response)
            real_printed_string = mock_print.getvalue()
        self.assertEqual(
            expected_printed_string,
            real_printed_string,
            'unexpected set of print() calls in the "show_data" method!'
        )


class TestMainParseFunction(unittest.TestCase):
    """
    Test case of the metatool.__main__.parse() function.
    """
    def test_url_argument(self):

        # testing of parsing "url_base" value by default
        args_default = parse().parse_args('info'.split())
        self.assertIsNone(args_default.url_base)

        # testing of parsing given "url_base" value
        args_passed_url = parse().parse_args('--url TEST_URL_STR info'.split())
        self.assertEqual(args_passed_url.url_base, 'TEST_URL_STR')

    def test_audit_argument(self):
        # testing of raising exception when required arguments are not given
        with mock.patch('sys.stderr', new_callable=StringIO):
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
        # testing of raising exception when required arguments are not given
        with mock.patch('sys.stderr', new_callable=StringIO):
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
        # Test fixture
        full_file_path = os.path.join(os.path.dirname(__file__),
                                      'temporary_test_file')

        self.addCleanup(os.unlink, full_file_path)
        # Testing of raising exception when required arguments are not given
        with mock.patch('sys.stderr', new_callable=StringIO):
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
            expected_args_dict
        )
        parsed_args.file.close()

        # test on correctly parsing of full set of available arguments
        args_list = '--url TEST_URL ' \
                    'upload {} ' \
                    '--file_role TEST_FILE_ROLE'.format(full_file_path).split()
        parsed_args = parse().parse_args(args_list)
        real_parsed_args_dict = dict(parsed_args._get_kwargs())
        expected_args_dict = {
            'file': parsed_args.file,
            'file_role': args_list[5],
            'url_base': args_list[1],
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
        # test of parsing appropriate default "core function"
        parsed_args = parse().parse_args('info'.split())
        self.assertEqual(parsed_args.execute_case, core.info)

    def test_files_argument(self):
        # test of parsing appropriate default "core function"
        parsed_args = parse().parse_args('files'.split())
        self.assertEqual(parsed_args.execute_case, core.files)


class TestMainArgumentsPreparation(unittest.TestCase):
    def test_get_all_func_args(self):
        # test of accurate discovery of required arguments of the function
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

    @mock.patch('metatool.cli.BtcTxStore')
    def test_args_prepare(self, mock_btctx_store):
        # test on accurate setting of omitted required arguments
        # to the core function
        mock_btctx_api = mock_btctx_store.return_value
        mock_btctx_api.create_key.return_value = 'TEST_SENDER_KEY'
        expected_args_dict = dict(
            one='TEST 1',
            two='TEST 2'
        )
        given_required_names = ['one', 'two']
        given_namespace = mock.Mock(
            one='TEST 1',
            two='TEST 2',
            three='TEST 3'
        )
        del given_namespace.sender_key
        del given_namespace.btctx_api
        self.assertDictEqual(
            args_prepare(given_required_names, given_namespace),
            expected_args_dict
        )
        expected_args_dict['sender_key'] = 'TEST_SENDER_KEY'
        expected_args_dict['btctx_api'] = mock_btctx_api
        given_required_names += ['sender_key', 'btctx_api']

        self.assertDictEqual(
            args_prepare(given_required_names, given_namespace),
            expected_args_dict,
            "don't work!!!!"
        )
