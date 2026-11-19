import os
from dotenv import load_dotenv

import os

from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from extensions import db, login_manager
from datetime import datetime

load_dotenv()

EXPENSE_CATEGORIES = [
    "Food & Dining",
    "Groceries",
    "Transportation",
    "Fuel",
    "Shopping",
    "Rent",
    "Electricity & Bills",
    "Internet & Mobile",
    "Healthcare",
    "Education",
    "Entertainment",
    "Travel",
    "Personal Care",
    "Subscriptions",
    "Home & Maintenance",
    "Insurance",
    "Other Expenses"
]

INCOME_CATEGORIES = [
    "Salary",
    "Freelancing",
    "Business Income",
    "Investment Returns",
    "Interest",
    "Rental Income",
    "Gift",
    "Other Income"
]

app = Flask(__name__)

# Application configuration
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///expense_tracker.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Create instance directory if it doesn't exist
os.makedirs(app.instance_path, exist_ok=True)

# Initialize database and login manager
db.init_app(app)

login_manager.init_app(app)

login_manager.login_view = "login"

# Import models
from models import User, Expense


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route("/")
def home():
    return "Personal Expense Tracker Database Connected!"


# Create database tables
with app.app_context():
    db.create_all()


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # Check whether email already exists
        existing_user = db.session.execute(
            db.select(User).filter_by(email=email)
        ).scalar_one_or_none()

        if existing_user:
            flash("Email already registered!")
            return redirect(url_for("register"))

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Create a new user
        new_user = User(
            username=username,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please login.")

        return redirect(url_for("login"))

    return render_template("register.html")



@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = db.session.execute(
            db.select(User).filter_by(email=email)
        ).scalar_one_or_none()

        if user and check_password_hash(user.password, password):

            login_user(user)

            flash("Login successful!")

            return redirect(url_for("dashboard"))

        flash("Invalid email or password!")

    return render_template("login.html")




@app.route("/dashboard")
@login_required
def dashboard():

    user_id = current_user.id

    transactions = Expense.query.filter_by(
        user_id=user_id
    ).order_by(Expense.date.desc()).all()

    total_income = db.session.query(
        db.func.sum(Expense.amount)
    ).filter_by(
        user_id=user_id,
        transaction_type="income"
    ).scalar() or 0

    total_expenses = db.session.query(
        db.func.sum(Expense.amount)
    ).filter_by(
        user_id=user_id,
        transaction_type="expense"
    ).scalar() or 0

    
    balance = total_income - total_expenses

    recent_transactions = transactions[:5]

    
    # Get the current date
    today = datetime.now()

    # Find the first day of this month
    month_start = datetime(today.year, today.month, 1)

    # Find the first day of next month
    if today.month == 12:
        next_month = datetime(today.year + 1, 1, 1)
    else:
        next_month = datetime(today.year, today.month + 1, 1)


    # Calculate monthly income
    monthly_income = db.session.query(
        db.func.sum(Expense.amount)
    ).filter(
        Expense.user_id == user_id,
        Expense.transaction_type == "income",
        Expense.date >= month_start,
        Expense.date < next_month
    ).scalar() or 0


    # Calculate monthly expenses
    monthly_expenses = db.session.query(
        db.func.sum(Expense.amount)
    ).filter(
        Expense.user_id == user_id,
        Expense.transaction_type == "expense",
        Expense.date >= month_start,
        Expense.date < next_month
    ).scalar() or 0


    # Calculate monthly balance
    monthly_balance = monthly_income - monthly_expenses

    # Calculate expenses by category for this month     
    category_totals = db.session.query(
        Expense.category,
        db.func.sum(Expense.amount)
    ).filter(
        Expense.user_id == user_id,
        Expense.transaction_type == "expense",
        Expense.date >= month_start,
        Expense.date < next_month
    ).group_by(
        Expense.category
    ).all()

    category_labels = [row[0] for row in category_totals]
    category_amounts = [float(row[1]) for row in category_totals]

    # Get the last 6 months
    month_keys = []
    month_labels = []

    for i in range(5, -1, -1):
        year = today.year
        month = today.month - i

        while month <= 0:
            month += 12
            year -= 1

        month_keys.append(f"{year}-{month:02d}")

        month_labels.append(
            datetime(year, month, 1).strftime("%b %Y")
        )


    # Get income and expenses grouped by month
    monthly_data = db.session.query(
        db.func.strftime("%Y-%m", Expense.date).label("month"),
        Expense.transaction_type,
        db.func.sum(Expense.amount)
    ).filter(
        Expense.user_id == user_id,
        Expense.date >= datetime(
            int(month_keys[0][:4]),
            int(month_keys[0][5:7]),
            1
        ),
        Expense.date < next_month
    ).group_by(
        "month",
        Expense.transaction_type
    ).all()


    # Prepare chart data
    income_by_month = {}
    expenses_by_month = {}

    for month, transaction_type, amount in monthly_data:

        if transaction_type == "income":
            income_by_month[month] = float(amount)

        elif transaction_type == "expense":
            expenses_by_month[month] = float(amount)


    monthly_income_values = [
        income_by_month.get(month, 0)
        for month in month_keys
    ]

    monthly_expense_values = [
        expenses_by_month.get(month, 0)
        for month in month_keys
    ]

    return render_template(
        "dashboard.html",
        transactions=transactions,
        total_income=total_income,
        total_expenses=total_expenses,
        balance=balance,
        recent_transactions=recent_transactions,
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        monthly_balance=monthly_balance,
        category_labels=category_labels,
        category_amounts=category_amounts,
        month_labels=month_labels,
        monthly_income_values=monthly_income_values,
        monthly_expense_values=monthly_expense_values
    )




@app.route("/add-expense", methods=["GET", "POST"])
@login_required
def add_expense():

    if request.method == "POST":

        description = request.form.get("description", "").strip()
        category = request.form.get("category", "")
        transaction_type = request.form.get("transaction_type", "")

        # Validate transaction type
        if transaction_type not in ["income", "expense"]:
            flash("Invalid transaction type.")
            return redirect(url_for("add_expense"))

        # Select the correct category list
        if transaction_type == "expense":
            allowed_categories = EXPENSE_CATEGORIES
        else:
            allowed_categories = INCOME_CATEGORIES

        # Validate category
        if category not in allowed_categories:
            flash("Invalid category for this transaction type.")
            return redirect(url_for("add_expense"))

        # Validate description
        if not description:
            flash("Description is required.")
            return redirect(url_for("add_expense"))

        # Validate amount
        try:
            amount = float(request.form.get("amount", ""))
        except ValueError:
            flash("Please enter a valid amount.")
            return redirect(url_for("add_expense"))

        if not 0 < amount < float("inf"):
            flash("Amount must be greater than zero.")
            return redirect(url_for("add_expense"))

        # Validate date
        try:
            date = datetime.strptime(
                request.form.get("date", ""), "%Y-%m-%d"
            )
        except ValueError:
            flash("Please enter a valid date.")
            return redirect(url_for("add_expense"))

        new_expense = Expense(
            description=description,
            amount=amount,
            category=category,
            transaction_type=transaction_type,
            date=date,
            user_id=current_user.id
        )

        db.session.add(new_expense)
        db.session.commit()

        flash("Transaction added successfully!")

        return redirect(url_for("dashboard"))

    return render_template("add_expense.html")


@app.route("/edit-expense/<int:expense_id>", methods=["GET", "POST"])
@login_required
def edit_expense(expense_id):

    expense = Expense.query.filter_by(
        id=expense_id,
        user_id=current_user.id
    ).first_or_404()

    if request.method == "POST":

        description = request.form.get("description", "").strip()
        category = request.form.get("category", "")
        transaction_type = request.form.get("transaction_type", "")

        # Validate transaction type
        if transaction_type not in ["income", "expense"]:
            flash("Invalid transaction type.")
            return redirect(url_for(
                "edit_expense", expense_id=expense.id
            ))

        # Select the correct category list
        if transaction_type == "expense":
            allowed_categories = EXPENSE_CATEGORIES
        else:
            allowed_categories = INCOME_CATEGORIES

        # Validate category
        if category not in allowed_categories:
            flash("Invalid category for this transaction type.")
            return redirect(url_for(
                "edit_expense", expense_id=expense.id
            ))

        # Validate description
        if not description:
            flash("Description is required.")
            return redirect(url_for(
                "edit_expense", expense_id=expense.id
            ))

        # Validate amount
        try:
            amount = float(request.form.get("amount", ""))
        except ValueError:
            flash("Please enter a valid amount.")
            return redirect(url_for(
                "edit_expense", expense_id=expense.id
            ))

        if not 0 < amount < float("inf"):
            flash("Amount must be greater than zero.")
            return redirect(url_for(
                "edit_expense", expense_id=expense.id
            ))

        # Validate date
        try:
            date = datetime.strptime(
                request.form.get("date", ""), "%Y-%m-%d"
            )
        except ValueError:
            flash("Please enter a valid date.")
            return redirect(url_for(
                "edit_expense", expense_id=expense.id
            ))

        # Update only after all validations pass
        expense.description = description
        expense.amount = amount
        expense.category = category
        expense.transaction_type = transaction_type
        expense.date = date

        db.session.commit()

        flash("Transaction updated successfully!")

        return redirect(url_for("dashboard"))

    return render_template("edit_expense.html", expense=expense)


@app.route("/delete-expense/<int:expense_id>", methods=["POST"])
@login_required
def delete_expense(expense_id):

    expense = Expense.query.filter_by(
        id=expense_id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(expense)
    db.session.commit()

    flash("Transaction deleted successfully!")

    return redirect(url_for("dashboard"))


@app.route("/logout", methods=["POST"])
@login_required
def logout():

    logout_user()

    flash("You have logged out successfully!")

    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
