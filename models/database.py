import aiosqlite

DB_PATH = "cake_bot.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            user_name TEXT,
            cake_type TEXT,
            filling TEXT,
            biscuit TEXT,
            size TEXT,
            quantity INTEGER,
            options TEXT,
            delivery TEXT,
            address TEXT,
            status TEXT,
            feedback TEXT,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        await db.commit()

async def add_order(data: dict):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        INSERT INTO orders (user_id, user_name, cake_type, filling, biscuit, size, quantity, options, delivery, address, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['user_id'], data['user_name'], data['cake_type'], data['filling'],
            data['biscuit'], data['size'], data['quantity'], data['options'],
            data['delivery'], data['address'], data['status']
        ))
        await db.commit()

async def get_all_orders(status_filter: str = None, id_filter: int = None):
    async with aiosqlite.connect(DB_PATH) as db:
        query = "SELECT * FROM orders"
        params = []

        if status_filter:
            query += " WHERE status = ?"
            params.append(status_filter)

        if id_filter is not None:
            if "WHERE" in query:
                query += " AND id = ?"
            else:
                query += " WHERE id = ?"
            params.append(id_filter)

        query += " ORDER BY created DESC"

        cursor = await db.execute(query, params)
        return await cursor.fetchall()

async def update_order_status(order_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
        await db.commit()

async def save_feedback(user_id: int, feedback: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE orders
            SET feedback = ?
            WHERE user_id = ? AND feedback IS NULL
            ORDER BY created DESC LIMIT 1
        """, (feedback, user_id))
        await db.commit()
