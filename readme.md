# GeoNames RestAPI

### [GitHub Repos](https://github.com/klekks/InfotecsTestTask)

Тестовое задание для стажера на позицию «Программист на языке Python» Infotecs

На основе базы данных [GeoNames](http://download.geonames.org) создан сервис, который:
* Принимает geonameid и возвращает информацию о городе.
* Осуществляет постраничную пагинацию набора данных.
* Принимает названия двух городов и возвращает информацию о них и дополнительные сведения: какой город расположен севернее, какая часовая разница между населенными пунктами.
* По части названия города возвращает возможные варианты продолжений.

*Что соответствует всем основным и дополнительным пунктам технического задания*

Запуск осуществляется командой `python3 script.py`

При запуске проверяется наличие библиотеки transliteration, в случае, если её не удается обнаружить, она устанавливается с помощью pip3.

Далее происходит чтение данных:
+ База городов читается из файла, указанного в settings.py (CITIES_FILE, по умолчанию 'RU.txt')
+ База временнЫх зон читается из файла, указанного в settings.py (TIMEZONES_FILE, нужный файл приложен и стоит по умолчанию)


~~База данных о городах подвергается фильтрации, так как не каждый элемент [базы](http://download.geonames.org/export/dump/RU.zip) в действительности является населенным пунктом.~~

![#f03c15](https://via.placeholder.com/15/f03c15/000000?text=+) 

***В ТЗ есть неясность: в описании задания говорится о географических объектах, а в описании методов речь идет о городах.***

***Ответы на возникшие вопросы предлагается задавать на [почту](practice@infotecs.ru), но, увы, все вопросы игнорируются.***

***Вопрос решен следующим образом: фильтрация поддерживается, и по умолчанию она включена.***
***Для выключения в конфигурационном файле settings.py переменной `CITIES_ONLY` присвойте значение `False`***

*Все допустимые настройки можно посмотреть в файле settings.py*

## Формат данных об объекте

|Имя параметра|Тип|Описание|
|:------:|:-------:|:-----------------:|
|geonameid|`int`|Уникальный идентификатор объекта|
|name|`str`|Имя объекта|
|asciiname|`str`|Имя в кодировки ascii|
|alternatenames|`list[str]`|Массив альтернативных имен объекта|
|latitude|`float`|Географическая широта|
|longitude|`float`|Географическая долгота|
|feature_class|`char (str)`|Тип объекта ('P' - для городов)|
|feature_code|`str`|[См. подробнее здесь](http://download.geonames.org/export/dump/readme.txt)|
|country_code|`str`|[См. подробнее здесь](http://download.geonames.org/export/dump/readme.txt)|
|cc2|`str`|[См. подробнее здесь](http://download.geonames.org/export/dump/readme.txt)|
|admin1_code|`str`|[См. подробнее здесь](http://download.geonames.org/export/dump/readme.txt)|
|admin2_code|`str`|[См. подробнее здесь](http://download.geonames.org/export/dump/readme.txt)|
|admin3_code|`str`|[См. подробнее здесь](http://download.geonames.org/export/dump/readme.txt)|
|admin4_code|`str`|[См. подробнее здесь](http://download.geonames.org/export/dump/readme.txt)|
|population|`str`|Население|
|elevation|`int`|[См. подробнее здесь](http://download.geonames.org/export/dump/readme.txt)|
|dem|`int`|[См. подробнее здесь](http://download.geonames.org/export/dump/readme.txt)|
|timezone|`str`|Имя временной зоны (напр. "Europe/Moscow")|
|modification_date|`str`| Время последнего изменения данных|
|_autotranslit_ru_name|`str`|Кириллическое имя, полученное автоматическим транслитератором (не надежно)|
|_ru_name|`list[str]`| Массив альтернативных кириллических названий объекта|

~~*Типы возвращаемых параметров можно изменить в файле settings.py (is not recommended)*~~

## Поддерживаемые методы
|Путь|Аргументы|Описание|
|:------:|:---------:|:-----------------:|
|`/get_by_id`|`geonameid`: int|Единственный параметр - уникальный идентификатор объекта. Возвращает полную информацию (см. таблицу выше) или ошибку|
|`/pagination`|`page`: int (default=1)<br/>`per_page`: int (default=25)|`page`: текущая показываемая страница<br/>`per_page`: количество элементов на странице (настройками ограничено сверху значением 50, можно изменить в settings.py)<br/>Возвращаемый JSON имеет параметры `count` - количество элементов и `data` - массив объектов. Объекты отсортированы по убыванию населения.|
|`/compare`|`first_city`: str<br/> `second_city`: str|Оба параметра -- полные русскоязычные имена городов.<br/>Возвращает параметры `first_city` и `second_city` -- объекты городов (или null), `to_the_north` со значением first_city или second_city (более северного города), `equal_timezone` -- булево значение, `time_difference` -- вещественная разница в часах между первым и вторым нас. пунктом (может быть отрицательным)|
|`/hint`|`part`: str<br/>`max_count`: int|`part` -- часть названия города, <br/>`max_count` -- максимальное количество предлагаемых вариантов (ограниченно значением 50, изменяемо в settings.py)<br/> Возвращает массив объектов вида ```{"name": "cityname", "geonameid": 123456}```|

## Примеры корректных GET-запросов

* `http://127.0.0.1/get_by_id?geonameid=498817`
* `http://127.0.0.1/pagination`
* `http://127.0.0.1/pagination?page=7&per_page=11`
* `http://127.0.0.1/compare?first_city=Москва&second_city=Санкт-Петербург`
* `http://127.0.0.1/compare?first_city=кАзАнЬ&second_city=уфа`
* `http://127.0.0.1/hint?part=Санкт&max_count=50`
* `http://127.0.0.1/hint?part=Са`
<hr/>


