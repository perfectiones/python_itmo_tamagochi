"""Модуль с интерфейсом и реализацией кликера"""

import random
from abc import ABC, abstractmethod


class AbstractClicker(ABC):
    """Интерфейс для кликера"""

    @abstractmethod
    def __init__(self) -> None:
        """Абстрактный метод инициализации"""
        raise NotImplementedError

    @abstractmethod
    def click(self) -> None:
        """Абстрактный метод клика для накапливания монет"""
        raise NotImplementedError

    @property
    @abstractmethod
    def income_per_click(self) -> int:
        """Абстрактное свойство для доступа к количеству монет за клик"""
        raise NotImplementedError


class SimpleRandomClicker(AbstractClicker):
    """
    Кликер со случайным доходом

    Каждый клик приносит случайное количество монет
    от min_income до max_income включительно.
    """

    def __init__(
        self,
        min_income: int,
        max_income: int,
        rng: random.Random | None = None,
    ) -> None:
        """
        Создаёт кликер с заданным диапазоном дохода за клик

        :param min_income: минимальный доход за клик
        :param max_income: максимальный доход за клик
        :param rng: генератор случайных чисел (по умолчанию — новый)
        :raises ValueError: если min_income < 0 или min_income > max_income
        """
        if min_income < 0 or min_income > max_income:
            raise ValueError(
                'Доход за клик должен удовлетворять условию '
                '0 <= min_income <= max_income'
            )
        self._min_income = min_income
        self._max_income = max_income
        self._rng = rng if rng is not None else random.Random()
        self._income_per_click = 0

    def click(self) -> None:
        """Совершает клик и определяет, сколько монет он принёс"""
        self._income_per_click = self._rng.randint(
            self._min_income, self._max_income
        )

    @property
    def income_per_click(self) -> int:
        """
        Количество монет, принесённых последним кликом

        :return: доход последнего клика (0, если кликов ещё не было)
        """
        return self._income_per_click
