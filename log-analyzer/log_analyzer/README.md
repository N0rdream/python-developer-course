# Log_analyzer

About
-----
Log_analyzer - скрипт, предназначеннный для парсинга логов веб-сервера Nginx, их первичной обработки и генерации отчета по шаблону.

Dependencies & requirments
--------------------------
Log_analyzer has no dependencies other than the Python Standard Library.
Log_analyzer runs with Python 3.6+.

How to run
----------
Перед запуском скрипта необходимо задать следующие параметры:
```  
REPORT_SIZE     - количество url для отчета  
REPORT_DIR      - директория отчета  
LOG_DIR         - директория с логами Nginx  
ANALYZER_LOG    - путь до лога скрипта  
TS_FILE         - путь до файла, содержащего mtime сгенерированного отчета  
FAILS_PERC      - разрешенное количество записей лога Nginx, которые не удалось отпарсить (в процентах) 
``` 

Параметры можно задать через отдельный файл конфигурации в формате json:
```
{
	"FAILS_PERC": 20,
	"LOG_DIR": "test/logs",
	"TS_FILE": "test/log.ts"
}
```
Путь до файла конфигурации можно указать при запуске скрипта в командной строке через ключ --config:
```
python3 log_analyzer.py --config ../../../data/hw01/config.json
```
Незаданные параметры берутся из конфигурации по умолчанию из кода скрипта.

How to run tests
----------------
```
python3 -m unittest test_log_analyzer.py 
```