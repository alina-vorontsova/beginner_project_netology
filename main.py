from typing import Any

import requests
import datetime
import json
from tqdm import tqdm


def get_yandex_token() -> str:
    """Получение токена Я.Диска, на который будут загружены фото."""
    return input("Введите токен Я.Диска: ")


def get_vk_user_id() -> int:
    """Получение id пользователя, чьи фотографии надо скопировать на Я.Диск."""
    return int(input("Введите id пользователя ВК: "))


class VK:
    def __init__(
        self, vkontakte_token: str, user_id: int, version: str = "5.131", count: int = 5
    ):
        """Получение параметров авторизации для запроса."""
        self.token = vkontakte_token
        self.id = user_id
        self.version = version
        self.count = count
        self.params = {"access_token": self.token, "v": self.version}

    def all_photos(self) -> list:
        """Получение фотографий из определённого альбома пользователя."""
        params: dict[str, Any] = {
            "owner_id": self.id,
            "album_id": "profile",
            "rev": 0,
            "extended": 1,
            "photo_sizes": 1,
            "count": self.count,
        }
        response: dict[str, Any] = requests.get(
            "https://api.vk.com/method/photos.get", params={**self.params, **params}
        ).json()
        return response["response"]["items"]

    @staticmethod
    def biggest_photo() -> dict[str, Any]:
        """Получение фотографий в максимальном размере."""
        all_photos: list = vk.all_photos()
        photos_dict: dict[str | int, Any] = {}
        for photo in all_photos:
            likes: int = photo["likes"]["count"]
            date: str = datetime.datetime.fromtimestamp(photo["date"]).strftime(
                "%d.%m.%Y"
            )
            photo_info: dict[str, Any] = {
                "url": photo["sizes"][-1]["url"],
                "likes_count": likes,
                "date": date,
                "size_type": photo["sizes"][-1]["type"],
            }
            if likes not in photos_dict.keys():
                photos_dict[likes] = photo_info
            else:
                photos_dict[f"{likes}, {date}"] = photo_info
        return photos_dict

    @staticmethod
    def json_file():
        """Создание json-файла с информацией о фото."""
        photos_dict: dict[str, Any] = vk.biggest_photo()
        photos_info_list: list = []
        photos_info_dict: dict[str, Any] = {}
        for value in photos_dict.values():
            photos_info_dict["file_name"] = value["likes_count"]
            photos_info_dict["size"] = value["size_type"]
            photos_info_list.append(photos_info_dict)
        with open("photos_info.json", "w") as file:
            json.dump(photos_info_list, file, indent=4)


class Yandex:
    def __init__(self, ya_token: str):
        """Получение параметров авторизации для запроса."""
        self.token = ya_token
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"OAuth {ya_token}",
        }

    def create_new_folder(self, folder_name="Курсовая") -> str:
        """Создание новой папки на Я.Диске."""
        url: str = "https://cloud-api.yandex.net/v1/disk/resources"
        params: dict[str, str] = {"path": folder_name}
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            requests.put(url, headers=self.headers, params=params)
            print(f'Папка "{folder_name}" успешно создана.')
        else:
            print(
                f"Папка {folder_name} уже существует. Фотографии будут загружены в неё."
            )
        return folder_name

    def upload_photos(self):
        """Загрузка фото на Я.Диск."""
        folder_name: str = ya.create_new_folder()
        photos_dict: dict[str, Any] = vk.biggest_photo()
        for key, value in tqdm(photos_dict.items()):
            params: dict[str, Any] = {
                "path": f"{folder_name}/{key}",
                "url": value["url"],
                "overwrite": False,
            }
            requests.post(
                "https://cloud-api.yandex.net/v1/disk/resources/upload",
                headers=self.headers,
                params=params,
            )


if __name__ == "__main__":
    # В файле "config.py" должен быть записан токен для ВК
    with open("config.txt") as config_file:
        vk_token: str = config_file.readline().strip()

    vk_user_id: int = get_vk_user_id()
    yandex_token: str = get_yandex_token()
    vk: VK = VK(vk_token, vk_user_id)
    ya: Yandex = Yandex(yandex_token)
    ya.upload_photos()
