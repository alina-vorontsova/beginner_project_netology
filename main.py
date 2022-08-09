import requests
import datetime
import json
from tqdm import tqdm


with open('config.txt') as config_file: # В файле записан токен для ВК
    vk_token = config_file.readline().strip()

def ya_token():
    '''Получение токена Я.Диска, на который будут загружены фото.'''
    ya_token = input('Введите токен: ')
    return ya_token

def user_id():
    '''Получение id пользователя, чьи фотографии надо скопировать на Я.Диск.'''
    user_id = input('Введите id пользователя: ')
    return user_id


class VK:

    def __init__(self, vk_token, user_id, version='5.131'):
        '''Получение параметров авторизации для запроса.'''
        self.token = vk_token
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def all_photos(self, count=5):
        '''Получение фотографий из определённого альбома пользователя.'''
        url = 'https://api.vk.com/method/photos.get'
        self.count = count # По умолчанию (по условию задачи) - 5
        params = {'owner_id': self.id, 'album_id': 'profile', 'rev': 0, 'extended': 1, 'photo_sizes': 1, 'count': self.count}
        response = requests.get(url, params={**self.params, **params}).json()
        res = response['response']['items']
        return res

    def biggest_photo(self):
        '''Получение фотографий в максимальном размере.'''
        all_photos = vk.all_photos()
        photos_dict = {}
        for photo in all_photos:
            url_to_biggest_photo = photo['sizes'][-1]['url']
            likes = photo['likes']['count']
            date = datetime.datetime.fromtimestamp(photo['date']).strftime("%d.%m.%Y")
            type = photo['sizes'][-1]['type']
            photo_info = {'url': url_to_biggest_photo, 
                'likes_count': likes, 
                'date': date,
                'size_type': type}
            if likes not in photos_dict.keys():
                photos_dict[likes] = photo_info
            else:
                photos_dict[f'{likes}, {date}'] = photo_info
        return photos_dict

    def json_file(self):
        '''Создание json-файла с информацией о фото.'''
        photos_dict = vk.biggest_photo()
        photos_info_list = []
        photos_info_dict = {}
        for value in photos_dict.values():
            photos_info_dict = {"file_name": value['likes_count'], "size": value['size_type']}
            photos_info_list.append(photos_info_dict)
        with open('photos_info.json', 'w') as file:
            json.dump(photos_info_list, file, indent=4)
        return 'Succes'


class Yandex:

    def __init__(self, ya_token: str):
        '''Получение параметров авторизации для запроса.'''
        self.token = ya_token
        self.headers = {'Content-Type': 'application/json', 'Authorization': f'OAuth {ya_token}'}

    def create_new_folder(self, folder_name='Курсовая'):
        '''Создание новой папки на Я.Диске.'''
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {'path': folder_name}
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code != 200:
            requests.put(url, headers=self.headers, params=params)
            print(f'Папка "{folder_name}" успешно создана.')
        else:
            print(f'Папка {folder_name} уже существует.')
        return folder_name

    def upload_photos(self):
        '''Загрузка фото на Я.Диск.'''
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        folder_name = ya.create_new_folder()
        photos_dict = vk.biggest_photo()
        for key, value in tqdm(photos_dict.items()):
            params = {'path': f'{folder_name}/{key}', 'url': value['url'], 'overwrite': False}
            response = requests.post(url, headers=self.headers, params=params)
        return response


if __name__ == '__main__':
    user_id = user_id()
    ya_token = ya_token()
    vk = VK(vk_token, user_id)
    ya = Yandex(ya_token)
    ya.upload_photos()