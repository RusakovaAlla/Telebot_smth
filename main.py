import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Text
from config_reader import config
from random import choice

logging.basicConfig(level=logging.INFO)  # Включаем логирование, чтобы не пропустить важные сообщения
bot = Bot(token=config.bot_token.get_secret_value())  # Объект бота
dp = Dispatcher(bot)  # Диспетчер


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = ["Да", "Нет"]
    keyboard.add(*buttons)
    await message.reply("Привет!\n Теоретически вы тут можете складывать комплексные числа и вносить изменения "
                        "в телефонный справочник, но это пока в разработке, а пока..."
                        " сыграем в крестики-нолики?\n", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Да")
async def with_yes(message: types.Message):
    global button
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    button = []
    for i in range(1, 10):
        button_num = types.InlineKeyboardButton(" ", callback_data=f"place_{i}")
        button.append(button_num)
    keyboard.add(*button)
    await message.answer("Отлично! Погнали \n ")
    await message.answer(f"Проводим жеребьевку...🎲")
    players = [bot, message.from_user.first_name]
    global moves_order
    global move_options
    global bot_combos
    global user_combos
    user_combos, bot_combos = [], []
    move_options = list(range(1, 10))
    print(f"Это исходный список {move_options}")
    moves_order = [choice(players)]
    [moves_order.append(i) for i in players if i not in moves_order]
    moves_order.append(["X", "0"])
    if moves_order[0] == message.from_user.first_name:
        global mark_bot
        mark_bot = None
        await message.answer(f"Первый ход за вами", reply_markup=keyboard)
    else:
        first_move = choice(move_options)
        bot_combos.append(first_move)
        move_options.remove(first_move)
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        mark_bot = "Х"
        for enum, i in enumerate(button):
            if enum == first_move - 1:
                button_num = types.InlineKeyboardButton(mark_bot, callback_data=f"forbidden")
                button[enum] = button_num
                break
            else:
                continue
        keyboard.add(*button)
        # keyboard.add(*new_keyboard(callback_place, "Х", "forbidden"))
        await message.answer(f"Первым хожу я!", reply_markup=keyboard)


@dp.callback_query_handler(Text(startswith="place_"))
async def tic_tac_toe_mark(callback_place: types.CallbackQuery):
    winner = False
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    mark = "O" if moves_order.index(callback_place.from_user.first_name) == 1 else "X"
    user_combos.append(int(callback_place.data.split("_")[1]))  # добавили кнопку, нажатую пользователем в список
    move_options.remove(int(callback_place.data.split("_")[1]))  # удаляем кнопку из списка доступных
    for enum, i in enumerate(button):
        if enum == int(callback_place.data.split("_")[1]) - 1:
            button_num = types.InlineKeyboardButton(mark, callback_data=f"forbidden")
            button[enum] = button_num
            break
        else:
            continue
    keyboard.add(*button)
    await callback_place.message.edit_reply_markup(reply_markup=keyboard)
    if check4win(user_combos):
        winner = True
        await callback_place.message.answer(f'Вы победили! Поздравляю!')
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ["Да", "Нет"]
        keyboard.add(*buttons)
        await callback_place.message.answer("Сыграем еще раз?", reply_markup=keyboard)
        # стикер бы сюда
    else:
        await asyncio.sleep(1)
        # бот делает ход
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        bot_move = choice(move_options)
        bot_combos.append(bot_move)
        move_options.remove(bot_move)
        mark_bot = "X" if mark == "O" else "O"
        for enum, i in enumerate(button):
            if enum == bot_move - 1:
                button_num = types.InlineKeyboardButton(mark_bot, callback_data=f"forbidden")
                button[enum] = button_num
                break
            else:
                continue
        keyboard.add(*button)
        await callback_place.message.edit_reply_markup(reply_markup=keyboard)
        print(bot_combos)
        if check4win(bot_combos):
            winner = True
            await callback_place.message.answer(f'Я выиграл!')
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            buttons = ["Да", "Нет"]
            keyboard.add(*buttons)
            await callback_place.message.answer("Сыграем еще раз?", reply_markup=keyboard)
            # стикер бы сюда
        else:
            await callback_place.answer(f"Жду ваш ход")


@dp.callback_query_handler(Text("forbidden"))
async def no_mark(callback_answ: types.CallbackQuery):
    await callback_answ.answer(f"Клетка занята. Выберите другую.", show_alert=True)


@dp.message_handler(lambda message: message.text == "Нет")
async def with_no(message: types.Message):
    await message.answer("В другой раз...", reply_markup=types.ReplyKeyboardRemove())


def check4win(array):  # модернизированная функция из задачи
    """победные комбинации"""
    if len(array) >= 3:
        combos = [[1, 2, 3],
                  [4, 5, 6],
                  [7, 8, 9],
                  [1, 4, 7],
                  [2, 5, 8],
                  [3, 6, 9],
                  [1, 5, 9],
                  [3, 5, 7]]
        for combo in combos:
            if (combo[0] in array) and (combo[1] in array) and (combo[2] in array):
                return True
    else:
        return False


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot, reset_webhook=True)


if __name__ == "__main__":
    asyncio.run(main())
