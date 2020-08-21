import unittest
from log_analyzer import (
    parse_log_record,
    parse_log_filename,
    get_parsed_log_records,
    process_parsed_records,
    get_last_log
)
from collections import defaultdict


class TestAnalyzer(unittest.TestCase):

    def test_parse_log_record(self):
        record_1 = (
            '1.99.174.176 '
            '3b81f63526fa8  '
            '- '
            '[29/Jun/2017:03:50:22 +0300] '
            '"GET /api/1/photogenic_banners/list/?server_name=WIN7RB4 HTTP/1.1" '
            '200 '
            '12 '
            '"-" '
            '"Python-urllib/2.7" '
            '"-" '
            '"1498697422-32900793-4708-9752770" '
            '"-" '
            '0.133'
        )
        result_1 = {
            'url': '/api/1/photogenic_banners/list/?server_name=WIN7RB4',
            'request_time': '0.133'
        }
        empty_record = ''
        record_2 = '1 1 1 1 "GET /test HTTP/1.1" 1 1 1 1 1 1 1 222.2'
        result_2 = {
            'url': '/test',
            'request_time': '222.2'
        }
        self.assertEqual(parse_log_record(record_1), result_1)
        self.assertIsNone(parse_log_record(empty_record))
        self.assertEqual(parse_log_record(record_2), result_2)

    def test_parse_log_filename(self):
        fname_gzip = 'nginx-access-ui.log-20180103.gz'
        fname_plain = 'nginx-access-ui.log-20180122'
        fname_empty = ''
        fname_bad = 'nginx-access-ui.log-201802222'
        result_gzip = {'date': '20180103'}
        result_plain = {'date': '20180122'}
        self.assertEqual(parse_log_filename(fname_gzip), result_gzip)
        self.assertEqual(parse_log_filename(fname_plain), result_plain)
        self.assertIsNone(parse_log_filename(fname_empty))
        self.assertIsNone(parse_log_filename(fname_bad))

    def test_get_parsed_log_records(self):
        records = [
            '- - - - "GET /test/1 HTTP/1.1" - - - - - - - 1.0',
            '- - - - "GET /test/2 HTTP/1.1" - - - - - - - 2.0',
            '- - - - "GET /test/2 HTTP/1.1" - - - - - - - 2.0',
            '- - - - "GET /test/3 HTTP/1.1" - - - - - - - 3.0',
            '- - - - "GET /test/3 HTTP/1.1" - - - - - - - 3.0',
            '- - - - "GET /test/3 HTTP/1.1" - - - - - - - 3.0',
            '- - - - "GET /test/4 HTTP/111" - - - - - - - 7.0',
            '- - - - "GET /test/4 WSGI/1.1" - - - - - - - 8.0',
            '- - - - "GOT /test/4 HTTP/1.1" - - - - - - - 9.0',
            '- - - - "GET /test/4 HTTP/1.1" - - - - - - - ten'
        ]
        result = defaultdict(list)
        result['/test/1'] = [1.0]
        result['/test/2'] = [2.0, 2.0]
        result['/test/3'] = [3.0, 3.0, 3.0]
        self.assertEqual(get_parsed_log_records(records), (result, 10, 4))
        with self.assertRaises(Exception):
            records = get_parsed_log_records(records, fails_perc=10)

    def test_process_parsed_records(self):
        records = {
            '/1': [1, 1, 1, 1],
            '/2': [2, 2, 2, 2, 2, 2]
        }
        result = [{
            'url': '/1',
            'count': 4,
            'count_perc': 40.0,
            'time_sum': 4,
            'time_perc': 25.0,
            'time_avg': 1.0,
            'time_max': 1,
            'time_med': 1.0
        }, {
            'url': '/2',
            'count': 6,
            'count_perc': 60.0,
            'time_sum': 12,
            'time_perc': 75.0,
            'time_avg': 2.0,
            'time_max': 2,
            'time_med': 2.0
        }]
        self.assertEqual(process_parsed_records(records), result)

    def test_get_last_log(self):
        result = ('nginx-access-ui.log-20180202.gz', '20180202')
        self.assertEqual(get_last_log('../test_data'), result)
