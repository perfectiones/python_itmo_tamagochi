"""Модуль с исключениями"""


class TamagochiGameError(Exception):
    """Базовая ошибка игры: действие не может быть выполнено"""


class TamagochiIsGone(TamagochiGameError):
    """Ошибка при смерти тамагочи"""


class NotEnoughMoney(TamagochiGameError):
    """Ошибка когда не хватает монет для покупки"""


class TamagochiIsTired(TamagochiGameError):
    """Ошибка, когда питомцу не хватает энергии для игры"""


class MedicineIsOver(TamagochiGameError):
    """Ошибка при попытке применить закончившееся лекарство"""


class NoItemsToChoose(TamagochiGameError):
    """Ошибка, когда выбирать не из чего: сумка или магазин пусты"""


class WrongChoice(TamagochiGameError):
    """Ошибка при выборе несуществующего пункта меню"""


class ActionCancelled(TamagochiGameError):
    """Игрок отменил действие"""
