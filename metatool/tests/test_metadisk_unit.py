import sys
import json
import os.path
import unittest

from metatool.metadisk import (action_audit, action_download, action_files, action_info,
                      action_upload, _show_data, set_up, main)

if sys.version_info.major == 3:
    from io import StringIO
    from unittest.mock import patch, MagicMock, mock_open, Mock
else:
    from io import BytesIO as StringIO
    from mock import patch, MagicMock, mock_open, Mock


class MetadiskTest(unittest.TestCase):

    def test__show_data(self):
        test_response = Mock()
        test_response.status_code = 'status code string'
        test_response.text = 'status text string'
        print_out = StringIO()
        sys.stdout = print_out
        _show_data(test_response)
        sys.stdout = sys.__stdout__
        print_out.seek(0)
        self.assertEqual(
            print_out.read(),
            test_response.status_code + '\n' + test_response.text + '\n',
            'problem with printing out data in console'
        )
        print_out.close()


if __name__ == "__main__":
    unittest.main()