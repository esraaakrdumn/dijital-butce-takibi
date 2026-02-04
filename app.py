from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Transaction, Category
from sqlalchemy import func
from datetime import datetime
from collections import defaultdict


app = Flask(__name__)

app.config["SECRET_KEY"] = "supersecretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"

db.init_app(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():
    return render_template("home.html")


# ================= DASHBOARD =================
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():

    categories = Category.query.filter_by(user_id=current_user.id).all()

    if request.method == "POST":
        amount = float(request.form.get("amount"))
        category_id = int(request.form.get("category"))
        type_ = request.form.get("type")

        new_transaction = Transaction(
            amount=amount,
            type=type_,
            user_id=current_user.id,
            category_id=category_id
        )

        db.session.add(new_transaction)
        db.session.commit()

        flash("İşlem eklendi!", "success")
        return redirect(url_for("dashboard"))

    # 🔥 İşlemleri tarih sıralı çek
    transactions = Transaction.query.filter_by(
        user_id=current_user.id
    ).order_by(Transaction.date).all()

    # ================= TOPLAM =================
    income_total = sum(t.amount for t in transactions if t.type == "income")
    expense_total = sum(t.amount for t in transactions if t.type == "expense")
    balance = income_total - expense_total

    # ================= GÜNLÜK GRAFİK =================
    daily_income = defaultdict(float)
    daily_expense = defaultdict(float)

    for t in transactions:
        day = t.date.strftime("%d-%m")

        if t.type == "income":
            daily_income[day] += t.amount
        else:
            daily_expense[day] += t.amount

    chart_labels = sorted(set(list(daily_income.keys()) + list(daily_expense.keys())))

    income_chart_data = [daily_income[day] for day in chart_labels]
    expense_chart_data = [daily_expense[day] for day in chart_labels]

    # ================= KATEGORİ ANALİZİ =================
    category_totals = {}

    for t in transactions:
        if t.type == "expense":
            cat_name = t.category.name
            category_totals[cat_name] = category_totals.get(cat_name, 0) + t.amount

    category_labels = list(category_totals.keys())
    category_data = list(category_totals.values())

    return render_template(
        "dashboard.html",
        transactions=transactions,
        categories=categories,
        income_total=income_total,
        expense_total=expense_total,
        balance=balance,
        chart_labels=chart_labels,
        income_chart_data=income_chart_data,
        expense_chart_data=expense_chart_data,
        category_labels=category_labels,
        category_data=category_data
    )


# ================= KATEGORİ EKLE =================
@app.route("/add_category", methods=["POST"])
@login_required
def add_category():

    name = request.form.get("category_name")

    if not name or not name.strip():
        flash("Kategori adı boş olamaz.", "danger")
        return redirect(url_for("dashboard"))

    name = name.strip()

    existing = Category.query.filter(
        func.lower(Category.name) == name.lower(),
        Category.user_id == current_user.id
    ).first()

    if existing:
        flash("Bu kategori zaten mevcut.", "warning")
        return redirect(url_for("dashboard"))

    new_category = Category(
        name=name,
        user_id=current_user.id
    )

    db.session.add(new_category)
    db.session.commit()

    flash("Kategori eklendi.", "success")
    return redirect(url_for("dashboard"))


# ================= DELETE =================
@app.route("/delete/<int:transaction_id>")
@login_required
def delete_transaction(transaction_id):

    transaction = Transaction.query.get_or_404(transaction_id)

    if transaction.user_id != current_user.id:
        flash("Bu işlemi silemezsiniz.", "danger")
        return redirect(url_for("dashboard"))

    db.session.delete(transaction)
    db.session.commit()

    flash("İşlem silindi.", "info")
    return redirect(url_for("dashboard"))


# ================= LOGOUT =================
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Çıkış yaptınız.", "info")
    return redirect(url_for("login"))


# ================= EDIT =================
@app.route("/edit/<int:transaction_id>", methods=["GET", "POST"])
@login_required
def edit_transaction(transaction_id):

    transaction = Transaction.query.get_or_404(transaction_id)
    categories = Category.query.filter_by(user_id=current_user.id).all()

    if transaction.user_id != current_user.id:
        flash("Bu işlemi düzenleyemezsiniz.", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        transaction.amount = float(request.form.get("amount"))
        transaction.category_id = int(request.form.get("category"))
        transaction.type = request.form.get("type")

        db.session.commit()
        flash("İşlem güncellendi.", "success")
        return redirect(url_for("dashboard"))

    return render_template("edit.html", transaction=transaction, categories=categories)


# ================= REGISTER =================
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Bu email zaten kayıtlı.", "danger")
            return redirect(url_for("register"))

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        new_user = User(
            username=username,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        default_categories = [
            "Yemek",
            "Ulaşım",
            "Alışveriş",
            "Faturalar",
            "Eğlence"
        ]

        for cat in default_categories:
            db.session.add(Category(name=cat, user_id=new_user.id))

        db.session.commit()

        flash("Kayıt başarılı! Giriş yapabilirsiniz.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash("Giriş başarılı!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Giriş başarısız. Bilgileri kontrol edin.", "danger")

    return render_template("login.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

