from itertools import permutations
from os import get_terminal_size, system
from random import choice, randint, random, sample
from re import compile
from sys import exit as sysexit
import textwrap

# Показывать ли загаданное компьютером число
CHEAT_MODE = False
# Если не пустая строка, то компьютер загадывает и постоянно выбирает это число
TEST_NUMBER = ""

# Количество цифр в числе
NUM_DIGITS = 4
# Строка с символами, допустимыми в качестве цифр
DIGITS = "0123456789"
# Запрещать ли появление первой цифры из списка в начале числа
NO_LEADING_ZERO = True

# Вероятность выбора компьютером в свой ход просто случайного числа (от 0 до 1)
RANDOM_GUESS_CHANCE = 0.2
# Ход, начиная с которого компьютер выбирает свою попытку через итератор
# подходящих размещений; если меньше 2, то этот алгоритм не используется
ITER_GUESS_START = 2
# Ход, начиная с которого компьютер выбирает свою попытку через список оставшихся
# подходящих размещений; если меньше 2, то этот алгоритм не используется
LIST_GUESS_START = 3

# Максимально допустимая длина строк для переноса при выводе
MAX_LINE_LENGTH = 80
# Использовать ли цветной режим терминала
USE_COLOR_MODE = True
# Строка, ввод которой пользователем вызывает выход из игры
EXIT_KEY = "0"

if USE_COLOR_MODE:
    # Коды цветов ANSI для терминала
    COLOR_RED = "\033[31m"
    COLOR_GREEN = "\033[32m"
    COLOR_YELLOW = "\033[33m"
    COLOR_RESET = "\033[0m"
    # Шаблон цветовых кодов ANSI
    COLOR_PATTERN = compile(r"\x1b\[\d+m")
else:
    COLOR_RED = COLOR_GREEN = COLOR_YELLOW = COLOR_RESET = ""


def red(s: str) -> str:
    """
    Окрашивает строку в красный цвет.
    Возвращает исходную строку с добавленными кодами ANSI.
    :param s: исходная строка
    :return: строка с добавленными кодами ANSI
    """
    return f"{COLOR_RED}{s}{COLOR_RESET}"


def green(s: str) -> str:
    """
    Окрашивает строку в зелёный цвет.
    Возвращает исходную строку с добавленными кодами ANSI.
    :param s: исходная строка
    :return: строка с добавленными кодами ANSI
    """
    return f"{COLOR_GREEN}{s}{COLOR_RESET}"


def yellow(s: str) -> str:
    """
    Окрашивает строку в жёлтый цвет.
    Возвращает исходную строку с добавленными кодами ANSI.
    :param s: исходная строка
    :return: строка с добавленными кодами ANSI
    """
    return f"{COLOR_YELLOW}{s}{COLOR_RESET}"


# Текст правил игры
RULES_TEXT = (
    f"{yellow('Правила')}:\n\n"
    f"  Двое игроков (человек и компьютер) загадывают по числу, состоящему из "
    f"{green(f'{NUM_DIGITS} разных цифр')}"
    f"{f' и {red(f"не начинающемуся с {DIGITS[0]}")}' if NO_LEADING_ZERO else ''}. "
    f"Допустимые цифры: {green(DIGITS)}.\n"
    f"  Затем они пытаются угадать число, загаданное соперником. Для этого они каждый "
    f"ход называют числа, составленные по тем же правилам.\n"
    f"  Если в загаданном числе соперника есть цифра из тех, что были названы при "
    f"данной попытке — это {yellow('«корова»')}; если, кроме того, эти цифры стоят "
    f"на одинаковых позициях — это {yellow('«бык»')}.\n"
    f"  Количество «быков» и «коров» подсчитывается и сообщается игрокам, и, исходя из "
    f"этой информации, делаются следующие попытки, пока не будет угадано одно из "
    f"загаданных чисел (или оба).\n"
)
# Текст подсказки для пользователя при необходимости повторить ввод числа
INPUT_HINT = (
    f"{red('Ошибка!')} Введите число, состоящее из {green(f'{NUM_DIGITS} разных цифр')}"
    f" ({green(DIGITS)})"
    f"{f'\nи {red(f"не начинающееся с {DIGITS[0]}")}' if NO_LEADING_ZERO else ''} "
    f"(или {red(EXIT_KEY)} для выхода): "
)


def color_len(s: str) -> int:
    """
    Рассчитывает длину строки, игнорируя цветовые коды ANSI.
    :param s: исходная строка
    :return: длина строки без учёта цветовых кодов ANSI
    """
    return len(COLOR_PATTERN.sub("", s))


def line_length() -> int:
    """
    Определяет максимальную длину строк для переноса при печати.
    :return: выбранная максимальная длина строк для переноса при печати
    """
    try:
        size = get_terminal_size().columns
    except OSError:
        size = MAX_LINE_LENGTH
    return min(size, MAX_LINE_LENGTH)


