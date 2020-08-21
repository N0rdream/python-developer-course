О проекте
---------
Проект представляет из себя асинхронный http-сервер на базе модуля asyncio.  
Сервер осуществляет обработку GET и HEAD запросов.


Зависимости
-----------    
Для работы сервера требуется версия Python не ниже 3.6.


Работа с сервером
-----------------
Запуск сервера осуществляется посредством файла httpd.py.  
Задание настроек сервера осуществляется из командной строки при помощи специальных ключей.  
Некоторые из ключей имеют значение по умолчанию, которое допускается не указывать в явном виде.  
### -a  
Задает адрес сервера. Значение по умолчанию "0.0.0.0".     
  
### -p
Задает порт сервера. Значение по умолчанию "8000".      

### -r  
Задает директорию с контентом.  

### -w  
Задает количество worker'ов. Значение по умолчанию 2.  

### Пример запуска:
```
$ python3 httpd.py -a 127.0.0.1 -p 80 -r tests/httptest -w 4
```


Тестирование сервера
--------------------
Для запуска тестов предварительно необходимо запустить сервер на порту 80,
задав в качестве директрии "tests":
```
$ python3 httpd.py -a 127.0.0.1 -p 80 -r tests
```
Запуск тестов осуществляется командой:
```
$ python test.py
```

Результаты нагрузочного тестирования
------------------------------------
Количество worker'ов равно четырем.
```
Document Path:          /
Document Length:        18 bytes

Concurrency Level:      100
Time taken for tests:   2.581 seconds
Complete requests:      50000
Failed requests:        0
Non-2xx responses:      50000
Total transferred:      9300000 bytes
HTML transferred:       900000 bytes
Requests per second:    19374.66 [#/sec] (mean)
Time per request:       5.161 [ms] (mean)
Time per request:       0.052 [ms] (mean, across all concurrent requests)
Transfer rate:          3519.22 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    1   0.4      1       5
Processing:     0    4   3.1      3      30
Waiting:        0    4   3.1      3      28
Total:          1    5   3.1      4      31

Percentage of the requests served within a certain time (ms)
  50%      4
  66%      5
  75%      5
  80%      6
  90%      8
  95%     12
  98%     16
  99%     19
 100%     31 (longest request)

```
```
Document Path:          /wikipedia_russia.html
Document Length:        954824 bytes

Concurrency Level:      100
Time taken for tests:   25.580 seconds
Complete requests:      50000
Failed requests:        0
Total transferred:      47749450000 bytes
HTML transferred:       47741200000 bytes
Requests per second:    1954.66 [#/sec] (mean)
Time per request:       51.160 [ms] (mean)
Time per request:       0.512 [ms] (mean, across all concurrent requests)
Transfer rate:          1822927.53 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    1   0.9      0      17
Processing:     1   51  26.7     45     197
Waiting:        0   32  24.3     27     193
Total:          1   51  26.6     45     197
WARNING: The median and mean for the initial connection time are not within a normal deviation
        These results are probably not that reliable.

Percentage of the requests served within a certain time (ms)
  50%     45
  66%     57
  75%     66
  80%     72
  90%     88
  95%    102
  98%    119
  99%    132
 100%    197 (longest request)
 ```
