О проекте
---------
Проект представляет из себя асинхронный http-сервер на базе модуля asyncio.  
Сервер осуществляет обработку GET и HEAD запросов.


Зависимости
-----------    
Для работы сервера требуется версия Python не ниже 3.6.
Установку необходимых зависимостей можно осуществить, выполнив команду:
```
$ pip install -r requirements.txt
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

### Пример запуска:
```
$ python3 httpd.py -a 127.0.0.1 -p 80 -r tests/httptest
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
```
Document Path:          /
Document Length:        18 bytes

Concurrency Level:      100
Time taken for tests:   19.070 seconds
Complete requests:      50000
Failed requests:        0
Non-2xx responses:      50000
Total transferred:      9300000 bytes
HTML transferred:       900000 bytes
Requests per second:    2621.92 [#/sec] (mean)
Time per request:       38.140 [ms] (mean)
Time per request:       0.381 [ms] (mean, across all concurrent requests)
Transfer rate:          476.25 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    1   1.4      0      16
Processing:    10   37   7.2     36      84
Waiting:       10   37   7.3     35      84
Total:         10   38   6.7     36      84

Percentage of the requests served within a certain time (ms)
  50%     36
  66%     40
  75%     44
  80%     44
  90%     47
  95%     49
  98%     53
  99%     55
 100%     84 (longest request)
```
```
Document Path:          /splash.css
Document Length:        98620 bytes

Concurrency Level:      100
Time taken for tests:   61.861 seconds
Complete requests:      50000
Failed requests:        0
Total transferred:      4939150000 bytes
HTML transferred:       4931000000 bytes
Requests per second:    808.26 [#/sec] (mean)
Time per request:       123.722 [ms] (mean)
Time per request:       1.237 [ms] (mean, across all concurrent requests)
Transfer rate:          77971.42 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.3      0      10
Processing:    55  124  20.4    120     279
Waiting:       53  123  20.3    120     279
Total:         55  124  20.4    120     279

Percentage of the requests served within a certain time (ms)
  50%    120
  66%    127
  75%    134
  80%    138
  90%    150
  95%    161
  98%    177
  99%    188
 100%    279 (longest request)
 ```