def print_rules() -> None:
    """
    Выводит на экран описание и правила игры.
    """
    line_length_to_use = line_length()
    print(
        f"Игра {yellow('«Быки и коровы»')}.".center(
            line_length_to_use + len(COLOR_YELLOW + COLOR_RESET)
        )
        + "\n"
    )
    print(
        "\n".join(
            textwrap.fill(s, width=line_length_to_use) for s in RULES_TEXT.splitlines()
        )
    )
    print(f"\nДля {red('выхода')} из игры введите {red(EXIT_KEY)}.")


def number_choice() -> str:
    """
    Генерирует строку со случайным числом, соответствующим правилам игры.
    :return: строка со случайным числом, соответствующим правилам игры
    """
    # Копируем строку с допустимыми цифрами в список
    digits_list = list(DIGITS)
    # Первая цифра из списка может быть выбрана первой цифрой числа
    # в зависимости от NO_LEADING_ZERO;
    # использованная цифра удаляется из списка для генерации
    num = digits_list.pop(randint(1 if NO_LEADING_ZERO else 0, len(digits_list) - 1))
    # Добавляем остальные цифры
    num = f"{num}{''.join(sample(digits_list, NUM_DIGITS - 1))}"
    return num


def number_is_ok(number: str) -> bool:
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


