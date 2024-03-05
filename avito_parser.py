import csv
import math
import os
import sys
import time
import random
from typing import List, IO, Set, Tuple

from loguru import logger
import loguru

from product import Product
from tags import AvitoCSSTags
from seleniumbase import SB, BaseCase
import re


class Visited:
    def __init__(self, filename: str):
        self.filename = filename
        self.file: IO = None
        self.list: Set = {}

        self.__read()
        self.__open()

    def __open(self):
        self.file = open(self.filename, "a")

    def __read(self):
        if os.path.isfile(self.filename):
            with open(self.filename, "r") as file:
                self.list = {*map(lambda x: x.strip(), file.readlines())}

    def __iter__(self):
        return self.list.__iter__()

    def add(self, item: str):
        self.list.add(item)
        self.file.write(f"{item}\n")


class MyParse:
    def __init__(self, driver: BaseCase):
        self.driver = driver

    def get_elements(self, selector: Tuple[str, str], limit=0):
        return self.driver.find_elements(*selector, limit)

    def get_element(self, selector: Tuple[str, str]):
        try:
            return self.driver.find_element(*selector)
        except Exception:
            return None

    def open(self, url: str):
        return self.driver.open(url)

    def title(self):
        return self.driver.get_title()

    def wait_load(self):
        return self.driver.wait_for_ready_state_complete()


class AvitoParse:
    def __init__(self,
                 url: str,
                 csv_path: str,
                 keywords_list: List[str] = [],
                 count: int = 10,
                 max_price: int = 0,
                 min_price: int = 0,
                 address: str = None,
                 log_level: int = 0
                 ):

        """
        :param url: product's page url
        :param csv_path: Path to the CSV
        :param keywords_list: Keywords
        :param count: How many products to be processed
        :param max_price: Maximum price
        :param min_price: Mininmum price
        :param address: Address
        :param log_level: 0 - success and errors, 1 - info, 2 - debug
        """

        self.driver: BaseCase = None
        self.parser: MyParse = None
        self.url = url
        self.keywords = keywords_list
        self.count = count
        self.max_price = int(max_price) if max_price else math.inf
        self.min_price = int(min_price)
        self.address = address
        self.log_level = log_level
        self.logger = logger
        self.csv_path = csv_path
        self.visited = Visited("visited")

        self.wait_range = (5000, 7000)  # in ms

        self.logger.remove()
        self.logger.add(sys.stdout, level=["SUCCESS", "INFO", "DEBUG"][log_level])

    def __csv_file_name(self) -> str:

        if self.keywords:
            title_file = "-".join(list(map(str.lower, self.keywords)))
        else:
            title_file = 'all'
        return title_file

    def __save_data(self, data: Product):
        with open(f"{self.csv_path}", mode="a", newline='', encoding='utf-8', errors='ignore') as file:
            writer = csv.writer(file, delimiter="|")
            writer.writerow(
                list(map(lambda x: x[1], filter(lambda y: not y[0].startswith("__"), data.__dict__.items()))))

    def __check_product(self, item: Product):
        res = True
        if self.keywords:
            res = any([i.lower() in (item.description + item.title).lower() for i in self.keywords])
        return res and self.min_price <= item.price <= self.max_price

    def __try_open_page(self, url: str):
        self.driver.get(url)

        """Если не дождались загрузки"""
        try:
            self.driver.wait_for_element(*AvitoCSSTags.TOTAL_VIEWS, timeout=10)
        except Exception as ex:
            """Проверка на бан по ip"""
            if "Доступ ограничен" in self.driver.get_title():
                self.logger.success("Доступ ограничен: проблема с IP. \nПоследние объявления будут без подробностей")

            # self.driver.go_back()

            self.logger.debug("Не дождался загрузки страницы")
            return False
        return True

    def __parse_product_page(self, item: Product) -> Product:
        self.parser.open(item.url)
        self.parser.wait_load()

        self.logger.debug(f"Смотрю подробнее {item.title} {item.url}")

        """Адрес"""
        item.address = self.parser.get_element(AvitoCSSTags.ADDRESS).text.lower()

        """Количество просмотров"""
        item.views = int(self.parser.get_element(AvitoCSSTags.TOTAL_VIEWS).text.split()[0])

        """Дата публикации"""
        item.publish_date = self.parser.get_element(AvitoCSSTags.PUBLISH_DATE).text.replace("· ", "")

        """Имя продавца"""
        item.seller = self.parser.get_element(AvitoCSSTags.SELLER_NAME).text

        return item

    def __pretty_log(self, data: Product):
        """Красивый вывод"""
        self.logger.success(
            f'\n{data.title}\n'
            f'Цена: {data.price}\n'
            f'Описание: {data.description}\n'
            f'Просмотров: {data.views}\n'
            f'Продвинуто: {data.promoted}\n'
            f'Дата публикации: {data.publish_date}\n'
            f'Продавец: {data.seller}\n'
            f'Изображение: {data.img}\n'
            f'Ссылка: {data.url}\n')

    def __parse_page(self, items):
        for product in filter(self.__check_product, items):
            if self.count <= 0:
                break

            self.logger.debug(f"Смотрю на {product.title} {product.url}")

            if product.ads_id in self.visited:
                continue
            self.visited.add(product.ads_id)

            product = self.__parse_product_page(product)

            if self.address and self.address.lower() != product.address:
                continue

            self.__pretty_log(data=product)
            self.__save_data(data=product)

            yield product
            self.count -= 1

    def __wait(self):
        time.sleep(random.randint(*self.wait_range) / 1000)

    def __get_items(self):

        self.parser.wait_load()

        titles = self.parser.get_elements(AvitoCSSTags.TITLES)

        for title in titles:
            parser = MyParse(title)

            name = parser.get_element(AvitoCSSTags.NAME).text

            description = parser.get_element(AvitoCSSTags.DESCRIPTIONS)
            description = "" if description is None else description.text

            url = parser.get_element(AvitoCSSTags.URL).get_attribute("href")
            price = parser.get_element(AvitoCSSTags.PRICE).get_attribute("content")
            img = parser.get_element(AvitoCSSTags.IMG)
            img = img.get_attribute("src") if img else ""
            promoted = bool(parser.get_element(AvitoCSSTags.PROMOTED))
            ads_id = title.get_attribute("data-item-id")

            yield Product(title=name,
                          description=description,
                          url=url,
                          img=img,
                          price=float(price),
                          ads_id=ads_id,
                          promoted=promoted)

    def __paginator(self):
        self.logger.info('Страница успешно загружена. Просматриваю объявления')

        items = []

        while True:
            if self.count < len(items):
                break

            items += [*self.__get_items()]

            self.__wait()

            """Проверяем есть ли кнопка далее"""
            button = self.parser.get_element(AvitoCSSTags.NEXT_BTN)
            if button:
                button.click()
                self.logger.debug("Следующая страница")
            else:
                self.logger.info("Нет кнопки дальше")
                break

        yield from self.__parse_page(items)

    def __load_start_page(self):
        self.parser.open(self.url)

        if "Доступ ограничен" in self.parser.title():
            raise Exception("IP Blocked")

    def parse(self):
        with SB(uc=True,
                headed=True if self.log_level == 2 else False,
                headless=True if self.log_level != 2 else False,
                page_load_strategy="eager",
                block_images=True,
                # skip_js_waits=True,
                ) as self.driver:
            try:
                self.parser: MyParse = MyParse(self.driver)

                self.__load_start_page()
                yield from self.__paginator()
            except Exception as error:
                self.logger.error(f"Error: {error}")
