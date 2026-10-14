"""Модуль с интерфейсом и реализациями класса тамагочи"""

import random
from abc import ABC, abstractmethod

from .exceptions import MedicineIsOver, TamagochiIsGone, TamagochiIsTired
from .models import Food, Medicine


class AbstractTamagochi(ABC):
    """Интерфейс логики тамагочи"""

    @abstractmethod
    def feed(self, food: Food) -> None:
        """
        Абстрактный метод для кормления тамагочи

        :param food: объект еды для кормления
        """
        raise NotImplementedError

    @abstractmethod
    def play(self) -> None:
        """Абстрактный метод для игры с тамагочи"""
        raise NotImplementedError

    @abstractmethod
    def rest(self) -> None:
        """Абстрактный метод для отдыха тамагочи"""
        raise NotImplementedError

    @abstractmethod
    def heal(self, medicine: Medicine) -> None:
        """
        Абстрактный метод для лечения тамагочи

        :param medicine: лекарство для лечения
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def status(self) -> dict[str, int]:
        """
        Абстрактное свойство для доступа ко всем состояниям тамагочи

        :return: словарь со всеми состояниями тамагочи
        """
        raise NotImplementedError

    @abstractmethod
    def is_alive(self) -> bool:
        """
        Абстрактный метод для проверки жив ли тамагочи

        :return: True если жив, иначе False
        """
        raise NotImplementedError

    @abstractmethod
    def is_sick(self) -> bool:
        """
        Абстрактный метод для проверки, не заболел ли тамагочи

        :return: True если тамагочи болеет, иначе False
        """
        raise NotImplementedError

    @abstractmethod
    def update(self) -> None:
        """
        Абстрактный метод для обновления состояний тамагочи.
        Должен использоваться после каждого взаимодействия с тамагочи
        """
        raise NotImplementedError


class SimpleTamagochi(AbstractTamagochi):
    """
    Котёнок-тамагочи

    Показатели голода, усталости, энергии и здоровья лежат
    в диапазоне от 0 до 100. С каждым тиком (вызовом update) питомец
    голодает, устаёт и тратит энергию. Ухоженный питомец понемногу
    восстанавливает здоровье, а голодный или измотанный теряет его
    и чаще болеет. Болезнь отнимает здоровье, добавляет усталость
    и вдвое ослабляет отдых. Когда здоровье падает до нуля,
    питомец умирает.
    """

    MIN_LEVEL = 0
    MAX_LEVEL = 100
    CRITICAL_LEVEL = 80  # голод или усталость, опасные для здоровья
    COMFORT_LEVEL = 50  # граница, при которой питомец чувствует себя хорошо

    START_HUNGER = 20

    HUNGER_PER_TICK = 3
    FATIGUE_PER_TICK = 3
    ENERGY_PER_TICK = 3
    HEALTH_REGEN = 2
    NEGLECT_DAMAGE = 5  # урон за каждый запущенный показатель
    SICKNESS_DAMAGE = 5
    SICKNESS_FATIGUE = 5
    RISK_SICKNESS_CHANCE = 0.1  # прибавка к шансу заболеть за фактор риска

    PLAY_ENERGY_COST = 15
    PLAY_FATIGUE = 15
    PLAY_HUNGER = 10
    PLAY_HEALTH_BONUS = 5
    REST_POWER = 30

    def __init__(
        self,
        name: str = 'Барсик',
        sickness_chance: float = 0.05,
        rng: random.Random | None = None,
    ) -> None:
        """
        Создаёт бодрого, здорового и слегка голодного питомца

        :param name: имя питомца
        :param sickness_chance: базовая вероятность заболеть за один тик
        :param rng: генератор случайных чисел (по умолчанию — новый)
        :raises ValueError: если вероятность болезни вне отрезка [0, 1]
        """
        if not 0 <= sickness_chance <= 1:
            raise ValueError('Вероятность болезни должна быть от 0 до 1')
        self.name = name
        self._sickness_chance = sickness_chance
        self._rng = rng if rng is not None else random.Random()
        self._hunger = self.START_HUNGER
        self._fatigue = self.MIN_LEVEL
        self._energy = self.MAX_LEVEL
        self._hp = self.MAX_LEVEL
        self._sick = False

    @property
    def status(self) -> dict[str, int]:
        """
        Текущие показатели питомца

        :return: словарь с ключами hunger, fatigue, energy и hp
        """
        return {
            'hunger': self._hunger,
            'fatigue': self._fatigue,
            'energy': self._energy,
            'hp': self._hp,
        }

    def is_alive(self) -> bool:
        """
        Проверяет, жив ли питомец

        :return: True, если здоровье больше нуля, иначе False
        """
        return self._hp > self.MIN_LEVEL

    def is_sick(self) -> bool:
        """
        Проверяет, болеет ли питомец

        :return: True, если питомец болен, иначе False
        """
        return self._sick

    def feed(self, food: Food) -> None:
        """
        Кормит питомца: голод уменьшается на сытность еды

        Если еда сытнее, чем питомец голоден, он объедается
        и теряет энергию на величину лишней сытости.

        :param food: еда для кормления
        :raises TamagochiIsGone: если питомец мёртв
        """
        self._ensure_alive()
        overeating = max(0, food.satiety - self._hunger)
        self._hunger = self._clamp(self._hunger - food.satiety)
        self._energy = self._clamp(self._energy - overeating)

    def play(self) -> None:
        """
        Играет с питомцем

        Игра тратит энергию, утомляет и вызывает аппетит,
        но здоровому питомцу прибавляет здоровья.

        :raises TamagochiIsGone: если питомец мёртв
        :raises TamagochiIsTired: если на игру не хватает энергии
        """
        self._ensure_alive()
        if self._energy < self.PLAY_ENERGY_COST:
            raise TamagochiIsTired(
                f'{self.name} слишком устал для игр — дайте ему отдохнуть'
            )
        self._energy = self._clamp(self._energy - self.PLAY_ENERGY_COST)
        self._fatigue = self._clamp(self._fatigue + self.PLAY_FATIGUE)
        self._hunger = self._clamp(self._hunger + self.PLAY_HUNGER)
        if not self._sick:
            self._hp = self._clamp(self._hp + self.PLAY_HEALTH_BONUS)

    def rest(self) -> None:
        """
        Укладывает питомца отдыхать: энергия растёт, усталость падает

        Больной питомец восстанавливается вдвое хуже.

        :raises TamagochiIsGone: если питомец мёртв
        """
        self._ensure_alive()
        recovery = self.REST_POWER // 2 if self._sick else self.REST_POWER
        self._energy = self._clamp(self._energy + recovery)
        self._fatigue = self._clamp(self._fatigue - recovery)

    def heal(self, medicine: Medicine) -> None:
        """
        Лечит питомца: восстанавливает здоровье и излечивает болезнь

        Расход лекарства (счётчик применений) ведёт владелец лекарства.

        :param medicine: лекарство для лечения
        :raises TamagochiIsGone: если питомец мёртв
        :raises MedicineIsOver: если лекарство закончилось
        """
        self._ensure_alive()
        if medicine.is_empty():
            raise MedicineIsOver(f'{medicine.name} закончился')
        self._hp = self._clamp(self._hp + medicine.heal_hp)
        self._sick = False

    def update(self) -> None:
        """
        Проживает один тик времени

        Питомец голодает, устаёт и тратит энергию, здоровье меняется
        в зависимости от ухода, а затем питомец может заболеть.

        :raises TamagochiIsGone: если питомец мёртв
        """
        self._ensure_alive()
        fatigue_gain = self.FATIGUE_PER_TICK
        if self._sick:
            fatigue_gain += self.SICKNESS_FATIGUE
        self._hunger = self._clamp(self._hunger + self.HUNGER_PER_TICK)
        self._fatigue = self._clamp(self._fatigue + fatigue_gain)
        self._energy = self._clamp(self._energy - self.ENERGY_PER_TICK)
        self._hp = self._clamp(self._hp + self._health_change())
        self._maybe_get_sick()

    def _health_change(self) -> int:
        """
        Считает изменение здоровья за тик

        :return: прирост здоровья (положительное число) или урон
            (отрицательное число)
        """
        if self._is_comfortable():
            return self.HEALTH_REGEN
        damage = 0
        if self._is_starving():
            damage += self.NEGLECT_DAMAGE
        if self._is_exhausted():
            damage += self.NEGLECT_DAMAGE
        if self._sick:
            damage += self.SICKNESS_DAMAGE
        return -damage

    def _maybe_get_sick(self) -> None:
        """Случайным образом заражает питомца; плохой уход повышает риск"""
        if self._sick:
            return
        risk_factors = sum((self._is_starving(), self._is_exhausted()))
        chance = (
            self._sickness_chance
            + self.RISK_SICKNESS_CHANCE * risk_factors
        )
        if self._rng.random() < chance:
            self._sick = True

    def _is_comfortable(self) -> bool:
        """
        Проверяет, хорошо ли питомцу: он здоров, сыт, бодр и не устал

        :return: True, если питомец в комфортном состоянии, иначе False
        """
        return (
            not self._sick
            and self._hunger < self.COMFORT_LEVEL
            and self._fatigue < self.COMFORT_LEVEL
            and self._energy >= self.COMFORT_LEVEL
        )

    def _is_starving(self) -> bool:
        """
        Проверяет, голодает ли питомец

        :return: True, если голод достиг критического уровня, иначе False
        """
        return self._hunger >= self.CRITICAL_LEVEL

    def _is_exhausted(self) -> bool:
        """
        Проверяет, измотан ли питомец

        :return: True, если усталость критическая или энергия на нуле,
            иначе False
        """
        return (
            self._fatigue >= self.CRITICAL_LEVEL
            or self._energy == self.MIN_LEVEL
        )

    def _ensure_alive(self) -> None:
        """
        Проверяет, что с питомцем ещё можно взаимодействовать

        :raises TamagochiIsGone: если питомец мёртв
        """
        if not self.is_alive():
            raise TamagochiIsGone(f'{self.name} умер. Игра окончена')

    @classmethod
    def _clamp(cls, value: int) -> int:
        """
        Ограничивает значение показателя допустимым диапазоном

        :param value: новое значение показателя
        :return: значение в диапазоне от MIN_LEVEL до MAX_LEVEL
        """
        return max(cls.MIN_LEVEL, min(cls.MAX_LEVEL, value))
