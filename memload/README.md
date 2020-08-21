#

Test results
-----------

Single (38 min, 28 sec)  
```
[2018.09.03 22:50:14] I Memc loader started with options: {'test': False, 'log': None, 'dry': False, 'pattern': '/home/nordream/projects/files/*.tsv.gz', 'idfa': '127.0.0.1:33013', 'gaid': '127.0.0.1:33014', 'adid': '127.0.0.1:33015', 'dvid': '127.0.0.1:33016'}
[2018.09.03 22:50:14] I Processing /home/nordream/projects/files/20170929000100.tsv.gz

[2018.09.03 23:03:04] I Acceptable error rate (0.0). Successfull load
[2018.09.03 23:03:04] I Processing /home/nordream/projects/files/20170929000200.tsv.gz

[2018.09.03 23:15:53] I Acceptable error rate (0.0). Successfull load
[2018.09.03 23:15:53] I Processing /home/nordream/projects/files/20170929000000.tsv.gz

[2018.09.03 23:28:42] I Acceptable error rate (0.0). Successfull load
```

Threads (29 min, 14 sec)  
```
[2018.09.03 22:00:08] I Memc loader started with options: {'log': None, 'dry': False, 'pattern': '/home/nordream/projects/files/*.tsv.gz', 'idfa': '127.0.0.1:33013', 'gaid': '127.0.0.1:33014', 'adid': '127.0.0.1:33015', 'dvid': '127.0.0.1:33016', 'w': 4}
[2018.09.03 22:00:08] I Processing /home/nordream/projects/files/20170929000000.tsv.gz

[2018.09.03 22:09:49] I Acceptable error rate (0.0). Successfull load
[2018.09.03 22:09:49] I Processing /home/nordream/projects/files/20170929000100.tsv.gz

[2018.09.03 22:19:34] I Acceptable error rate (0.0). Successfull load
[2018.09.03 22:19:34] I Processing /home/nordream/projects/files/20170929000200.tsv.gz

[2018.09.03 22:29:22] I Acceptable error rate (0.0). Successfull load
```

Threads and processes (6 min, 46 sec)  
```
[2018.09.03 22:38:29] I Memc loader started with options: {'log': None, 'dry': False, 'pattern': '/home/nordream/projects/files/*.tsv.gz', 'idfa': '127.0.0.1:33013', 'gaid': '127.0.0.1:33014', 'adid': '127.0.0.1:33015', 'dvid': '127.0.0.1:33016', 'w': 4}
[2018.09.03 22:38:29] I Processing /home/nordream/projects/files/20170929000100.tsv.gz
[2018.09.03 22:38:29] I Processing /home/nordream/projects/files/20170929000000.tsv.gz
[2018.09.03 22:38:29] I Processing /home/nordream/projects/files/20170929000200.tsv.gz

[2018.09.03 22:45:15] I Acceptable error rate (0.0). Successfull load
[2018.09.03 22:45:15] I Acceptable error rate (0.0). Successfull load
[2018.09.03 22:45:15] I Acceptable error rate (0.0). Successfull load
```
