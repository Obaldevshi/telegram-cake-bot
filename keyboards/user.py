from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_delivery_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚚 Доставка", callback_data="delivery")],
        [InlineKeyboardButton(text="🏃 Самовывоз", callback_data="pickup")]
    ])

def get_cake_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Бенто торт", callback_data="bento")],
        [InlineKeyboardButton(text="Полноразмерный торт", callback_data="full")]
    ])

def get_filling_kb():
    fillings = ["Вишня", "Груша", "Шоколад", "Карамель", "Сникерс"]
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=fl, callback_data=f"filling_{fl}") for fl in fillings]
    ])

def get_biscuit_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Ванильный", callback_data="biscuit_Ванильный")],
        [InlineKeyboardButton(text="Шоколадный", callback_data="biscuit_Шоколадный")]
    ])

def get_size_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Маленький", callback_data="small")],
        [InlineKeyboardButton(text="Средний", callback_data="medium")],
        [InlineKeyboardButton(text="Большой", callback_data="large")]
    ])

def get_quantity_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1", callback_data="1"),
         InlineKeyboardButton(text="2", callback_data="2"),
         InlineKeyboardButton(text="3", callback_data="3")]
    ])

def get_options_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Без доп. пожеланий", callback_data="none")],
        [InlineKeyboardButton(text="С пожеланием на торте", callback_data="with_note")]
    ])

def get_new_order_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить заказ", callback_data="confirm_order")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_order")]
    ])
