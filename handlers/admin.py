from aiogram import Router, F, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from models.database import get_all_orders, update_order_status

router = Router()

# === Переводчики значений ===
def translate_delivery(value):
    return "Доставка" if value == "delivery" else "Самовывоз"

def translate_option(value):
    return {
        "none": "Без доп. пожеланий",
        "with_note": "С пожеланием на торте"
    }.get(value, value)

def translate_cake(value):
    return {
        "bento": "Бенто торт",
        "full": "Полноразмерный торт"
    }.get(value, value)

def clean_prefix(value):
    return value.split("_")[-1] if "_" in value else value

# === Регистрация хендлеров ===
def register(dp, admin_ids):
    @router.message(F.text == "/orders")
    async def show_orders(msg: types.Message):
        if msg.from_user.id not in admin_ids:
            await msg.answer("⛔ У вас нет доступа к этой команде.")
            return

        orders = await get_all_orders(status_filter="Ожидает подтверждения")
        if not orders:
            await msg.answer("📭 Нет новых заказов.")
            return

        for order in orders:
            await send_order_summary(msg.bot, order, msg.chat.id)

    @router.callback_query(F.data.startswith("admin_confirm_"))
    async def confirm_order(call: types.CallbackQuery):
        order_id = int(call.data.split("_")[-1])
        await update_order_status(order_id, "Подтверждён ✅")
        await call.message.edit_text(f"✅ Заказ #{order_id} подтверждён.")

        orders = await get_all_orders(id_filter=order_id)
        if orders:
            uid = orders[0][1]  # user_id
            await call.bot.send_message(
                chat_id=uid,
                text=f"🎉 Ваш заказ #{order_id} подтверждён! Мы начали его приготовление 🧁"
            )

    @router.callback_query(F.data.startswith("admin_reject_"))
    async def reject_order(call: types.CallbackQuery):
        order_id = int(call.data.split("_")[-1])
        await update_order_status(order_id, "Отклонён ❌")
        await call.message.edit_text(f"❌ Заказ #{order_id} отклонён.")

    dp.include_router(router)

# === Общая функция отправки описания заказа ===
async def send_order_summary(bot, order, chat_id):
    order_id, uid, uname, cake, fill, bis, size, qty, opt, delivery, addr, status, feedback, created = order
    text = f"""📦 Заказ #{order_id} от {uname}:
🍰 Торт: {translate_cake(cake)}
🥄 Начинка: {clean_prefix(fill)}
🍪 Коржи: {clean_prefix(bis)}
📏 Размер: {clean_prefix(size)}
🔢 Количество: {qty}
🎁 Опции: {translate_option(opt)}
🚚 Доставка: {translate_delivery(delivery)}
🏠 Адрес: {addr if delivery == "delivery" else "Самовывоз"}
📅 Статус: {status}"""
    if feedback:
        text += f"\n💬 Пожелание: {feedback}"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"admin_confirm_{order_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"admin_reject_{order_id}")
        ]
    ])
    await bot.send_message(chat_id=chat_id, text=text, reply_markup=kb)
