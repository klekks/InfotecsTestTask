import server

import settings
from settings import LOGGER as LOG

import re
from typing import Any, Callable


def load_data():
    LOG("Loading cities data.")
    load_cities()
    LOG("Loading timezones data.")
    load_timezones()


def load_cities():
    load_table_from_file(
        settings.CITIES_FILE,
        settings.CITIES_FORMAT,
        save_cities_data,
        is_suitable_city_data,
        extra_actions=[russianize_city_name]
    )
    represent_cities()


def load_timezones():
    load_table_from_file(
        settings.TIMEZONES_FILE,
        settings.TIMEZONE_FORMAT,
        save_timezones_data,
        is_suitable_timezone
    )


def load_table_from_file(file_name: str,
                         row_format: dict[str, Any],
                         save_function: Callable,
                         is_suitable: Callable[
                             [dict[str, Any]],
                             bool
                         ],
                         extra_actions: list[Callable[[dict], Any]] = ()
                         ):
    with open(file_name, "r", encoding="UTF-8") as inp:
        for line in inp.readlines():
            data = parse_data_row_to_dict(line, row_format)
            if is_suitable(data):
                for action in extra_actions:
                    action(data)

                save_function(data)


def parse_data_row_to_dict(row: str,
                           row_format: dict[str, Any] = settings.CITIES_FORMAT):
    data = dict()

    cell = row.replace("\n", "") \
        .split("\t")

    # row_format: dict, key -- name of table column, value -- type of column data
    try:
        for ind, (key, val_type) in enumerate(row_format.items()):
            data[key] = val_type(cell[ind] or val_type())
    except ValueError:
        raise \
            ValueError(f"Incorrect type of data was passed.\
                       \n\tExpected type: {val_type}       \
                       \n\tPassed type: {type(cell[ind])}  \
                       \n\tPassed value: {cell[ind]}")

    return data


def russianize_city_name(data):
    re_ru_name = r'([,|&](?P<name>[а-яА-ЯёЁ][а-яА-ЯёЁ\.\- ]+))'

    data["_autotranslit_ru_name"] = transliterate.translit(data["name"], 'ru')
    if (data["_autotranslit_ru_name"] + "ь") in data['alternatenames']:  # Казань, Тверь, Пермь и подобные кейсы
        data["_autotranslit_ru_name"] += "ь"

    try:
        data["_ru_names"] = list(
                                    set(
                                        [match[1] for match in list(
                                            re.findall(
                                                re_ru_name,
                                                "&" + data["alternatenames"]
                                            )
                                        )]
                                    )
                                )

        if len(data["_ru_names"]) == 1:  # немного нечестная подмена имени
            data["_autotranslit_ru_name"] = data["_ru_names"][0]

        if not data["_ru_names"]:  # если вдруг не удалось обнаружить кириллическое имя
            data["_ru_names"].append(data["_autotranslit_ru_name"])
            
        data["_ru_names"] = [name.lower() for name in data["_ru_names"]]
        # если сделать это при распаковке из re.findall, то _autotranslit_ru_name будет lowercase
    except IndexError:
        data["_ru_names"] = [data["_autotranslit_ru_name"], ]

    data["alternatenames"] = [name.strip() for name in data["alternatenames"].split(",")]


def is_suitable_city_data(obj):
    if settings.CITIES_ONLY:
        return obj["feature_class"] == "P"  # нам нужны только населенные пункты (2/3 of dataset)
    else:
        return True


def is_suitable_timezone(tz):
    try:
        return float(tz["GMT"]) or True
    except ValueError:
        return False


def represent_cities():
    settings.DATA.sort(
        key=lambda x: x["population"],  # по умолчанию города отсортированы по убыванию численности населения,
        reverse=True  # за счет этого не будет нужна сортировка для п. 3 основного задания
    )


def save_cities_data(data):
    settings.DATA.append(data)  # сохраняем в простой список городов
    settings.ID_DATA[data["geonameid"]] = data  # сохраняем по id (чтобы возвращать информацию по id за O(1))


def save_timezones_data(data):
    settings.TIMEZONES[data["TimeZoneId"]] = float(data["GMT"])  # {"timezone_name": GMT}


def install_package(package):
    LOG(f"Installing {package}")
    import pip
    if hasattr(pip, 'main'):
        pip.main(['install', package])
    else:
        pip._internal.main(['install', package])


def check_transliterate():
    try:
        import transliterate
    except ImportError:
        LOG("Module <<transliterate>> was not installed yet.")
        install_package("transliterate")


def update_autotranslit():
    from transliterate.base import registry
    from transliterate.contrib.languages.ru.translit_language_pack import RussianLanguagePack
    RussianLanguagePack.pre_processor_mapping.update(
        {
            "Ye": "Е",
            "ye": "е",
            "'ye": "ье",
            "Moscow": "Москва",
            "Saint Petersburg": "Санкт-Петербург",
            "Vy": "Вы",
            "vy": "вы",
            "iy": "ий",
        }
    )
    registry.register(RussianLanguagePack, force=True)


if __name__ == "__main__":
    check_transliterate()
    try:
        import transliterate
    except ImportError:
        raise ModuleNotFoundError("transliterate")

    update_autotranslit()

    LOG("Data is being read.")
    load_data()
    LOG("Data reading completed.")

    LOG(f"There are {len(settings.DATA)} cities.")
    LOG(f"There are {len(settings.TIMEZONES)} timezones.")

    LOG(f"Runserver on {settings.HOST}:{settings.PORT}")
    server.runserver()