def count_bulls_cows(number1: str, number2: str) -> tuple[int, int]:
    """
    Подсчитывает количество "быков" и "коров" в 2 числах.
    :param number1: строка с первым числом
    :param number2: строка со вторым числом
    :return: кортеж из 2 чисел: количество "быков" и "коров"
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


def guess_is_good(
    number: str, guesses_list: list[str], bulls_list: list[int], cows_list: list[int]
) -> bool:
    """
    Проверяет, соответствует ли попытка информации из предыдущих ходов.
    :param number: строка с проверяемым числом
    :param guesses_list: список из предыдущих попыток
    :param bulls_list: список из "быков" на предыдущих ходах
    :param cows_list: список из "коров" на предыдущих ходах
    :return: True, если попытка подходит, иначе False
    """
    for i in range(len(guesses_list)):
        # Если количество "быков" и "коров" не соответствует хотя бы одной
        # из предыдущих попыток, то попытка неудачная
        if count_bulls_cows(number, guesses_list[i]) != (bulls_list[i], cows_list[i]):
            return False
    return True


def guess_random(
    guesses_list: list[str], bulls_list: list[int], cows_list: list[int]
) -> str:
    """
    Выбирает случайным образом число, соответствующее информации из предыдущих ходов.
    :param guesses_list: список из предыдущих попыток.
    :param bulls_list: список из "быков" на предыдущих ходах
    :param cows_list: список из "коров" на предыдущих ходах
    :return: строка со случайным числом, соответствующим предыдущим попыткам
    """
    # Выбираем случайное число, соответствующее правилам игры
    guess = number_choice()
    # Если нужно, повторяем, пока выбранное число не будет соответствовать
    # полученной в предыдущих попытках информации
    while not guess_is_good(guess, guesses_list, bulls_list, cows_list):
        guess = number_choice()
    return guess


def guess_from_iterator(
    guesses_list: list[str], bulls_list: list[int], cows_list: list[int]
) -> str:
    """
    Выбирает число, соответствующее информации из предыдущих ходов, через итератор
    подходящих размещений.
    :param guesses_list: список из предыдущих попыток
    :param bulls_list: список из "быков" на предыдущих ходах
    :param cows_list: список из "коров" на предыдущих ходах
    :return: строка со случайным числом, соответствующим предыдущим попыткам
    """
    # Перемешиваем список допустимых цифр, чтобы затем получать размещения
    # в случайном порядке
    digits = "".join(sample(DIGITS, len(DIGITS)))
    # Получаем первое подходящее из возможных размещений
    guess = next(
        filter(
            # Соответствует ли текущее число правилам и информации из предыдущих ходов
            lambda s: number_is_ok(s)
            and guess_is_good(s, guesses_list, bulls_list, cows_list),
            # Итератор, перебирающий все возможные размещения и выдающий их строками
            map("".join, permutations(digits, NUM_DIGITS)),
        )
    )
    return guess


def guess_from_list(
    guesses_list: list[str],
    bulls_list: list[int],
    cows_list: list[int],
    choices_list: list[str],
) -> str:
    """
    Выбирает число, соответствующее информации из предыдущих ходов, через список
    оставшихся подходящих размещений choices_list, который при этом обновляется.
    :param guesses_list: список из предыдущих попыток
    :param bulls_list: список из "быков" на предыдущих ходах
    :param cows_list: список из "коров" на предыдущих ходах
    :param choices_list: список оставшихся подходящих размещений
    :return: строка со случайным числом, соответствующим предыдущим попыткам
    """
    # Если список оставшихся возможных размещений пока пуст, то заполняем его
    if not choices_list:
        # Отбираем из всех возможных размещений подходящие
        choices_list.extend(
            filter(
                # Соответствует ли текущее число правилам и информации
                # из предыдущих ходов
                lambda s: number_is_ok(s)
                and guess_is_good(s, guesses_list, bulls_list, cows_list),
                # Итератор, перебирающий все возможные размещения и выдающий их строками
                map("".join, permutations(DIGITS, NUM_DIGITS)),
            )
        )
    else:
        # Перебираем элементы имеющегося списка в обратном порядке
        # (для предотвращения смещения индексов после удалений)
        for i in range(len(choices_list) - 1, -1, -1):
            # Удаляем элементы, которые не соответствуют информации из предыдущих ходов
            if not guess_is_good(choices_list[i], guesses_list, bulls_list, cows_list):
                choices_list.pop(i)
    guess = choice(choices_list)
    return guess


def main():
    # Проверяем корректность правил
    if (
        len(DIGITS) < NUM_DIGITS
        or len(DIGITS) == 1
        or NO_LEADING_ZERO
        and len(DIGITS) == 2
    ):
        print(
            red("Ошибка в установленных правилах!")
            + "\nДопустимых цифр меньше, чем требуется в числах. Игра невозможна."
        )
        input(f"Нажмите {yellow('Enter')} для выхода...")
        sysexit("Invalid configuration")

    if USE_COLOR_MODE:
        # Заставляем textwrap рассчитывать длину строк, игнорируя цветовые коды ANSI
        textwrap.len = color_len

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
    # Список с оставшимися подходящими размещениями
    good_choices_list: list[str] = []
    # Флаг окончания игры
    game_over: bool = False
    # Счётчик ходов
    turn: int = 0

    # Основной цикл игры
    while True:
        turn += 1
        if turn == 1:
            # Очистка экрана терминала и вывод правил
            system("cls||clear")
            print_rules()
            # Компьютер "загадывает" случайное число, соответствующее правилам игры
            if TEST_NUMBER:
                comp_number = TEST_NUMBER
            else:
                comp_number = number_choice()
            if CHEAT_MODE:
                print(f"Компьютер загадал число {comp_number}")

            # Пользователь вводит загаданное число
            user_number = input("\nВведите число, которое хотите загадать: ")
            # Если число не соответствует правилам игры, то просим повторить
            while user_number != EXIT_KEY and not number_is_ok(user_number):
                user_number = input(INPUT_HINT)
            # Если пользователь ввёл EXIT_KEY, то выход из игры
            if user_number == EXIT_KEY:
                break

        # Пользователь вводит свою попытку
        user_guess = input(f"\nХод: {yellow(f'{turn:2d}')}. Введите число: ")
        # Если число не соответствует правилам игры, то просим повторить
        while user_guess != EXIT_KEY and not number_is_ok(user_guess):
            user_guess = input(INPUT_HINT)
        # Если пользователь ввёл EXIT_KEY, то выход из игры
        if user_guess == EXIT_KEY:
            break
        user_guesses.append(user_guess)

        # Компьютер выбирает число для своей попытки согласно соответствующему алгоритму
        # в зависимости от номера хода
        if TEST_NUMBER:
            comp_guess = TEST_NUMBER
        elif turn == 1 or random() < RANDOM_GUESS_CHANCE:
            # Случайный выбор
            comp_guess = number_choice()
        elif 2 <= LIST_GUESS_START <= turn:
            # Выбор через список оставшихся подходящих размещений
            comp_guess = guess_from_list(
                comp_guesses, comp_bulls, comp_cows, good_choices_list
            )
        elif 2 <= ITER_GUESS_START <= turn:
            # Выбор через итератор подходящих размещений
            comp_guess = guess_from_iterator(comp_guesses, comp_bulls, comp_cows)
        else:
            # Случайный подбор
            comp_guess = guess_random(comp_guesses, comp_bulls, comp_cows)
        comp_guesses.append(comp_guess)

        # Подсчитываем количество "быков" и "коров" и добавляем в соответствующие списки
        # noinspection PyUnboundLocalVariable
        comp_bulls_last, comp_cows_last = count_bulls_cows(comp_guess, user_number)
        comp_bulls.append(comp_bulls_last)
        comp_cows.append(comp_cows_last)
        # noinspection PyUnboundLocalVariable
        user_bulls_last, user_cows_last = count_bulls_cows(user_guess, comp_number)
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
                f"     {t + 1:2d}   {comp_guesses[t]}  {comp_bulls[t]}  {comp_cows[t]}"
                f"    {user_guesses[t]}  {user_bulls[t]}  {user_cows[t]}"
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
            print(
                f"\n{red('Компьютер выиграл на')} {turn} {red('ходу! Сочувствую...')}"
            )
            if turn == 1:
                print("Досадная случайность...")
            print(f"Загаданное компьютером число: {red(comp_number)}")
            game_over = True
        if game_over:
            if comp_number == user_number:
                print("Загаданные числа были одинаковыми — кто бы мог подумать!")
            if (
                input(
                    f"\n{yellow('Спасибо за игру!')}\nНажмите {green('Enter')}, чтобы "
                    f"сыграть снова, или введите {red(EXIT_KEY)} для выхода: "
                )
                == EXIT_KEY
            ):
                break
            else:
                comp_guesses.clear()
                user_guesses.clear()
                comp_bulls.clear()
                comp_cows.clear()
                user_bulls.clear()
                user_cows.clear()
                good_choices_list.clear()
                game_over = False
                turn = 0


if __name__ == "__main__":
    main()
