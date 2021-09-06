from http.server import SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Any
import json
import settings


class MyHttpHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
        url = urlparse(self.path)
        params = parse_qs(url.query)
        path = url.path

        try:
            if path == "/get_by_id":
                self.get_city_by_id(params)
            elif path == "/pagination":
                self.paginate(params)
            elif path == "/compare":
                self.compare(params)
            elif path == "/hint":
                self.hint(params)
            else:
                self.NOT_IMPLEMENTED({"status": "method not found"})
        except (ValueError, TypeError, NameError):
            self.BAD_REQUEST({"status": "invalid argument"})

    def paginate(self, params):
        current_page = max(  # min page number is 1
            get_query_param(params, "page", to_type=int, default=settings.DEFAULT_PAGE),
            1
        )
        cities_per_page = min(
            get_query_param(params, "per_page", to_type=int, default=settings.DEFAULT_PAGINATION_SIZE),
            settings.PAGINATION_LIMIT
        )

        pag_begin = (current_page - 1) * cities_per_page  # the page numbering starts from 1
        pag_end = current_page * cities_per_page

        data = settings.DATA[pag_begin: pag_end]

        self.SUCCESS({
            "count": len(data),
            "data": data
        })

    def compare(self, params):
        first_city_name = get_query_param(params, "first_city")
        second_city_name = get_query_param(params, "second_city")

        city1 = self.get_city_by_name(first_city_name)
        city2 = self.get_city_by_name(second_city_name)

        if city1 and city2:
            self.SUCCESS({
                "first_city": city1,
                "second_city": city2,
                "to_the_north": "first_city" if city1["latitude"] > city2["latitude"]
                else "second_city",
                "equal_timezone": True if city1["timezone"] == city2["timezone"]
                else False,
                "time_difference": settings.TIMEZONES[city1["timezone"]] - settings.TIMEZONES[city2["timezone"]]
            })
        else:
            self.NOT_FOUND({
                "status": "One of the cities was not found.",
                "first_city": city1 if city1 else None,
                "second_city": city2 if city2 else None
            })

    @staticmethod
    def get_city_by_name(city_name):
        try:
            return list(filter(
                lambda city: city_name.lower() in city["_ru_name"],
                settings.DATA
            ))[0]  # достаем город с совпадающим именем (города уже отсортированы по населению)
        except IndexError:
            return None  # если подходящего города нет, то None

    def get_city_by_id(self, params):
        geoid = -1
        try:
            geoid = get_query_param(params, "geonameid", to_type=int)
            geoobj = settings.ID_DATA[geoid]
            self.SUCCESS(geoobj)
        except KeyError:
            self.NOT_FOUND({"geonameid": geoid, "status": "Not Found"})
        except TypeError:
            self.BAD_REQUEST({"invalid": "geonameid"})

    def hint(self, params):
        part = get_query_param(params, "part", default=None)

        limit = get_query_param(params,
                                "max_count",
                                to_type=int,
                                default=settings.DEFAULT_HINTS_COUNT
                                )
        limit = min(limit, settings.HINTS_COUNT_LIMIT)

        if not part:
            return self.BAD_REQUEST({"invalid": "part"})

        hints = list(
            filter(
                lambda city: city["_autotranslit_ru_name"].lower().startswith(part.lower()),
                settings.DATA
            )
        )[:limit]

        self._add_extra_hints(part, hints, limit)

        hints.sort(
            key=lambda city: city["population"],
            reverse=True
        )

        self.SUCCESS(
            [{"name": city["name"], "geonameid": city["geonameid"]} for city in hints]
        )

    @staticmethod
    def _add_extra_hints(part, hints, limit):
        extra_hints = list()
        if len(hints) < limit:  # если вдруг недобрали городов, то подкинем еще какие-нибудь варинаты
            extra_hints = list(  # эта громоздкая штука говорит:
                filter(  # найти те города
                    lambda city: any(
                        map(  # одно из альтернативных имен которых начинается так, как юзер хочет
                            lambda altername: altername.lower().startswith(part.lower()),
                            city["alternatenames"]
                        )
                    ),
                    settings.DATA
                )
            )[:limit]

        for city in extra_hints:
            if city not in hints:
                hints.append(city)
            if len(hints) == limit:
                break

    def DEFAULT_JSON_RESPONSE(self, data: (dict, list)):
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=4).encode())

    def SUCCESS(self, data: (dict, list)):
        self.send_response(200)
        self.DEFAULT_JSON_RESPONSE(data)

    def NOT_FOUND(self, data: (dict, list)):
        self.send_response(404)
        self.DEFAULT_JSON_RESPONSE(data)

    def BAD_REQUEST(self, data: (dict, list)):
        self.send_response(400)
        self.DEFAULT_JSON_RESPONSE(data)

    def NOT_IMPLEMENTED(self, data: (dict, list)):
        self.send_response(501)
        self.DEFAULT_JSON_RESPONSE(data)

    def __str__(self):
        return self.__name__


def get_query_param(query,
                    param: str,
                    to_type: Any = str,
                    default: Any = str()):
    try:
        return to_type(query.get(param, None)[0])
    except TypeError:
        return default


