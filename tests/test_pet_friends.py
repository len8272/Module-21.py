from settings import valid_email, valid_password
from api import PetFriends
import pytest
import os
import sys


class TestPetFriends:
    @pytest.fixture(autouse=True)
    def test_get_api_key_for_valid_user(self):
        """ Проверяем, что запрос api ключа возвращает статус 200 и в результате содержится слово key"""

        self.pf = PetFriends()
        status, self.auth_key = self.pf.get_api_key(email=valid_email, password=valid_password)
        assert status == 200
        assert 'key' in self.auth_key

        yield

        assert self.status == self.status_expected

    @pytest.mark.get
    @pytest.mark.positive
    def test_get_all_pets_with_valid_key(self, filter='my_pets'):
        """ Проверяем, что запрос всех питомцев возвращает не пустой список.
        Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этот ключ
        запрашиваем список всех питомцев и проверяем что список не пустой.
        Доступное значение параметра filter - 'my_pets' либо '' """

        self.status_expected = 200
        self.status, result = self.pf.get_list_of_pets(auth_key=self.auth_key, filter=filter)
        assert len(result['pets']) > 0

    @pytest.mark.add
    @pytest.mark.positive
    def test_add_new_pet_with_valid_data(self, name='Барбоскин', animal_type='двортерьер',
                                         age='4', pet_photo='images/cat1.jpg'):
        """Проверяем что можно добавить питомца с корректными данными"""

        self.status_expected = 200
        pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
        self.status, result = self.pf.add_new_pet(auth_key=self.auth_key, name=name, animal_type=animal_type,
                                                  age=age, pet_photo=pet_photo)
        assert result['name'] == name

    @pytest.mark.mod
    @pytest.mark.positive
    def test_successful_delete_self_pet(self):
        """Проверяем возможность удаления питомца"""

        self.status_expected = 200
        _, my_pets = self.pf.get_list_of_pets(auth_key=self.auth_key, filter="my_pets")

        if len(my_pets['pets']) == 0:
            self.pf.add_new_pet(auth_key=self.auth_key, name="Суперкот", animal_type="кот", age="3", pet_photo="images/cat1.jpg")
            _, my_pets = self.pf.get_list_of_pets(auth_key=self.auth_key, filter="my_pets")

        pet_id = my_pets['pets'][0]['id']
        self.status, _ = self.pf.delete_pet(auth_key=self.auth_key, pet_id=pet_id)
        _, my_pets = self.pf.get_list_of_pets(auth_key=self.auth_key, filter="my_pets")
        assert pet_id not in my_pets.values()

    @pytest.mark.add
    @pytest.mark.positive
    def test_add_new_pet_without_photo_with_valid_data(self, name='Барбоскин', animal_type='двортерьер', age='4'):
        """Проверяем, что можно добавить питомца без фото с корректными данными"""

        self.status_expected = 200
        self.status, result = self.pf.add_new_pet_without_photo(auth_key=self.auth_key, name=name,
                                                                animal_type=animal_type, age=age)
        assert result['name'] == name

    @pytest.mark.mod
    @pytest.mark.positive
    def test_add_photo_of_pet_with_valid_data(self, pet_photo='images/cat1.jpg'):
        """Проверяем, что можно добавить фото питомца с корректными данными"""

        self.status_expected = 200
        pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
        _, my_pets = self.pf.get_list_of_pets(auth_key=self.auth_key, filter="my_pets")

        if len(my_pets['pets']) > 0:
            self.status, result = self.pf.add_photo_of_pet(auth_key=self.auth_key, pet_id=my_pets['pets'][0]['id'],
                                                           pet_photo=pet_photo)
            assert result['id'] == my_pets['pets'][0]['id']
        else:
            raise Exception("There is no my pets")

    @pytest.mark.auth
    @pytest.mark.negative
    def test_get_api_key_for_invalid_email(self, email='invalid_email', password=valid_password):
        """ Проверяем, что запрос api ключа с неверным email возвращает статус 403"""

        self.status_expected = 403
        self.status, result = self.pf.get_api_key(email=email, password=password)

    @pytest.mark.auth
    @pytest.mark.negative
    def test_get_api_key_for_empty_password(self, email=valid_email, password=''):
        """ Проверяем, что запрос api ключа с пустым паролем возвращает статус 403"""

        self.status_expected = 403
        self.status, result = self.pf.get_api_key(email=email, password=password)

    @pytest.mark.get
    @pytest.mark.negative
    def test_get_all_pets_with_invalid_key(self, filter=''):
        """ Проверяем, что запрос всех питомцев с неверным ключом возвращает статус 403.
        Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее меняем ключ
        на несуществующий и запрашиваем список всех питомцев"""

        self.status_expected = 403
        self.auth_key['key'] = 'key'
        self.status, result = self.pf.get_list_of_pets(auth_key=self.auth_key, filter=filter)

    @pytest.mark.add
    @pytest.mark.negative
    def test_add_new_pet_with_empty_name(self, name='', animal_type='двортерьер', age='4'):
        """Проверяем, что нельзя добавить питомца без имени"""

        self.status_expected = 400
        self.status, result = self.pf.add_new_pet_without_photo(auth_key=self.auth_key, name=name,
                                                                animal_type=animal_type, age=age)
        assert len(name) == 0

    @pytest.mark.add
    @pytest.mark.negative
    def test_add_new_pet_with_unlimited_name(self, name='Барбоскин'*10, animal_type='двортерьер', age='4'):
        """Проверяем, что нельзя добавить питомца с именем больше 80 символов"""

        self.status_expected = 400
        self.status, result = self.pf.add_new_pet_without_photo(auth_key=self.auth_key, name=name,
                                                                animal_type=animal_type, age=age)
        assert len(name) > 80

    @pytest.mark.add
    @pytest.mark.negative
    @pytest.mark.skip(reason="Баг на исправлении")
    def test_add_new_pet_with_invalid_animal_type(self, name='Барбоскин', animal_type='{двортерьер}', age='4'):
        """Проверяем, что нельзя добавить питомца с породой, имеющей в наименовании лишние символы.
        Для этого создаем множества для породы и нужных символов, и сравниваем их"""

        self.status_expected = 400
        self.status, result = self.pf.add_new_pet_without_photo(auth_key=self.auth_key, name=name,
                                                                animal_type=animal_type, age=age)

        lst_lat = [chr(i) for i in range(32, 123)]  # Символы от ' ' до 'z'
        lst_cyr = [chr(i) for i in range(1040, 1104)]  # Символы от 'А' до 'я'
        set_sym = set(animal_type).difference(lst_lat + lst_cyr)
        assert len(set_sym) > 0

    @pytest.mark.mod
    @pytest.mark.positive
    def test_successful_update_self_pet_info(self, name='Мурзик', animal_type='Котэ', age=5):
        """Проверяем возможность обновления информации о питомце"""

        self.status_expected = 200
        _, my_pets = self.pf.get_list_of_pets(auth_key=self.auth_key, filter="my_pets")

        if len(my_pets['pets']) > 0:
            self.status, result = self.pf.update_pet_info(auth_key=self.auth_key, pet_id=my_pets['pets'][0]['id'],
                                                          name=name, animal_type=animal_type, age=age)
            assert result['name'] == name
        else:
            raise Exception("There is no my pets")

    @pytest.mark.mod
    @pytest.mark.negative
    def test_update_pet_with_invalid_age(self, name='Барбоскин', animal_type='двортерьер', age='age'):
        """Проверяем, что нельзя изменить питомца с нечисловым возрастом"""

        self.status_expected = 400
        _, my_pets = self.pf.get_list_of_pets(auth_key=self.auth_key, filter="my_pets")

        if len(my_pets['pets']) > 0:
            self.status, result = self.pf.update_pet_info(auth_key=self.auth_key, pet_id=my_pets['pets'][0]['id'],
                                                          name=name, animal_type=animal_type, age=age)
            str_int = None

            try:
                str_int = int(age)
            except ValueError:
                print(f"Значение '{age}' невозможно преобразовать в целое число")

            assert not str_int
        else:
            raise Exception("There is no my pets")

    @pytest.mark.mod
    @pytest.mark.negative
    @pytest.mark.xfail(sys.platform == "win32", reason="Ошибка в системной библиотеке Windows")
    def test_update_pet_with_negative_age(self, name='Барбоскин', animal_type='двортерьер', age=-3):
        """Проверяем, что нельзя добавить питомца с отрицательным возрастом"""

        self.status_expected = 400
        _, my_pets = self.pf.get_list_of_pets(auth_key=self.auth_key, filter="my_pets")

        if len(my_pets['pets']) > 0:
            self.status, result = self.pf.update_pet_info(auth_key=self.auth_key, pet_id=my_pets['pets'][0]['id'],
                                                          name=name, animal_type=animal_type, age=age)
            assert int(age) < 0
        else:
            raise Exception("There is no my pets")
