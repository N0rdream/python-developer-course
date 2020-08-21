import gzip
import sys
import glob
import logging
from optparse import OptionParser
import memcache
import collections
import appsinstalled_pb2
import os
import time

from queue import Queue
from threading import Thread
from multiprocessing import Process, Pool
from functools import partial


NORMAL_ERR_RATE = 0.01
QUEUE_MAXSIZE = 0
MEMCACHE_TIMEOUT = 1
RECONNECT_MAX_ATTEMPTS = 2
RECONNECT_DELAY = 1
AppsInstalled = collections.namedtuple("AppsInstalled", ["dev_type", "dev_id", "lat", "lon", "apps"])


def dot_rename(path):
    head, fn = os.path.split(path)
    os.rename(path, os.path.join(head, "." + fn))


class Uploader(Thread):

    def __init__(self, queue, addr, reconnect_max_attempts, reconnect_delay, dry_run=False):
        Thread.__init__(self, daemon=True)
        self.queue = queue
        self.addr = addr
        self.reconnect_max_attempts = reconnect_max_attempts
        self.reconnect_delay = reconnect_delay
        self.errors = 0
        self.dry_run = dry_run

    def insert_record_into_memcache(self, client, data):
        attempts = 0
        while True:
            resp = client.set(data['key'], data['val'].SerializeToString())
            if resp:
                break
            attempts += 1
            if attempts == self.reconnect_max_attempts:
                logging.error("Cannot write to memc %s." % (self.addr))
                self.errors += 1
                break
            time.sleep(self.reconnect_delay)

    def run(self):
        client = memcache.Client([self.addr], socket_timeout=MEMCACHE_TIMEOUT)
        while True:
            data = self.queue.get()
            try:
                if self.dry_run:
                    logging.debug("%s - %s -> %s" % (self.addr, data['key'], str(data['val']).replace("\n", " ")))
                else:
                    self.insert_record_into_memcache(client, data)
            except Exception as e:
                logging.exception("Cannot write to memc %s: %s" % (self.addr, e))
                self.errors += 1
            self.queue.task_done()


class Parser:

    def __init__(self, devices, filepath, queues):
        self.devices = devices
        self.filepath = filepath
        self.queues = queues
        self.errors = 0
        self.empty_lines = 0
        self.total = 0

    def create_data_for_memcached(self, appsinstalled):
        ua = appsinstalled_pb2.UserApps()
        ua.lat = appsinstalled.lat
        ua.lon = appsinstalled.lon
        key = "%s:%s" % (appsinstalled.dev_type, appsinstalled.dev_id)
        ua.apps.extend(appsinstalled.apps)
        return {'key': key, 'val': ua}

    def parse_appsinstalled(self, line):
        line_parts = line.decode().strip().split("\t")
        if len(line_parts) < 5:
            return
        dev_type, dev_id, lat, lon, raw_apps = line_parts
        if not dev_type or not dev_id:
            return
        try:
            apps = [int(a.strip()) for a in raw_apps.split(",")]
        except ValueError:
            apps = [int(a.strip()) for a in raw_apps.split(",") if a.isidigit()]
            logging.info("Not all user apps are digits: `%s`" % line)
        try:
            lat, lon = float(lat), float(lon)
        except ValueError:
            logging.info("Invalid geo coords: `%s`" % line)
        return AppsInstalled(dev_type, dev_id, lat, lon, apps)

    def parse(self):
        with gzip.open(self.filepath) as fd:
            for total, line in enumerate(fd, start=1):
                if not total % 100000:
                    logging.info(total)
                line = line.strip()
                if not line:
                    self.empty_lines += 1 
                    continue
                appsinstalled = self.parse_appsinstalled(line)
                if not appsinstalled:
                    self.errors += 1
                    continue
                memc_addr = self.devices.get(appsinstalled.dev_type)
                if not memc_addr:
                    logging.error("Unknow device type: %s" % appsinstalled.dev_type)
                    self.errors += 1
                    continue
                data = self.create_data_for_memcached(appsinstalled)
                self.queues[appsinstalled.dev_type].put(data)
            self.total = total
        

def main(devices, filepath, dry_run):

    queues = {}
    uploaders = []

    for d in devices:
        queues[d] = Queue(maxsize=QUEUE_MAXSIZE)
        u = Uploader(queues[d], devices[d], RECONNECT_MAX_ATTEMPTS, RECONNECT_DELAY, dry_run)
        uploaders.append(u)

    for u in uploaders:
        u.start()

    logging.info('Processing %s' % filepath)

    parser = Parser(devices, filepath, queues,)
    parser.parse()

    for _, q in queues.items():
        q.join()

    errors = sum(u.errors for u in uploaders) + parser.errors
    processed = parser.total - parser.empty_lines - errors

    if processed:
        err_rate = float(errors) / processed
        if err_rate < NORMAL_ERR_RATE:
            logging.info("Acceptable error rate (%s). Successfull load" % err_rate)
        else:
            logging.error("High error rate (%s > %s). Failed load" % (err_rate, NORMAL_ERR_RATE))

    dot_rename(filepath)

    
def run_all(opts, filepath):
    devices = {
        "idfa": opts.idfa,
        "gaid": opts.gaid,
        "adid": opts.adid,
        "dvid": opts.dvid,
    }
    try:
        main(devices, filepath, opts.dry)
    except Exception as e:
        logging.exception("Unexpected error: %s" % e)
        sys.exit(1)


def prototest():
    sample = "idfa\t1rfw452y52g2gq4g\t55.55\t42.42\t1423,43,567,3,7,23\ngaid\t7rfw452y52g2gq4g\t55.55\t42.42\t7423,424"
    for line in sample.splitlines():
        dev_type, dev_id, lat, lon, raw_apps = line.strip().split("\t")
        apps = [int(a) for a in raw_apps.split(",") if a.isdigit()]
        lat, lon = float(lat), float(lon)
        ua = appsinstalled_pb2.UserApps()
        ua.lat = lat
        ua.lon = lon
        ua.apps.extend(apps)
        packed = ua.SerializeToString()
        unpacked = appsinstalled_pb2.UserApps()
        unpacked.ParseFromString(packed)
        assert ua == unpacked


if __name__ == '__main__':
    op = OptionParser()
    op.add_option("-l", "--log", action="store", default=None)
    op.add_option("--dry", action="store_true", default=False)
    op.add_option("--pattern", action="store", default="/data/appsinstalled/*.tsv.gz")
    op.add_option("--idfa", action="store", default="127.0.0.1:33013")
    op.add_option("--gaid", action="store", default="127.0.0.1:33014")
    op.add_option("--adid", action="store", default="127.0.0.1:33015")
    op.add_option("--dvid", action="store", default="127.0.0.1:33016")
    op.add_option("-w", action="store", default=4)
    (opts, args) = op.parse_args()
    
    logging.basicConfig(filename=opts.log, level=logging.INFO if not opts.dry else logging.DEBUG,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    logging.info("Memc loader started with options: %s" % opts)

    # for p in sorted(glob.iglob(opts.pattern)):
    #     run_all(opts, p)

    func = partial(run_all, opts)   

    with Pool(opts.w) as p:
        p.map(func, sorted(glob.iglob(opts.pattern)))
