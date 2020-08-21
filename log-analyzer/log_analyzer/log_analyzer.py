import gzip
import os
import re
import sys
import argparse
import logging
import string
import json
import statistics
from collections import defaultdict, namedtuple
from datetime import datetime


DEFAULT_CONFIG = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "../../../test/reports",
    "LOG_DIR": "../../../test/logs",
    "ANALYZER_LOG": None,
    "TS_FILE": "../../../test/log.ts",
    "FAILS_PERC": 10
}

REGEXP_LOG_RECORD = re.compile(
    r'(?:POST|GET|HEAD|PUT|OPTIONS)\s+(?P<url>.+)\s+HTTP\/\d\.\d"\s.+\s'
    r'(?P<request_time>\d+\.\d+)$'
)

REGEXP_LOG_FILENAME = re.compile(
    r'nginx-access-ui\.log-(?P<date>\d{8})(\.gz|$)'
)


def parse_log_record(record):
    match = re.search(REGEXP_LOG_RECORD, record)
    if match:
        return match.groupdict()


def parse_log_filename(filename):
    match = re.match(REGEXP_LOG_FILENAME, filename)
    if match:
        return match.groupdict()


def get_records_from_log(path):
    log = gzip.open(path, 'rb') if path.endswith('.gz') else open(path, 'rb')
    for record in log:
        yield record.decode('utf-8')
    log.close()


def get_parsed_log_records(records, fails_perc=100):
    parsed_records = defaultdict(list)
    fails = 0
    for total, record in enumerate(records, start=1):
        parsed_record = parse_log_record(record)
        if parsed_record is not None:
            request_time = float(parsed_record['request_time'])
            parsed_records[parsed_record['url']].append(request_time)
        else:
            fails += 1
    if fails / total * 100 >= fails_perc:
        raise Exception('Invalid log: too many unparsed records.')
    Records = namedtuple('Records', ['data', 'total', 'fails'])
    return Records(data=parsed_records, total=total, fails=fails)


def process_parsed_records(records):
    result = []
    urls_total = sum(len(v) for _, v in records.items())
    req_time_total = sum(n for _, v in records.items() for n in v)
    for url, req_times in records.items():
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


def render_report(template_path, report_path, data):
    with open(template_path, 'r') as tf:
        source = tf.read()
    template = string.Template(source)
    report_data = template.safe_substitute(table_json=json.dumps(data))
    with open(report_path, 'w') as rf:
        rf.write(report_data)


def get_last_log(path):
    date = ''
    last_log_filename = ''
    for filename in os.listdir(path):
        if os.path.isfile(os.path.join(path, filename)):
            parsed_filename = parse_log_filename(filename)
            if parsed_filename is None:
                continue
            if parsed_filename['date'] > date:
                date = parsed_filename['date']
                last_log_filename = filename
    LastLog = namedtuple('LastLog', ['filename', 'date'])
    return LastLog(filename=last_log_filename, date=date)


def get_cmd_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='config.json',
                        help='Path to config file')
    return parser.parse_args()


def get_merged_config(default_config, external_config_path):
    config = default_config.copy()
    if os.path.exists(external_config_path):
        with open(external_config_path, 'r') as ext_cfg_data:
            try:
                external_config = json.load(ext_cfg_data)
            except json.decoder.JSONDecodeError:
                raise Exception('Invalid external config file.')
        config.update(external_config)
    return config


def create_ts_file(ts_file_path, report_file_path):
    ts = str(os.path.getmtime(report_file_path))
    with open(ts_file_path, 'w') as f:
        f.write(ts)


def make_report(report_data, size):
    report = sorted(report_data, key=lambda x: x['time_sum'], reverse=True)
    return report[:size]


def main(default_config):
    cmd_args = get_cmd_args()
    config = get_merged_config(default_config, cmd_args.config)

    logging.basicConfig(
        level=logging.INFO,
        filename=config['ANALYZER_LOG'],
        format='[%(asctime)s] %(levelname).1s %(message)s',
        datefmt='%Y.%m.%d %H:%M:%S'
    )

    if not os.path.exists(config['REPORT_DIR']):
        os.mkdir(config['REPORT_DIR'])

    last_log = get_last_log(config['LOG_DIR'])
    log_filename, date = last_log.filename, last_log.date
    if not log_filename:
        logging.info(f"Directory <{config['LOG_DIR']}> has no log files.")
        sys.exit(0)

    report_date = datetime.strptime(date, '%Y%m%d').strftime('%Y.%m.%d')
    report_filename = f'report-{report_date}.html'
    report_file_path = os.path.join(config['REPORT_DIR'], report_filename)
    if os.path.exists(report_file_path):
        if not os.path.exists(config['TS_FILE']):
            create_ts_file(config['TS_FILE'], report_file_path)
        logging.info(f'Report with date <{date}> already exists.')
        sys.exit(0)

    records = get_records_from_log(os.path.join(config['LOG_DIR'], log_filename))
    logging.info('Parsing started.')
    parsed_records = get_parsed_log_records(records, float(config['FAILS_PERC']))
    fin_msg = (
        'Parsing finished. '
        f'Parsed records: {parsed_records.total}, '
        f'unparsed records: {parsed_records.fails}.'
    )
    logging.info(fin_msg)
    report_data = process_parsed_records(parsed_records.data)
    report = make_report(report_data, int(config['REPORT_SIZE']))
    render_report('report_template.html', report_file_path, report)
    logging.info('Report created.')
    create_ts_file(config['TS_FILE'], report_file_path)
    logging.info('Ts-file created.')


if __name__ == "__main__":
    try:
        main(DEFAULT_CONFIG)
    except (Exception, KeyboardInterrupt):
        msg = 'Got exception on <main> function'
        logging.exception(msg)
        sys.exit(msg)
