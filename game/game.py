"""Модуль с интерфейсом и реализацией класса игры"""

from abc import ABC, abstractmethod
from dataclasses import replace
from typing import Any, TypeVar

from .clicker import AbstractClicker
from .exceptions import (
    ActionCancelled,
    NoItemsToChoose,
    NotEnoughMoney,
    TamagochiIsGone,
    WrongChoice,
)
from .models import Food, Medicine
from .tamagochi import AbstractTamagochi

Item = TypeVar('Item', Food, Medicine)


class AbstractGame(ABC):
    """Интерфейс для логики игры"""

    @abstractmethod
    def __init__(
        self,
        tamagochi: AbstractTamagochi,
        clicker: AbstractClicker,
        all_food: list[Food],
        all_medicine: list[Medicine]
    ) -> None:
        """
        Абстрактный метод инициализации класса игры

        :param tamagochi: экземпляр тамагочи
        :param clicker: экземпляр кликера
        :param all_food: все доступные варианты еды
        :param all_medicine: все доступные варианты лекарств
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def tamagochi(self) -> AbstractTamagochi:
        """
        Абстрактное свойство для доступа к питомцу

        :return: питомец, за которым ухаживает игрок
        """
        raise NotImplementedError

    @abstractmethod
    def work(self) -> int:
        """
        Абстрактный метод для логики действия "работа

        :return: количество заработанных монет
        """
        raise NotImplementedError

    @abstractmethod
    def buy_food(self) -> None:
        """Абстрактный метод для покупки еды"""
        raise NotImplementedError

    @abstractmethod
    def buy_medicine(self) -> None:
        """Абстрактный метод для покупки лекарства"""
        raise NotImplementedError

    @abstractmethod
    def feed_tamagochi(self) -> None:
        """Абстрактный метод для кормления тамагочи"""
        raise NotImplementedError

    @abstractmethod
    def heal_tamagochi(self) -> None:
        """Абстрактный метод для лечения тамагочи"""
        raise NotImplementedError

    @abstractmethod
    def rest_tamagochi(self) -> None:
        """Абстрактный метод для отдыха тамагочи"""
        raise NotImplementedError

    @abstractmethod
    def play_with_tamagochi(self) -> None:
        """Абстрактный метод для игры с тамагочи"""
        raise NotImplementedError

    @abstractmethod
    def get_status(self) -> dict[str, Any]:
        """
        Абстрактный метод для получения статуса (всех характеристик) тамагочи

        :return: словарь со всеми характеристиками тамагочи
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def food(self) -> list[Food]:
        """
        Абстрактное свойство для доступа к сумке с едой

        :return: список с имеющимися (купленными) объектами еды
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def medicine(self) -> list[Medicine]:
        """
        Абстрактное свойство для доступа к сумке с лекарствами

        :return: список с имеющимися (купленными) объектами лекарств
        """
        raise NotImplementedError


class SimpleGame(AbstractGame):
    """
    Игра «Тамагочи-кликер»

    Управляет ресурсами игрока: кошельком, магазином и сумками
    с едой и лекарствами. Каждое взаимодействие с питомцем (кормление,
    лечение, игра, отдых) занимает один тик его времени. Когда питомец
    умирает, игра заканчивается и любые действия становятся недоступны.
    """

    REST_PRICE = 10  # место на лежанке тоже стоит денег

    def __init__(
        self,
        tamagochi: AbstractTamagochi,
        clicker: AbstractClicker,
        all_food: list[Food],
        all_medicine: list[Medicine]
    ) -> None:
        """
        Создаёт игру с пустыми сумками и пустым кошельком

        :param tamagochi: экземпляр тамагочи
        :param clicker: экземпляр кликера
        :param all_food: все доступные в магазине варианты еды
        :param all_medicine: все доступные в аптеке варианты лекарств
        """
        self._tamagochi = tamagochi
        self._clicker = clicker
        self._all_food = list(all_food)
        self._all_medicine = list(all_medicine)
        self._food_bag: list[Food] = []
        self._medicine_bag: list[Medicine] = []
        self._coins = 0

    @property
    def tamagochi(self) -> AbstractTamagochi:
        """
        Питомец, за которым ухаживает игрок

        :return: экземпляр тамагочи
        """
        return self._tamagochi

    @property
    def food(self) -> list[Food]:
        """
        Сумка с едой

        :return: копия списка купленной еды
        """
        return list(self._food_bag)

    @property
    def medicine(self) -> list[Medicine]:
        """
        Сумка с лекарствами

        :return: копия списка купленных лекарств
        """
        return list(self._medicine_bag)

    def work(self) -> int:
        """
        Отправляет игрока на работу: кликер приносит монеты в кошелёк

        :return: количество заработанных монет
        :raises TamagochiIsGone: если игра уже окончена
        """
        self._ensure_game_is_on()
        self._clicker.click()
        income = self._clicker.income_per_click
        self._coins += income
        return income

    def buy_food(self) -> None:
        """
        Покупает выбранную игроком еду и кладёт её в сумку

        :raises TamagochiIsGone: если игра уже окончена
        :raises NoItemsToChoose: если в магазине нет еды
        :raises ActionCancelled: если игрок отказался от покупки
        :raises WrongChoice: если выбран несуществующий товар
        :raises NotEnoughMoney: если не хватает монет
        """
        self._ensure_game_is_on()
        food = self._choose(
            self._all_food,
            f'Какую еду купить? Монет: {self._coins}',
            'В магазине нет еды',
        )
        self._pay(food.price)
        self._food_bag.append(food)

    def buy_medicine(self) -> None:
        """
        Покупает выбранное игроком лекарство и кладёт его в сумку

        :raises TamagochiIsGone: если игра уже окончена
        :raises NoItemsToChoose: если в аптеке нет лекарств
        :raises ActionCancelled: если игрок отказался от покупки
        :raises WrongChoice: если выбран несуществующий товар
        :raises NotEnoughMoney: если не хватает монет
        """
        self._ensure_game_is_on()
        medicine = self._choose(
            self._all_medicine,
            f'Какое лекарство купить? Монет: {self._coins}',
            'В аптеке нет лекарств',
        )
        self._pay(medicine.price)
        # каждая покупка — новая упаковка со своим счётчиком применений
        self._medicine_bag.append(replace(medicine, uses=0))

    def feed_tamagochi(self) -> None:
        """
        Кормит питомца выбранной едой из сумки

        Съеденная еда исчезает из сумки, проходит один тик.

        :raises TamagochiIsGone: если игра уже окончена
        :raises NoItemsToChoose: если сумка с едой пуста
        :raises ActionCancelled: если игрок передумал кормить
        :raises WrongChoice: если выбрана несуществующая еда
        """
        self._ensure_game_is_on()
        food = self._choose(
            self._food_bag,
            'Чем покормить питомца?',
            'Сумка с едой пуста — сначала купите еду',
        )
        self._tamagochi.feed(food)
        self._food_bag.remove(food)
        self._tamagochi.update()

    def heal_tamagochi(self) -> None:
        """
        Лечит питомца выбранным лекарством из сумки

        Тратит одно применение лекарства; закончившееся лекарство
        выбрасывается из сумки. Проходит один тик.

        :raises TamagochiIsGone: если игра уже окончена
        :raises NoItemsToChoose: если сумка с лекарствами пуста
        :raises ActionCancelled: если игрок передумал лечить
        :raises WrongChoice: если выбрано несуществующее лекарство
        """
        self._ensure_game_is_on()
        medicine = self._choose(
            self._medicine_bag,
            'Каким лекарством лечить питомца?',
            'Сумка с лекарствами пуста — сначала купите лекарство',
        )
        self._tamagochi.heal(medicine)
        medicine.uses += 1
        if medicine.is_empty():
            self._medicine_bag.remove(medicine)
        self._tamagochi.update()

    def rest_tamagochi(self) -> None:
        """
        Оплачивает питомцу отдых, проходит один тик

        :raises TamagochiIsGone: если игра уже окончена
        :raises NotEnoughMoney: если не хватает монет на отдых
        """
        self._ensure_game_is_on()
        self._pay(self.REST_PRICE)
        self._tamagochi.rest()
        self._tamagochi.update()

    def play_with_tamagochi(self) -> None:
        """
        Играет с питомцем, проходит один тик

        :raises TamagochiIsGone: если игра уже окончена
        :raises TamagochiIsTired: если питомцу не хватает энергии
        """
        self._ensure_game_is_on()
        self._tamagochi.play()
        self._tamagochi.update()

    def get_status(self) -> dict[str, int]:
        """
        Собирает показатели питомца и количество монет игрока

        :return: словарь с показателями питомца и ключом coins
        """
        return {**self._tamagochi.status, 'coins': self._coins}

    def _ensure_game_is_on(self) -> None:
        """
        Проверяет, что игра ещё не окончена

        :raises TamagochiIsGone: если питомец умер
        """
        if not self._tamagochi.is_alive():
            raise TamagochiIsGone('Питомец умер. Игра окончена')

    def _pay(self, price: int) -> None:
        """
        Списывает монеты из кошелька

        :param price: сумма к оплате
        :raises NotEnoughMoney: если в кошельке меньше монет, чем нужно
        """
        if price > self._coins:
            raise NotEnoughMoney(
                f'Не хватает монет: нужно {price}, а у вас {self._coins}'
            )
        self._coins -= price

    def _choose(
        self,
        items: list[Item],
        title: str,
        empty_message: str,
    ) -> Item:
        """
        Предлагает игроку выбрать предмет из списка по номеру

        :param items: варианты для выбора
        :param title: заголовок меню
        :param empty_message: текст ошибки, если выбирать не из чего
        :return: выбранный предмет
        :raises NoItemsToChoose: если список пуст
        :raises ActionCancelled: если игрок ввёл 0
        :raises WrongChoice: если введён несуществующий номер
        """
        if not items:
            raise NoItemsToChoose(empty_message)
        print(title)
        for number, item in enumerate(items, start=1):
            print(f'{number}. {item}')
        print('0. Отмена')
        answer = input('Ваш выбор: ').strip()
        if answer == '0':
            raise ActionCancelled('Действие отменено')
        if not answer.isdecimal() or not 1 <= int(answer) <= len(items):
            raise WrongChoice(f'Варианта «{answer}» нет в списке')
        return items[int(answer) - 1]
