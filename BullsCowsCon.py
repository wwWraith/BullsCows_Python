import random
import re
import sys
import textwrap
from os import system, get_terminal_size

# Показывать ли загаданное компьютером число
CHEAT_MODE = False
# Если не пустая строка, то компьютер загадывает и постоянно выбирает это число
TEST_NUMBER = ""

# Количество цифр в числе
NUM_DIGITS = 4
# Используемые цифры
DIGITS = "0123456789"
# Запрещать ли первую цифру из списка в начале числа
NO_LEADING_ZERO = True
# Вероятность выбора компьютером в свой ход просто случайного числа (от 0 до 1)
RANDOM_GUESS_CHANCE = 0.2

# Максимально допустимая длина строк для переноса при выводе
MAX_LINE_LENGTH = 80
# Использовать ли цветной режим
USE_COLOR_MODE = True

if USE_COLOR_MODE:
    # Коды цветов ANSI для терминала
    COLOR_RED = "\033[31m"
    COLOR_GREEN = "\033[32m"
    COLOR_YELLOW = "\033[33m"
    COLOR_RESET = "\033[0m"
    # Шаблон цветовых кодов ANSI
    COLOR_PATTERN = re.compile(r"\x1b\[\d+m")
else:
    COLOR_RED = COLOR_GREEN = COLOR_YELLOW = COLOR_RESET = ""


def red(s: str):
    """
    Окрашивает строку в красный цвет.
    Возвращает исходную строку с добавленными кодами ANSI.
    :param s: исходная строка
    :return: строка с добавленными кодами ANSI
    """
    return f"{COLOR_RED}{s}{COLOR_RESET}"


def green(s: str):
    """
    Окрашивает строку в зелёный цвет.
    Возвращает исходную строку с добавленными кодами ANSI.
    :param s: исходная строка
    :return: строка с добавленными кодами ANSI
    """
    return f"{COLOR_GREEN}{s}{COLOR_RESET}"


def yellow(s: str):
    """
    Окрашивает строку в жёлтый цвет.
    Возвращает исходную строку с добавленными кодами ANSI.
    :param s: исходная строка
    :return: строка с добавленными кодами ANSI
    """
    return f"{COLOR_YELLOW}{s}{COLOR_RESET}"


# Текст правил игры
RULES_TEXT = (
    f"Правила:\n\n"
    f"  Двое игроков (человек и компьютер) загадывают по числу, состоящему из "
    f"{yellow(f'{NUM_DIGITS} разных цифр')}"
    f"{f' и {yellow(f'не начинающемуся с {DIGITS[0]}')}' if NO_LEADING_ZERO else ''}. "
    f"Допустимые цифры: {yellow(DIGITS)}.\n"
    f"  Затем они пытаются угадать число, загаданное соперником. Для этого они каждый "
    f"ход называют числа, составленные по тем же правилам.\n"
    f"  Если в загаданном числе соперника есть цифра из тех, что были названы при "
    f"""данной попытке - это {yellow('"корова"')}; если, кроме того, эти цифры стоят """
    f"""на одинаковых позициях - это {yellow('"бык"')}.\n"""
    f'  Количество "быков" и "коров" подсчитывается и сообщается игрокам, и, исходя из '
    f"этой информации, делаются следующие попытки, пока не будет угадано одно из "
    f"загаданных чисел (или оба).\n"
)
# Текст подсказки для пользователя при необходимости повторить ввод числа
INPUT_HINT = (
    f"Ошибка! Введите число, состоящее из {NUM_DIGITS} разных цифр ({DIGITS})"
    f"{f' и не начинающееся с {DIGITS[0]}' if NO_LEADING_ZERO else ''}: "
)


def color_len(s: str):
    """
    Рассчитывает длину строки, игнорируя цветовые коды ANSI.
    :param s: исходная строка
    :return: длина строки без учёта цветовых кодов ANSI
    """
    return len(COLOR_PATTERN.sub("", s))


def line_length():
    """
    Определяет максимальную длину строк для переноса при печати.
    :return: выбранная максимальная длина строк для переноса при печати
    """
    try:
        size = get_terminal_size().columns
    except OSError:
        size = MAX_LINE_LENGTH
    return min(size, MAX_LINE_LENGTH)


