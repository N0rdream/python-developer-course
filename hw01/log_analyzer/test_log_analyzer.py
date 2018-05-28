import unittest
import log_analyzer
from collections import defaultdict

class TestAnalyzer(unittest.TestCase):

    def test_parse_log_data(self):
        
        s1 = (
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

        r1 = {
            'url': '/api/1/photogenic_banners/list/?server_name=WIN7RB4',
            'request_time': '0.133'
        }

        s2 = ''
        s3 = '1 1 1 1 "GET /test HTTP/1.1" 1 1 1 1 1 1 1 222.2'
        r3 = {
            'url': '/test',
            'request_time': '222.2'
        }

        self.assertEqual(log_analyzer.parse_log_data(s1), r1)
        self.assertIsNone(log_analyzer.parse_log_data(s2))
        self.assertEqual(log_analyzer.parse_log_data(s3), r3)


    def test_parse_log_filename(self):
        
        s1 = 'nginx-access-ui.log-20180103.gz'
        s2 = 'nginx-access-ui.log-20180122'
        s3 = ''
        s4 = 'nginx-access-ui.log-201802222'
        r1 = {'date': '20180103'}
        r2 = {'date': '20180122'}

        self.assertEqual(log_analyzer.parse_log_filename(s1), r1)
        self.assertEqual(log_analyzer.parse_log_filename(s2), r2)
        self.assertIsNone(log_analyzer.parse_log_filename(s3))
        self.assertIsNone(log_analyzer.parse_log_filename(s4))


    def test_get_parsed_data(self):
        
        data = [
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
        
        r1 = defaultdict(list)
        r1['/test/1'] = [1.0]
        r1['/test/2'] = [2.0, 2.0]
        r1['/test/3'] = [3.0, 3.0, 3.0]
        
        self.assertEqual(log_analyzer.get_parsed_data(data, 50), r1)
        with self.assertRaises(SystemExit):
            data = log_analyzer.get_parsed_data(data, 10)


    def test_process_data(self):

        data = {
            '/1': [1, 1, 1, 1],
            '/2': [2, 2, 2, 2, 2, 2]
        }
        
        r = [{
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

        self.assertEqual(log_analyzer.process_data(data), r)


    def test_get_last_log(self):

        r = ('test_data/logs/nginx-access-ui.log-20180228', '2018.02.28')
        self.assertEqual(log_analyzer.get_last_log('test_data/logs'), r)


    def test_get_merged_config(self):

        conf_def = {
            "REPORT_DIR": "reports",
            "LOG_DIR": "logs",
            "FAILS_PERC": 50
        }

        r = {
            "REPORT_DIR": "reports",
            "LOG_DIR": "test_logs",
            "FAILS_PERC": '1'
        } 

        cfp1 = 'test_data/test_config_1.ini'
        cfp2 = 'test_data/test_config_2.ini'
        cfp3 = 'test_data/test_config_3.ini'

        self.assertEqual(log_analyzer.get_merged_config(conf_def, cfp1), r)
        with self.assertRaises(SystemExit):
            c2 = log_analyzer.get_merged_config(conf_def, cfp2)
        with self.assertRaises(SystemExit):
            c3 = log_analyzer.get_merged_config(conf_def, cfp3)


