О проекте
---------
Проект представляет из себя асинхронный http-сервер на базе модуля asyncio.  
Сервер осуществляет обработку GET и HEAD запросов.


Зависимости
-----------    
Для работы сервера требуется версия Python не ниже 3.6.

```


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
Задает количество worker'ов. Значение по умолчанию 4.  

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
Time taken for tests:   4.516 seconds
Complete requests:      50000
Failed requests:        0
Non-2xx responses:      50000
Total transferred:      9300000 bytes
HTML transferred:       900000 bytes
Requests per second:    11071.64 [#/sec] (mean)
Time per request:       9.032 [ms] (mean)
Time per request:       0.090 [ms] (mean, across all concurrent requests)
Transfer rate:          2011.06 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    1   0.8      1       6
Processing:     0    8   4.1      7      52
Waiting:        0    7   4.0      7      51
Total:          0    9   4.1      8      53

Percentage of the requests served within a certain time (ms)
  50%      8
  66%     10
  75%     11
  80%     12
  90%     14
  95%     15
  98%     18
  99%     20
 100%     53 (longest request)
```
```
Document Path:          /wikipedia_russia.html
Document Length:        954824 bytes

Concurrency Level:      100
Time taken for tests:   29.876 seconds
Complete requests:      50000
Failed requests:        0
Total transferred:      47749450292 bytes
HTML transferred:       47741200000 bytes
Requests per second:    1673.60 [#/sec] (mean)
Time per request:       59.751 [ms] (mean)
Time per request:       0.598 [ms] (mean, across all concurrent requests)
Transfer rate:          1560814.08 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    1   0.8      1      22
Processing:     3   59  24.3     58     155
Waiting:        0   27  20.4     23     134
Total:          3   60  24.2     59     155

Percentage of the requests served within a certain time (ms)
  50%     59
  66%     68
  75%     74
  80%     79
  90%     93
  95%    104
  98%    116
  99%    123
 100%    155 (longest request)
 ```