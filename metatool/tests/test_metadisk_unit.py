import sys
import json
import os.path
import unittest

from metatool.metadisk import _show_data
from requests import Response

if sys.version_info.major == 3:
    from io import StringIO
    from unittest.mock import patch, MagicMock, mock_open, Mock
else:
    from io import BytesIO as StringIO
    from mock import patch, MagicMock, mock_open, Mock


class MetadiskTest(unittest.TestCase):

    def test__show_data_string_type(self):
        test_string_argument = 'status text string'
        print_out = StringIO()
        sys.stdout = print_out
        _show_data(test_string_argument)
        sys.stdout = sys.__stdout__
        print_out.seek(0)
        self.assertEqual(
            print_out.read(),
            test_string_argument + '\n',
            'problem with printing out str type in the "_show_data" method!'
        )
        print_out.close()


if __name__ == "__main__":
    unittest.main()