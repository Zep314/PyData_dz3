# Сбор и разметка данных (семинары)
# Урок 3. Системы управления базами данных MongoDB и Кликхаус в Python
#
# 1. Установите MongoDB на локальной машине, а также зарегистрируйтесь в онлайн-сервисе.
#    https://www.mongodb.com/ https://www.mongodb.com/products/compass
# 2. Загрузите данные который вы получили на предыдущем уроке путем скрейпинга сайта с помощью
#    Buautiful Soup в MongoDB и создайте базу данных и коллекции для их хранения.
# 3. Поэкспериментируйте с различными методами запросов.
# 4. Зарегистрируйтесь в ClickHouse.
# 5. Загрузите данные в ClickHouse и создайте таблицу для их хранения.

import json
import re
from bson import json_util
from pymongo import MongoClient

SOURCE_FILE = 'source.json'
MONGO_SERVER = 'localhost'
MONGO_PORT = 27017
DB_NAME = 'BooksDB'
COLLECTION = 'books'
CHUNK_SIZE = 10


def chunk_data(local_data, chunk_size=CHUNK_SIZE):
    """
    Генератор данных для загрузки данных в базу частями
    :param local_data:
    :param chunk_size:
    :return:
    """
    for i in range(0, len(local_data), chunk_size):
        yield local_data[i:i + chunk_size]


if __name__ == '__main__':
    with open(SOURCE_FILE, 'r') as f:
        data = json.load(f)  # Грузим файл
        client = MongoClient(MONGO_SERVER, MONGO_PORT)  # Соединяемся с сервером
        db = client[DB_NAME]  # Соединяемся с базой mongodb

        books_collection = db[COLLECTION]  # Выбираем коллекцию, с которой будем работать
        books_collection.delete_many(filter={})  # Чистим коллекцию от старых данных

        data_chunk = list(chunk_data(data))  # Делим данные на части

        for chunk in data_chunk:  # Грузим данные в базу частями
            books_collection.insert_many(chunk)

        print(f'Data uploaded into MongoDB! {books_collection.count_documents({})} documents in collection.')

        # Разные запросы к БД

        # Выборка одного конкретного документа
        print('==========================')
        query = {"Name": "Under the Tuscan Sun"}
        print('Found one book, named "Under the Tuscan Sun":')
        print(json_util.dumps(books_collection.find_one(query), indent=4))

        # Выборка нескольких документов (название книги начинается с "Uns")
        print('==========================')
        query = {"Name": re.compile(r'^Uns', re.IGNORECASE)}
        projection = {"_id": 0, "Name": 1, "FullPrice": 1}
        result = json_util.dumps(books_collection.find(query, projection), indent=4)
        print('Found books whose titles begin with "Uns%":')
        print(result)

        # Пробуем агрегатные функции
        # Считаем, сколько книг в каждой категории, и выводим те категории, в которых >= 70 книг
        # аналог group by having в SQL
        print('==========================')
        my_group = {"$group":
                        {"_id": "$Category",
                         "Category_length": {"$sum": 1}
                         }}
        my_having = {"$match": {"Category_length": {"$gte": 70}}}
        agg_result = books_collection.aggregate([my_group, my_having])
        print('Counting books by category and printing those categories with more than 70 books:')
        print(json_util.dumps(agg_result, indent=4))

# Результат:
# C:\Work\python\Data\PyData_dz3\venv\Scripts\python.exe C:\Work\python\Data\PyData_dz3\main.py
# Data uploaded into MongoDB! 1000 documents in collection.
# ==========================
# Found one book, named "Under the Tuscan Sun":
# {
#     "_id": {
#         "$oid": "658973d0386ee2f757ca7ba1"
#     },
#     "Category": "Travel",
#     "Name": "Under the Tuscan Sun",
#     "UPC": "a94350ee74deaa07",
#     "FullPrice": 37.33,
#     "Price": 37.33,
#     "Tax": 0.0,
#     "Availability": "In stock (7 available)",
#     "Amount": 7,
#     "Url": "http://books.toscrape.com//catalogue/category/books/travel_2/../../../under-the-tuscan-sun_504/index.html",
#     "Cover": "http://books.toscrape.com//catalogue/category/books/travel_2/../../../under-the-tuscan-sun_504/../../media/cache/45/21/4521c581ba727f5c835e34860cbf53e5.jpg",
#     "Rating": 3
# }
# ==========================
# Found books whose titles begin with "Uns%":
# [
#     {
#         "Name": "Unseen City: The Majesty of Pigeons, the Discreet Charm of Snails & Other Wonders of the Urban Wilderness",
#         "FullPrice": 44.18
#     },
#     {
#         "Name": "Unstuffed: Decluttering Your Home, Mind, and Soul",
#         "FullPrice": 58.09
#     }
# ]
# ==========================
# Counting books by category and printing those categories with more than 70 books:
# [
#     {
#         "_id": "Nonfiction",
#         "Category_length": 110
#     },
#     {
#         "_id": "Default",
#         "Category_length": 152
#     },
#     {
#         "_id": "Sequential Art",
#         "Category_length": 75
#     }
# ]
#
# Process finished with exit code 0
