from database import get_connection

def add_expense(vendor, date, amount, category):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (vendor, date, amount, category) VALUES (?, ?, ?, ?)",
        (vendor, date, amount, category)
    )
    conn.commit()
    conn.close()

def get_expenses(search="", category="", sort_by="", sort_dir="asc", start_date="", end_date=""):
    query = "SELECT * FROM expenses WHERE 1=1"
    params = []

    if search:
        query += " AND vendor LIKE ?"
        params.append(f"%{search}%")

    if category:
        query += " AND category LIKE ?"
        params.append(f"%{category}%")

    if start_date:
        query += " AND date >= ?"
        params.append(start_date)

    if end_date:
        query += " AND date <= ?"
        params.append(end_date)

    if sort_by in ["vendor", "date", "amount", "category"]:
        query += f" ORDER BY {sort_by} {sort_dir.upper()}"

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results


def update_expense(expense_id, vendor, date, amount, category):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE expenses
        SET vendor = ?, date = ?, amount = ?, category = ?
        WHERE id = ?
    """, (vendor, date, amount, category, expense_id))
    conn.commit()
    conn.close()

def delete_expense(expense_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()

def get_expense(expense_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT vendor, date, amount, category FROM expenses WHERE id = ?", (expense_id,)
    )
    expense = cursor.fetchone()
    conn.close()
    return expense

def get_total(search="", category=""):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT SUM(amount) FROM expenses WHERE 1=1"
    params = []
    if search:
        query += " AND vendor LIKE ?"
        params.append(f"%{search}%")
    if category:
        query += " AND category = ?"
        params.append(category)
    cursor.execute(query, params)
    total = cursor.fetchone()[0] or 0
    conn.close()
    return total