def print_rules():
    """
    Выводит на экран описание игры и правил.
    """
    line_length_to_use = line_length()
    print(
        f"""Игра {yellow('"Быки и коровы"')}.""".center(
            line_length_to_use + len(COLOR_YELLOW + COLOR_RESET)
        )
        + "\n"
    )
    print(
        "\n".join(
            textwrap.fill(s, width=line_length_to_use) for s in RULES_TEXT.splitlines()
        )
    )
    print(f"\nДля {yellow('выхода')} из игры введите {yellow('0')}.")


def number_choice():
    """
    Генерирует случайное число, соответствующее правилам игры.
    :return: случайное число, соответствующее правилам игры
    """
    # Копируем строку с допустимыми цифрами в список
    digits_list = list(DIGITS)
    # Первая цифра из списка может быть выбрана первой цифрой числа
    # в зависимости от NO_LEADING_ZERO;
    # использованная цифра удаляется из списка для генерации
    num = digits_list.pop(
        random.randint(1 if NO_LEADING_ZERO else 0, len(digits_list) - 1)
    )
    for n in range(NUM_DIGITS - 1):
        # Добавляем оставшиеся цифры;
        # использованные цифры удаляются из списка для генерации
        num += digits_list.pop(random.randint(0, len(digits_list) - 1))
    return num


def number_is_ok(number: str):
    """
    Проверяет, соответствует ли число правилам игры.
    :param number: строка с проверяемым числом
    :return: True, если аргумент соответствует правилам, иначе False
    """
    # Если количество цифр верное и первая цифра числа - не первая из списка допустимых
    # (в зависимости от NO_LEADING_ZERO), то число может подойти
    if len(number) == NUM_DIGITS and (number[0] != DIGITS[0] or not NO_LEADING_ZERO):
        for digit in number:
            # Если любая из цифр отсутствует в списке допустимых или повторяется,
            # то число не подходит
            if digit not in DIGITS or number.count(digit) > 1:
                return False
        return True
    else:
        return False


def count_bulls_cows(number1: str, number2: str):
    """
    Подсчитывает количество "быков" и "коров" в 2 числах.
    :param number1: строка с первым числом
    :param number2: строка со вторым числом
    :return: кортеж из 2 чисел: количества "быков" и "коров"
    """
    bulls = cows = 0
    for n in range(NUM_DIGITS):
        # Если одинаковые цифры стоят на одинаковых местах, то это "бык"
        if number1[n] == number2[n]:
            bulls += 1
        # Иначе, если цифры просто одинаковые, то это "корова"
        elif number1[n] in number2:
            cows += 1
    return bulls, cows


# Счётчик ходов
turn: int = 0
# Список попыток компьютера
comp_guesses: list[str] = []
# Список попыток пользователя
user_guesses: list[str] = []
# Список "быков" в попытках компьютера
comp_bulls: list[int] = []
# Список "коров" в попытках компьютера
comp_cows: list[int] = []
# Список "быков" в попытках пользователя
user_bulls: list[int] = []
# Список "коров" в попытках пользователя
user_cows: list[int] = []
# Флаг окончания игры
game_over: bool = False

# При необходимости устанавливаем цветной режим
if USE_COLOR_MODE:
    # Переводим терминал в цветной режим
    system("color")
    # Заставляем textwrap рассчитывать длину строк, игнорируя цветовые коды ANSI
    textwrap.len = color_len

# Проверяем корректность правил
if len(DIGITS) < NUM_DIGITS or len(DIGITS) == 1 or NO_LEADING_ZERO and len(DIGITS) == 2:
    print(
        red("Ошибка в установленных правилах!")
        + "\nДопустимых цифр меньше, чем требуется в числах. Игра невозможна."
    )
    input(f"Нажмите {yellow('Enter')} для выхода...")
    sys.exit("Invalid configuration")

