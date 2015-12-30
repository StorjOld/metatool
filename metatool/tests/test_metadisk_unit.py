from __future__ import print_function
import sys
import unittest

from metatool.__main__ import show_data

if sys.version_info.major == 3:
    from io import StringIO
    from unittest import mock
else:
    from io import BytesIO as StringIO
    import mock


class Test__main__module(unittest.TestCase):

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
