from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, ReplyKeyboardMarkup, KeyboardButton
from models.database import add_order, save_feedback, get_all_orders
from keyboards.user import (
    get_delivery_kb, get_cake_kb, get_filling_kb, get_biscuit_kb,
    get_size_kb, get_quantity_kb, get_options_kb, get_new_order_kb
)
from utils.validators import is_valid_address
from handlers.admin import send_order_summary

ADMIN_CHAT_ID = 473088323  # сюда отправляются уведомления о заказах

router = Router()

class OrderCake(StatesGroup):
    delivery = State()
    address = State()
    cake = State()
    filling = State()
    biscuit = State()
    size = State()
    quantity = State()
    options = State()
    wish = State()
    confirm = State()

@router.message(F.text.lower() == "/start")
async def start_order(msg: Message, state: FSMContext):
    await state.clear()
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🧁 Заказать")]],
        resize_keyboard=True
    )
    await msg.answer("Добро пожаловать в кондитерскую!", reply_markup=kb)

@router.message(F.text == "🧁 Заказать")
async def begin_order(msg: Message, state: FSMContext):
    await msg.answer("Выберите способ получения:", reply_markup=get_delivery_kb())
    await state.set_state(OrderCake.delivery)

@router.callback_query(OrderCake.delivery)
async def choose_delivery(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(delivery=call.data)
    if call.data == "delivery":
        await call.message.edit_text("Введите адрес доставки:")
        await state.set_state(OrderCake.address)
    else:
        await call.message.edit_text("Выберите тип торта:", reply_markup=get_cake_kb())
        await state.set_state(OrderCake.cake)

@router.message(OrderCake.address)
async def enter_address(msg: Message, state: FSMContext):
    if not is_valid_address(msg.text):
        await msg.reply("Пожалуйста, введите корректный адрес (не менее 10 символов).")
        return
    await state.update_data(address=msg.text)
    await msg.answer("Выберите тип торта:", reply_markup=get_cake_kb())
    await state.set_state(OrderCake.cake)

@router.callback_query(OrderCake.cake)
async def choose_cake(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(cake_type=call.data)
    await call.message.edit_text("Выберите начинку:", reply_markup=get_filling_kb())
    await state.set_state(OrderCake.filling)

@router.callback_query(OrderCake.filling)
async def choose_filling(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(filling=call.data)
    await call.message.edit_text("Выберите тип коржей:", reply_markup=get_biscuit_kb())
    await state.set_state(OrderCake.biscuit)

@router.callback_query(OrderCake.biscuit)
async def choose_biscuit(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(biscuit=call.data)
    await call.message.edit_text("Выберите размер торта:", reply_markup=get_size_kb())
    await state.set_state(OrderCake.size)

@router.callback_query(OrderCake.size)
async def choose_size(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(size=call.data)
    await call.message.edit_text("Выберите количество:", reply_markup=get_quantity_kb())
    await state.set_state(OrderCake.quantity)

@router.callback_query(OrderCake.quantity)
async def choose_quantity(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(quantity=int(call.data))
    await call.message.edit_text("Дополнительные опции:", reply_markup=get_options_kb())
    await state.set_state(OrderCake.options)

@router.callback_query(OrderCake.options)
async def choose_options(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(options=call.data)
    if call.data == "with_note":
        await call.message.edit_text("Введите пожелание, которое будет написано на торте:")
        await state.set_state(OrderCake.wish)
    else:
        await call.message.edit_text("Подтвердите заказ:", reply_markup=get_new_order_kb())
        await state.set_state(OrderCake.confirm)

@router.message(OrderCake.wish)
async def enter_wish(msg: Message, state: FSMContext):
    await state.update_data(feedback=msg.text)
    await msg.answer("Подтвердите заказ:", reply_markup=get_new_order_kb())
    await state.set_state(OrderCake.confirm)

@router.callback_query(OrderCake.confirm, F.data == "confirm_order")
async def confirm_order(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order = {
        "user_id": call.from_user.id,
        "user_name": call.from_user.full_name,
        **data,
        "address": data.get("address", "Самовывоз"),
        "feedback": data.get("feedback", None),
        "status": "Ожидает подтверждения"
    }
    await add_order(order)
    await call.message.edit_text("🎉 Ваш заказ принят! Ожидайте подтверждения администратора.")
    await state.clear()

    # отправка уведомления администратору
    orders = await get_all_orders(status_filter="Ожидает подтверждения")
    if orders:
        await send_order_summary(call.bot, orders[0], ADMIN_CHAT_ID)

@router.callback_query(F.data == "cancel_order")
async def cancel_order(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("❌ Заказ отменён. Чтобы начать заново, нажмите /start")

@router.message(F.text.lower().startswith("оценка:") | F.text.lower().startswith("отзыв:"))
async def handle_feedback(msg: Message, state: FSMContext):
    feedback = msg.text.strip()
    await save_feedback(user_id=msg.from_user.id, feedback=feedback)
    await msg.answer("Спасибо за ваш отзыв! 💖 Мы стараемся для вас.")

@router.message(F.text.lower() == "оставить отзыв")
async def ask_feedback(msg: Message, state: FSMContext):
    await msg.answer("📢 Пожалуйста, напишите ваш отзыв в свободной форме. Начните сообщение со слова 'Отзыв:' или 'Оценка:'")

def register(dp):
    dp.include_router(router)
