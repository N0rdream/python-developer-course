import gzip
import os
import re
import sys
import argparse
import configparser
import logging
import string
import json
import statistics
from collections import defaultdict


def parse_log_data(data):
    pattern = re.compile(
        r'(?:POST|GET|HEAD|PUT|OPTIONS)\s+(?P<url>.+)\s+HTTP\/\d\.\d"\s.+\s'
        r'(?P<request_time>\d+\.\d+)$'
    )
    match = re.search(pattern, data)
    if match:
        return match.groupdict()


def parse_log_filename(data):
    pattern = re.compile(r'nginx-access-ui\.log-(?P<date>\d{8})(\.gz|$)')
    match = re.search(pattern, data)
    if match:
        return match.groupdict()


def get_data_from_file(path):
    if path.endswith('.gz'):
        with gzip.open(path, 'rb') as f:
            for line in f:
                yield line.decode('utf-8')
    else:
        with open(path, 'r') as f:
            for line in f:
                yield line
    

def get_parsed_data(lines, fails_perc):
    data = defaultdict(list)
    fails = 0
    logging.info('Parsing started.')
    for total, line in enumerate(lines, start=1):
        parsed_line = parse_log_data(line)
        if parsed_line is not None:
            request_time = float(parsed_line['request_time'])
            data[parsed_line['url']].append(request_time)
        else:
            fails += 1
        if total % 100000 == 0:
            logging.info(f'{total} lines parsed.')
    if fails / total * 100 >= fails_perc:
        msg = 'Invalid log data: too many unparsed lines.'
        logging.error(msg)
        sys.exit(msg)
    logging.info(f'Parsing finished. Parsed lines: {total}, unparsed lines: {fails}')   
    return data


def process_data(data):
    result = []
    urls_total = sum(len(v) for k, v in data.items())
    req_time_total = sum(n for k, v in data.items() for n in v)
    for url, req_times in data.items():
        req_times.sort()
        url_number = len(req_times)
        time_sum = sum(req_times)
        result.append({
                'url': url,
                'count': url_number,
                'count_perc': round(url_number / urls_total * 100, 3),
                'time_sum': round(time_sum, 3),
                'time_perc': round(time_sum / req_time_total * 100, 3),
                'time_avg': round(time_sum / url_number, 3),
                'time_max': req_times[-1],
                'time_med': round(statistics.median(req_times), 3)
        })
    return result


def render_report(template_filepath, report_filepath, data):
    with open(template_filepath, 'r') as tf:
        source = tf.read()
    template = string.Template(source)
    report_data = template.safe_substitute(table_json=json.dumps(data))
    with open(report_filepath, 'w') as rf:
        for line in report_data:
            rf.write(line)


def get_filenames_from_dir(dir_path):
    filenames = []
    for name in os.listdir(dir_path):
        if os.path.isfile(os.path.join(dir_path, name)):
            filenames.append(name)
    if not filenames:
        logging.info(f'{dir_path} has no files')
        sys.exit(0)
    return filenames
    

def get_report_date(date):
    return '.'.join([date[:4], date[4:6], date[6:]])


def get_last_log(log_dir):
    date = ''
    actual_filename = ''
    for filename in get_filenames_from_dir(log_dir):
        data = parse_log_filename(filename)
        if data is None:
            continue
        if data['date'] > date:
            date = data['date']
            actual_filename = filename
    if not actual_filename:
        logging.info(f'{log_dir} has no log files')
        sys.exit(0)
    return os.path.join(log_dir, actual_filename), get_report_date(date)


def get_config_path():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='config.ini',
                        help='Path to config file')
    return parser.parse_args().config


def get_merged_config(config_default, config_file_path):
    config_file = configparser.ConfigParser()
    config_file.optionxform = str
    config_file.read(config_file_path)
    try:
        main_config = config_file['MAIN']
    except KeyError:
        sys.exit('Invalid config file.')
    for k in main_config:
        if k in config_default:
            config_default[k] = main_config[k]
    return config_default


def create_ts_file(ts_file_path, report_file_path):
    ts = os.path.getmtime(report_file_path)
    with open(ts_file_path, 'w') as f:
        f.write(str(ts))
    logging.info('Ts-file created.')


def make_report(report_data, size):
    report = sorted(report_data, key=lambda x: x['time_sum'], reverse=True)
    return report[:size]


def main(config_default):
    try:
        config_file_path = get_config_path()
        config = get_merged_config(config_default, config_file_path)
        logging.basicConfig(
            level=logging.INFO,
            filename=config['ANALYZER_LOG'],
            format='[%(asctime)s] %(levelname).1s %(message)s',
            datefmt='%Y.%m.%d %H:%M:%S'
        )
        log_file_path, date = get_last_log(config['LOG_DIR'])
        report_file_path = os.path.join(config['REPORT_DIR'], f'report-{date}.html')
        if os.path.exists(report_file_path):
            if not os.path.exists(config['TS_FILE']):
                create_ts_file(config['TS_FILE'], report_file_path)
            logging.info(f'Report with date {date} already exists')
            sys.exit(0)
        data = get_data_from_file(log_file_path)
        parsed_data = get_parsed_data(data, float(config['FAILS_PERC']))
        report_data = process_data(parsed_data)
        report = make_report(report_data, int(config['REPORT_SIZE']))
        render_report('report_template.html', report_file_path, report)
        logging.info('Report created.')
        create_ts_file(config['TS_FILE'], report_file_path)
        
    except (Exception, KeyboardInterrupt) as e:
        msg = 'Got exception on main()'
        logging.exception(msg)
        sys.exit(msg)


if __name__ == "__main__":
    
    config_default = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "../../../data/hw01/reports",
    "LOG_DIR": "../../../data/hw01/logs",
    "ANALYZER_LOG": None,
    "TS_FILE": "../../../data/hw01/log.ts",
    "FAILS_PERC": 10
    }

    main(config_default)
























