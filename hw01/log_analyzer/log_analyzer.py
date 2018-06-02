import gzip
import os
import re
import sys
import argparse
import logging
import string
import json
import statistics
from collections import defaultdict
from datetime import datetime


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


def get_data_from_log(path):
    if path.endswith('.gz'):
        with gzip.open(path, 'rb') as f:
            for line in f:
                yield line.decode('utf-8')
    else:
        with open(path, 'r') as f:
            for line in f:
                yield line


def get_parsed_log_data(lines, fails_perc=100):
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
    logging.info(f'Finished. Parsed lines: {total}, unparsed lines: {fails}')
    return data


def process_data(data):
    result = []
    urls_total = sum(len(v) for _, v in data.items())
    req_time_total = sum(n for _, v in data.items() for n in v)
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


def render_report(template_path, report_path, data):
    with open(template_path, 'r') as tf:
        source = tf.read()
    template = string.Template(source)
    report_data = template.safe_substitute(table_json=json.dumps(data))
    with open(report_path, 'w') as rf:
        for line in report_data:
            rf.write(line)


def get_log_filenames(path):
    filenames = []
    for filename in os.listdir(path):
        if os.path.isfile(os.path.join(path, filename)):
            filenames.append(filename)
    return filenames


def get_report_date(date):
    try:
        dt = datetime.strptime(date, '%Y%m%d')
    except ValueError:
        return None
    return f"{dt.year}.{dt.strftime('%m')}.{dt.strftime('%d')}"


def get_last_log(filenames):
    date = ''
    last_log_filename = ''
    for filename in filenames:
        data = parse_log_filename(filename)
        if data is None:
            continue
        if data['date'] > date:
            date = data['date']
            last_log_filename = filename
    return last_log_filename, date


def get_external_config_path():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='config.json',
                        help='Path to config file')
    return parser.parse_args().config


def get_external_config(path):
    with open(path, 'r') as json_data:
        try:
            external_config = json.load(json_data)
        except json.decoder.JSONDecodeError:
            return None
    return external_config


def get_merged_config(def_cfg, ext_cfg):
    for k in ext_cfg:
        if k in def_cfg:
            def_cfg[k] = ext_cfg[k]
    return def_cfg


def create_ts_file(ts_file_path, report_file_path):
    ts = os.path.getmtime(report_file_path)
    with open(ts_file_path, 'w') as f:
        f.write(str(ts))


def make_report(report_data, size):
    report = sorted(report_data, key=lambda x: x['time_sum'], reverse=True)
    return report[:size]


def main(default_config):
    try:
        external_config_path = get_external_config_path()
        if not os.path.exists(external_config_path):
            config = default_config
        else:
            external_config = get_external_config(external_config_path)
            if external_config is None:
                sys.exit('Invalid external config file.')
            config = get_merged_config(default_config, external_config)

        logging.basicConfig(
            level=logging.INFO,
            filename=config['ANALYZER_LOG'],
            format='[%(asctime)s] %(levelname).1s %(message)s',
            datefmt='%Y.%m.%d %H:%M:%S'
        )

        log_dir_path = config['LOG_DIR']
        ts_file_path = config['TS_FILE']
        report_dir_path = config['REPORT_DIR']

        if not os.path.exists(report_dir_path):
            os.mkdir(report_dir_path)

        log_filenames = get_log_filenames(log_dir_path)
        if not log_filenames:
            logging.info(f'Directory <{log_dir_path}> has no files.')
            sys.exit(0)

        log_filename, date = get_last_log(log_filenames)
        if not log_filename:
            logging.info(f'Directory <{log_dir_path}> has no log files.')
            sys.exit(0)

        report_date = get_report_date(date)
        if report_date is None:
            logging.info(f'Invalid date in log filename: {date}.')
            sys.exit(0)

        report_filename = f'report-{report_date}.html'
        report_file_path = os.path.join(report_dir_path, report_filename)
        if os.path.exists(report_file_path):
            if not os.path.exists(ts_file_path):
                create_ts_file(ts_file_path, report_file_path)
            logging.info(f'Report with date <{date}> already exists.')
            sys.exit(0)

        log_data = get_data_from_log(os.path.join(log_dir_path, log_filename))
        parsed_data = get_parsed_log_data(log_data, float(config['FAILS_PERC']))
        report_data = process_data(parsed_data)
        report = make_report(report_data, int(config['REPORT_SIZE']))
        render_report('report_template.html', report_file_path, report)
        logging.info('Report created.')
        create_ts_file(ts_file_path, report_file_path)
        logging.info('Ts-file created.')

    except (Exception, KeyboardInterrupt):
        msg = 'Got exception on <main> function'
        logging.exception(msg)
        sys.exit(msg)


if __name__ == "__main__":

    default_config = {
        "REPORT_SIZE": 1000,
        "REPORT_DIR": "../../../test/reports",
        "LOG_DIR": "../../../test/logs",
        "ANALYZER_LOG": None,
        "TS_FILE": "../../../test/log.ts",
        "FAILS_PERC": 10
    }
    main(default_config)
