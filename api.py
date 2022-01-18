import json
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import datetime
import functools
import inspect

# Структура параметров
pf_params = {'header': ['auth_key', 'email', 'password'],
             'path': ['pet_id'],
             'query': ['filter'],
             'formData': ['name', 'animal_type', 'age', 'pet_photo']}
last_func = None


def cut_photo(dict_val):
    for i_key, i_val in dict_val.items():
        if i_val.startswith('data:image'):
            dict_val[i_key] = i_val[0:30] + ' ...'


# Декоратор логирования запросов
def pf_log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with open('log.txt', 'a', encoding="utf8") as log_file:
            global last_func
            args_repr = [repr(a) for a in args]

            # Формируем структуру параметров с именованными переменными и их значениями
            val_params = {k: [] for k in pf_params.keys()}
            for p_key, p_val in pf_params.items():
                for k, v in kwargs.items():
                    if k in p_val:
                        val_params[p_key].append(f"{k}={v!r}")

            # Формируем список параметров с их типами
            kwargs_repr = []
            for key, val in val_params.items():
                lst_val = []
                for item in val:
                    lst_val.append(item)
                if lst_val:
                    str_val = key + ' : ' + ", ".join(lst_val)
                    kwargs_repr.append(str_val)

            # Определяем название вызывающего метода
            ins = inspect.stack()
            if last_func != ins[1][3]:
                log_file.write(f"{datetime.datetime.now()} {ins[1][3]} ->\n")
                last_func = ins[1][3]

            signature = ", ".join(args_repr + kwargs_repr)
            log_file.write(f"{datetime.datetime.now()} {func.__name__} ({signature})\n")
            status, result = func(*args, **kwargs)

            # Обрезаем значение картинки для читабельности лога
            if result and isinstance(result, dict):
                if 'pets' in result.keys():
                    for item in result['pets']:
                        cut_photo(item)
                else:
                    cut_photo(result)

            log_file.write(f"{datetime.datetime.now()} {func.__name__} : status {status}, body {result}\n")
            return status, result
    return wrapper


class PetFriends:
    """апи библиотека к веб приложению Pet Friends"""

    def __init__(self):
        self.base_url = "https://petfriends1.herokuapp.com/"

    def __repr__(self):
        return "PetFriends"

    @pf_log
    def get_api_key(self, email: str, password: str) -> json:
        """Метод делает запрос к API сервера и возвращает статус запроса и результат в формате
        JSON с уникальным ключем пользователя, найденного по указанным email и паролем"""
        #self.__class__
        headers = {
            'email': email,
            'password': password,
        }
        res = requests.get(self.base_url+'api/key', headers=headers)
        status = res.status_code
        result = ""
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

    @pf_log
    def get_list_of_pets(self, auth_key: json, filter: str = "") -> json:
        """Метод делает запрос к API сервера и возвращает статус запроса и результат в формате JSON
        со списком наденных питомцев, совпадающих с фильтром. На данный момент фильтр может иметь
        либо пустое значение - получить список всех питомцев, либо 'my_pets' - получить список
        собственных питомцев"""

        headers = {'auth_key': auth_key['key']}
        filter = {'filter': filter}

        res = requests.get(self.base_url + 'api/pets', headers=headers, params=filter)
        status = res.status_code
        result = ""
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

    @pf_log
    def add_new_pet(self, auth_key: json, name: str, animal_type: str, age: str, pet_photo: str) -> json:
        """Метод отправляет (постит) на сервер данные о добавляемом питомце и возвращает статус
        запроса на сервер и результат в формате JSON с данными добавленного питомца"""

        data = MultipartEncoder(
            fields={
                'name': name,
                'animal_type': animal_type,
                'age': age,
                'pet_photo': (pet_photo, open(pet_photo, 'rb'), 'image/jpeg')
            })
        headers = {'auth_key': auth_key['key'], 'Content-Type': data.content_type}

        res = requests.post(self.base_url + 'api/pets', headers=headers, data=data)
        status = res.status_code
        result = ""
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

    @pf_log
    def delete_pet(self, auth_key: json, pet_id: str) -> json:
        """Метод отправляет на сервер запрос на удаление питомца по указанному ID и возвращает
        статус запроса и результат в формате JSON с текстом уведомления о успешном удалении.
        На сегодняшний день тут есть баг - в result приходит пустая строка, но status при этом = 200"""

        headers = {'auth_key': auth_key['key']}

        res = requests.delete(self.base_url + 'api/pets/' + pet_id, headers=headers)
        status = res.status_code
        result = ""
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

    @pf_log
    def update_pet_info(self, auth_key: json, pet_id: str, name: str,
                        animal_type: str, age: int) -> json:
        """Метод отправляет запрос на сервер о обновлении данных питомуа по указанному ID и
        возвращает статус запроса и result в формате JSON с обновлённыи данными питомца"""

        headers = {'auth_key': auth_key['key']}
        data = {
            'name': name,
            'age': age,
            'animal_type': animal_type
        }

        res = requests.put(self.base_url + 'api/pets/' + pet_id, headers=headers, data=data)
        status = res.status_code
        result = ""
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

    # Еще 2 метода по заданию 19.7.2

    @pf_log
    def add_new_pet_without_photo(self, auth_key: json, name: str, animal_type: str, age: str) -> json:  # 1
        """Метод отправляет (постит) на сервер данные о добавляемом питомце без фото и возвращает статус
        запроса на сервер и результат в формате JSON с данными добавленного питомца"""

        headers = {'auth_key': auth_key['key']}
        data = {
            'name': name,
            'animal_type': animal_type,
            'age': age
        }

        res = requests.post(self.base_url + '/api/create_pet_simple', headers=headers, data=data)
        status = res.status_code
        result = ""
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

    @pf_log
    def add_photo_of_pet(self, auth_key: json, pet_id: str, pet_photo: str) -> json:  # 2
        """Метод отправляет (постит) на сервер фото питомца и возвращает статус
        запроса на сервер и результат в формате JSON с данными измененного питомца"""

        data = MultipartEncoder(
            fields={
                'pet_photo': (pet_photo, open(pet_photo, 'rb'), 'image/jpeg')
            })
        headers = {'auth_key': auth_key['key'], 'Content-Type': data.content_type}

        res = requests.post(self.base_url + '/api/pets/set_photo/' + pet_id, headers=headers, data=data)
        status = res.status_code
        result = ""
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result
