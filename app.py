from flask import Flask, request, redirect, url_for, render_template_string, Response
from database import init_db
import expenses
from datetime import datetime

app = Flask(__name__)

@app.template_filter("datetimeformat")
def datetimeformat(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").strftime("%m/%d/%Y")
    except:
        return value

# Initialize DB
init_db()

@app.route("/", methods=["GET"])
def home():
    search_query = request.args.get("search", "")
    category_filter = request.args.get("category", "")
    sort_by = request.args.get("sort", "")
    sort_dir = request.args.get("sort_dir", "asc")
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")


    all_expenses = expenses.get_expenses(search_query, category_filter, sort_by, sort_dir, start_date, end_date)
    total_amount = expenses.get_total(search_query, category_filter)

    return render_template_string("""
    <head>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>

    body {
        font-family: Arial, sans-serif;
        max-width: 900px;
        margin: 0 auto;
        padding: 20px;
        background-color: #f0f4fa;
    }
    h1, h2 {
        text-align: center;
        color: #1E3A8A; /* dark blue */
    }
    form {
        margin-bottom: 20px;
        padding: 15px;
        background: #fff;
        border-radius: 8px;
        box-shadow: 0 0 5px rgba(0,0,0,0.1);
    }
    input, select, button {
        padding: 8px 12px;
        margin: 5px 0;
        border-radius: 5px;
        border: 1px solid #ccc;
    }
    button {
        background-color: #2563EB; /* primary blue */
        color: white;
        border: none;
        cursor: pointer;
    }
    button:hover {
        background-color: #1D4ED8; /* darker blue */
    }
    table {
        width: 100%;
        border-collapse: collapse;
        background: #fff;
        border-radius: 8px;
        overflow: hidden;
    }
    th, td {
        padding: 12px;
        text-align: left;
    }
    th {
        background-color: #2563EB; /* header blue */
        color: white;
    }
    tr:nth-child(even) {
        background-color: #f2f6fc;
    }
        </style>
    </head>

    <h1>Expense Tracker</h1>

    <form action="/add" method="POST">
        Vendor: <input type="text" name="vendor" required><br>
        Date: <input type="date" name="date" required><br>
        Amount: <input type="number" step="0.01" name="amount" required><br>
        Category:
        <select name="category" required>
            <option value="Office Supplies">Office Supplies</option>
            <option value="Marketing / Advertising">Marketing / Advertising</option>
            <option value="Travel / Transport">Travel / Transport</option>
            <option value="Meals / Entertainment">Meals / Entertainment</option>
            <option value="Utilities / Internet">Utilities / Internet</option>
            <option value="Software / Subscriptions">Software / Subscriptions</option>
        </select><br>
        <button type="submit">Add Expense</button>
    </form>

    <h2>Saved Expenses</h2>

    <!-- Search + Category Filter -->
    <form method="GET" action="/">
        Search Vendor: <input type="text" name="search" value="{{ search_query }}">
        Category: 
            Start Date: <input type="date" name="start_date" value="{{ start_date }}">
            End Date: <input type="date" name="end_date" value="{{ end_date }}">
            Category:
            <select name="category">
                <option value="">All</option>
                <option value="Office Supplies" {% if category_filter=="Office Supplies" %}selected{% endif %}>Office Supplies</option>
                <option value="Marketing / Advertising" {% if category_filter=="Marketing / Advertising" %}selected{% endif %}>Marketing / Advertising</option>
                <option value="Travel / Transport" {% if category_filter=="Travel / Transport" %}selected{% endif %}>Travel / Transport</option>
                <option value="Meals / Entertainment" {% if category_filter=="Meals / Entertainment" %}selected{% endif %}>Meals / Entertainment</option>
                <option value="Utilities / Internet" {% if category_filter=="Utilities / Internet" %}selected{% endif %}>Utilities / Internet</option>
                <option value="Software / Subscriptions" {% if category_filter=="Software / Subscriptions" %}selected{% endif %}>Software / Subscriptions</option>
            </select>
            <button type="submit">Filter</button>
        </form>

    <!-- Sorting -->
    <form method="GET" action="/">
        <input type="hidden" name="search" value="{{ search_query }}">
        <input type="hidden" name="category" value="{{ category_filter }}">
        Sort by:
        <select name="sort" id="sortSelect">
            <option value="">Default</option>
            <option value="vendor" {% if request.args.get('sort')=='vendor' %}selected{% endif %}>Vendor</option>
            <option value="date" {% if request.args.get('sort')=='date' %}selected{% endif %}>Date</option>
            <option value="amount" {% if request.args.get('sort')=='amount' %}selected{% endif %}>Amount</option>
        </select>
        <select name="sort_dir" id="sortDirSelect" style="display: {% if request.args.get('sort')=='amount' %}inline{% else %}none{% endif %};">
            <option value="asc" {% if request.args.get('sort_dir')=='asc' %}selected{% endif %}>Low → High</option>
            <option value="desc" {% if request.args.get('sort_dir')=='desc' %}selected{% endif %}>High → Low</option>
        </select>
        <button type="submit">Sort</button>
    </form>

    <script>
    const sortSelect = document.getElementById('sortSelect');
    const sortDirSelect = document.getElementById('sortDirSelect');
    sortSelect.addEventListener('change', () => {
        sortDirSelect.style.display = sortSelect.value === 'amount' ? 'inline' : 'none';
    });
    </script>

    <br>
    <table border="1">
        <tr><th>Vendor</th><th>Date</th><th>Amount</th><th>Category</th><th>Actions</th></tr>
        {% for expense in expenses %}
        <tr>
            <td>{{ expense[1] }}</td>
            <td>{{ expense[2] | datetimeformat }}</td>
            <td>{{ expense[3] }}</td>
            <td>{{ expense[4] }}</td>
            <td>
                <a href="/edit/{{ expense[0] }}" style="text-decoration:none;">
                    <button style="background:none; border:none; cursor:pointer; font-size:18px; color:#2563EB;">
                        <i class="fa-solid fa-pen"></i>
                    </button>
                </a>
                <form action="/delete/{{ expense[0] }}" method="POST" style="display:inline;">
                    <button style="background:none; border:none; cursor:pointer; font-size:18px; color:#DC2626;">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </form>
            </td>
        </tr>
        {% endfor %}
    </table>

    <div style="margin-top:20px; padding:10px; border:1px solid #ccc; width:200px;">
        <strong>Total Expenses:</strong> ${{ "%.2f"|format(total_amount) }}
    </div>

    <!-- CSV Export -->
    <form method="GET" action="/export">
        <input type="hidden" name="search" value="{{ search_query }}">
        <input type="hidden" name="category" value="{{ category_filter }}">
        <input type="hidden" name="sort" value="{{ request.args.get('sort','') }}">
        <input type="hidden" name="sort_dir" value="{{ request.args.get('sort_dir','asc') }}">
        <button type="submit">Download CSV</button>
    </form>
        """, expenses=all_expenses, search_query=search_query,
            category_filter=category_filter, total_amount=total_amount,
            start_date=start_date, end_date=end_date)


@app.route("/add", methods=["POST"])
def add():
    vendor = request.form["vendor"]
    date = request.form["date"]
    amount = request.form["amount"]
    category = request.form["category"]
    expenses.add_expense(vendor, date, amount, category)
    return redirect(url_for("home"))

@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete(expense_id):
    expenses.delete_expense(expense_id)
    return redirect(url_for("home"))

@app.route("/edit/<int:expense_id>", methods=["GET","POST"])
def edit(expense_id):
    if request.method=="POST":
        vendor = request.form["vendor"]
        date = request.form["date"]
        amount = request.form["amount"]
        category = request.form["category"]
        expenses.update_expense(expense_id, vendor, date, amount, category)
        return redirect(url_for("home"))
    else:
        expense = expenses.get_expense(expense_id)
        return render_template_string("""
        <h1>Edit Expense</h1>
        <form action="/edit/{{ id }}" method="POST">
            Vendor: <input type="text" name="vendor" value="{{ expense[0] }}" required><br>
            Date: <input type="date" name="date" value="{{ expense[1] }}" required><br>
            Amount: <input type="number" step="0.01" name="amount" value="{{ expense[2] }}" required><br>
            Category: 
            <select name="category" required>
                <option value="Office Supplies" {% if expense[3]=="Office Supplies" %}selected{% endif %}>Office Supplies</option>
                <option value="Marketing / Advertising" {% if expense[3]=="Marketing / Advertising" %}selected{% endif %}>Marketing / Advertising</option>
                <option value="Travel / Transport" {% if expense[3]=="Travel / Transport" %}selected{% endif %}>Travel / Transport</option>
                <option value="Meals / Entertainment" {% if expense[3]=="Meals / Entertainment" %}selected{% endif %}>Meals / Entertainment</option>
                <option value="Utilities / Internet" {% if expense[3]=="Utilities / Internet" %}selected{% endif %}>Utilities / Internet</option>
                <option value="Software / Subscriptions" {% if expense[3]=="Software / Subscriptions" %}selected{% endif %}>Software / Subscriptions</option>
            </select><br>
            <button type="submit">Update</button>
        </form>
        """, expense=expense, id=expense_id)

@app.route("/export")
def export_csv():
    search_query = request.args.get("search", "")
    category_filter = request.args.get("category", "")
    sort_by = request.args.get("sort", "")
    sort_dir = request.args.get("sort_dir", "asc")
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")

    all_expenses = expenses.get_expenses(
    search_query, category_filter, sort_by, sort_dir, start_date, end_date)

    def generate():
        yield "Vendor,Date,Amount,Category\n"
        for exp in all_expenses:
            vendor = exp[1]
            try:
                date = datetime.strptime(exp[2], "%Y-%m-%d").strftime("%m/%d/%Y")
            except:
                date = exp[2]
            amount = f"{float(exp[3]):.2f}"
            category = exp[4]
            yield f'"{vendor}","{date}","{amount}","{category}"\n'

    return Response(generate(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=expenses.csv"})

if __name__ == "__main__":
    import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # use Render's PORT or default to 5000 locally
    app.run(host="0.0.0.0", port=port, debug=True)


from datetime import datetime

@app.template_filter('datetimeformat')
def datetimeformat(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").strftime("%d/%m/%Y")
    except:
        return value  # fallback in case format is unexpected
    