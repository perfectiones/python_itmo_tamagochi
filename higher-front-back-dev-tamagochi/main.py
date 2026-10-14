"""Точка входа в игру «Тамагочи-кликер»"""

import os

from game.clicker import SimpleRandomClicker
from game.exceptions import TamagochiGameError
from game.game import AbstractGame, SimpleGame
from game.models import Food, Medicine
from game.tamagochi import SimpleTamagochi


def clear_screen() -> None:
    """Очищает консоль: cls в Windows, clear в остальных системах"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_game_state(game: AbstractGame) -> None:
    """
    Выводит содержимое сумок и показатели питомца

    :param game: текущая игра
    """
    print(f"Сумка с едой: {game.food}")
    print(f"Сумка с лекарствами: {game.medicine}")

    status = game.get_status()
    print(
        f"\nСтатус: голод {status['hunger']}, "
        f"усталость {status['fatigue']}, здоровье {status['hp']}, "
        f"энергия {status['energy']}, монет {status['coins']}\n"
    )
    if game.tamagochi.is_sick():
        print("=======Тамагочи болеет======")
        print("=======Отдых действует менее эффективно=======")


def print_menu() -> None:
    """Выводит список доступных действий"""
    print("1. Пойти на работу")
    print("2. Купить еду")
    print("3. Купить лекарство")
    print("4. Покормить")
    print("5. Вылечить")
    print("6. Играть")
    print("7. Отдых")
    print("0. Выход")


def perform_action(game: AbstractGame, action: str) -> str:
    """
    Выполняет выбранное игроком действие

    :param game: текущая игра
    :param action: номер действия из меню
    :return: сообщение для игрока о результате действия
    :raises TamagochiGameError: если действие выполнить не удалось
    """
    match action:
        case "1":
            income = game.work()
            game.tamagochi.update()
            return f'Вы заработали {income} монет'
        case "2":
            game.buy_food()
            return 'Еда куплена'
        case "3":
            game.buy_medicine()
            return 'Лекарство куплено'
        case "4":
            game.feed_tamagochi()
            return 'Питомец поел'
        case "5":
            game.heal_tamagochi()
            return 'Питомец принял лекарство'
        case "6":
            game.play_with_tamagochi()
            return 'Вы поиграли с питомцем'
        case "7":
            game.rest_tamagochi()
            return 'Питомец отдохнул'
        case _:
            return "Неверная команда"


def main() -> None:
    """Создаёт игру и запускает игровой цикл до выхода или смерти питомца"""
    all_food = [
        Food(name='Бургер', satiety=20, price=40),
        Food(name='Салат', satiety=10, price=20),
        Food(name='Яблоко', satiety=10, price=15)
    ]

    all_medicine = [
        Medicine(name='Ибупрофен', price=30, heal_hp=20, number_of_uses=2)
    ]

    tamagochi = SimpleTamagochi()
    clicker = SimpleRandomClicker(10, 20)
    game = SimpleGame(tamagochi, clicker, all_food=all_food, all_medicine=all_medicine)

    print("Добро пожаловать в Тамагочи-кликер!")
    output = ''

    while True:
        print(output)
        print_game_state(game)
        print_menu()

        try:
            action = input("Выберите действие: ")
            if action == "0":
                break
            output = perform_action(game, action)
        except TamagochiGameError as error:
            output = str(error)
        except (KeyboardInterrupt, EOFError):
            print("\nИгра прервана")
            break

        clear_screen()

        if not game.tamagochi.is_alive():
            print(output)
            print_game_state(game)
            print("Питомец умер. Игра окончена")
            break


if __name__ == "__main__":
    main()
