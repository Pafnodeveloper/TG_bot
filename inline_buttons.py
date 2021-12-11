from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

layout = InlineKeyboardMarkup(row_width=2)

btn_yes = InlineKeyboardButton('Да', callback_data="yes")
btn_no = InlineKeyboardButton('Нет', callback_data="no")

layout.add(btn_yes, btn_no)