# Основной цикл игры
while True:
    turn += 1
    if turn == 1:
        # Очистка экрана терминала и вывод правил
        system("cls||clear")
        print_rules()
        # Компьютер "загадывает" случайное число, соответствующее правилам игры
        comp_number = number_choice()
        if TEST_NUMBER:
            comp_number = TEST_NUMBER
        if CHEAT_MODE:
            print(f"Компьютер загадал число {comp_number}")
        # Пользователь вводит загаданное число
        user_number = input("\nВведите число, которое хотите загадать: ")
        # Если пользователь ввёл 0, то играть не будем
        if user_number == "0":
            break
        # Если число не соответствует правилам игры, то просим повторить
        while not number_is_ok(user_number) and user_number != "0":
            user_number = input(INPUT_HINT)
        # Если пользователь ввёл 0, то играть не будем
        if user_number == "0":
            break

    # Пользователь вводит свою попытку
    user_guess = input(f"\nХод: {turn:2d}. Введите число: ")
    # Если число не соответствует правилам игры, то просим повторить
    while not number_is_ok(user_guess) and user_guess != "0":
        user_guess = input(INPUT_HINT)
    # Если пользователь ввёл 0, то завершаем игру
    if user_guess == "0":
        break
    user_guesses.append(user_guess)

    # Компьютер выбирает случайное число, соответствующее правилам игры
    comp_guess = number_choice()
    # Если нужно, повторяем, пока выбранное число не будет соответствовать полученной
    # в предыдущих попытках информации
    if random.random() >= RANDOM_GUESS_CHANCE and turn > 1:
        comp_guess_is_bad = True
        while comp_guess_is_bad:
            comp_guess_is_bad = False
            for t in range(turn - 1):
                bulls_temp, cows_temp = count_bulls_cows(comp_guess, comp_guesses[t])
                # Если количество "быков" и "коров" не соответствует хотя бы одной из
                # предыдущих попыток, то выбрать другое число
                if bulls_temp != comp_bulls[t] or cows_temp != comp_cows[t]:
                    comp_guess_is_bad = True
                    comp_guess = number_choice()
                    break
    if TEST_NUMBER:
        comp_guess = TEST_NUMBER
    comp_guesses.append(comp_guess)

    # Подсчитываем количества "коров" и "быков" и добавляем их в соответствующие списки
    # noinspection PyUnboundLocalVariable
    comp_bulls_last, comp_cows_last = count_bulls_cows(comp_guess, user_number)
    # noinspection PyUnboundLocalVariable
    user_bulls_last, user_cows_last = count_bulls_cows(user_guess, comp_number)
    comp_bulls.append(comp_bulls_last)
    comp_cows.append(comp_cows_last)
    user_bulls.append(user_bulls_last)
    user_cows.append(user_cows_last)

    # Очистка экрана терминала и вывод правил
    system("cls||clear")
    print_rules()
    print(f"\nЗагадано: {yellow(user_number)}")
    if CHEAT_MODE:
        print(f"Компьютер загадал число {comp_number}")
    # Выводим заголовок таблицы ходов
    print(f"\n     Ход  {red('Комп')}  Б  К     {green('Вы')}   Б  К")
    for t in range(turn):
        # Выводим строки таблицы ходов
        print(
            f"     {t + 1:2d}   {comp_guesses[t]}  {comp_bulls[t]}  {comp_cows[t]}    "
            f"{user_guesses[t]}  {user_bulls[t]}  {user_cows[t]}"
        )

    # Проверяем условия окончания игры
    if comp_bulls_last == user_bulls_last == NUM_DIGITS:
        print(f"\n{yellow('Ничья на')} {turn} {yellow('ходу! Победила дружба!')}")
        if turn == 1:
            print("Невероятное совпадение!")
        game_over = True
    elif user_bulls_last == NUM_DIGITS:
        print(f"\n{green('Вы выиграли на')} {turn} {green('ходу! Поздравляю!')}")
        if turn == 1:
            print("Потрясающая интуиция!")
        game_over = True
    elif comp_bulls_last == NUM_DIGITS:
        print(f"\n{red('Компьютер выиграл на')} {turn} {red('ходу! Сочувствую...')}")
        if turn == 1:
            print("Досадная случайность...")
        print(f"Загаданное компьютером число: {comp_number}")
        game_over = True
    if game_over:
        if comp_number == user_number:
            print("Загаданные числа одинаковы - кто бы мог подумать!")
        if (
            input(
                f"\nСпасибо за игру!\nНажмите {yellow('Enter')}, чтобы сыграть снова, "
                f"или введите {yellow('0')} для выхода: "
            )
            == "0"
        ):
            break
        else:
            turn = 0
            comp_guesses.clear()
            user_guesses.clear()
            comp_bulls.clear()
            comp_cows.clear()
            user_bulls.clear()
            user_cows.clear()
            game_over = False
