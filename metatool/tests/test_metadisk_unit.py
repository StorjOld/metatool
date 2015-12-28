import sys
import unittest

from metatool.__main__ import show_data

if sys.version_info.major == 3:
    from io import StringIO
else:
    from io import BytesIO as StringIO


class MetadiskTest(unittest.TestCase):

    def test__show_data_string_type(self):
        test_string_argument = 'status text string'
        print_out = StringIO()
        sys.stdout = print_out
        show_data(test_string_argument)
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