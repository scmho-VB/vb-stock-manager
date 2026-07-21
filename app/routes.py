from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import db, Product, StockMovement

main = Blueprint("main", __name__)

# ---------- DASHBOARD ----------
@main.route("/")
def home():
    total_products = Product.query.count()
    low_stock = Product.query.filter(Product.quantity <= Product.reorder_level).all()
    total_quantity = db.session.query(db.func.sum(Product.quantity)).scalar() or 0
    return render_template("dashboard.html",
                            total_products=total_products,
                            low_stock=low_stock,
                            total_quantity=total_quantity)

# ---------- PRODUCTS ----------
@main.route("/products")
def products():
    all_products = Product.query.order_by(Product.name).all()
    return render_template("products.html", products=all_products)

@main.route("/products/add", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        p = Product(
            name=request.form["name"],
            sku=request.form["sku"],
            category=request.form.get("category"),
            unit=request.form.get("unit") or "pcs",
            quantity=int(request.form.get("quantity") or 0),
            reorder_level=int(request.form.get("reorder_level") or 10)
        )
        db.session.add(p)
        db.session.commit()
        flash("Product added successfully!")
        return redirect(url_for("main.products"))
    return render_template("add_product.html")

@main.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
def edit_product(product_id):
    p = Product.query.get_or_404(product_id)
    if request.method == "POST":
        p.name = request.form["name"]
        p.sku = request.form["sku"]
        p.category = request.form.get("category")
        p.unit = request.form.get("unit") or "pcs"
        p.reorder_level = int(request.form.get("reorder_level") or 10)
        db.session.commit()
        flash("Product updated!")
        return redirect(url_for("main.products"))
    return render_template("edit_product.html", product=p)

@main.route("/products/<int:product_id>/delete", methods=["POST"])
def delete_product(product_id):
    p = Product.query.get_or_404(product_id)
    db.session.delete(p)
    db.session.commit()
    flash("Product deleted!")
    return redirect(url_for("main.products"))

# ---------- STOCK IN ----------
@main.route("/stock/in", methods=["GET", "POST"])
def stock_in():
    products_list = Product.query.order_by(Product.name).all()
    if request.method == "POST":
        product_id = int(request.form["product_id"])
        qty = int(request.form["quantity"])
        p = Product.query.get_or_404(product_id)
        p.quantity += qty
        movement = StockMovement(product_id=product_id, movement_type="IN",
                                  quantity=qty,
                                  reference=request.form.get("reference"),
                                  note=request.form.get("note"))
        db.session.add(movement)
        db.session.commit()
        flash(f"Stock IN recorded for {p.name}!")
        return redirect(url_for("main.stock_in"))
    return render_template("stock_in.html", products=products_list)

# ---------- STOCK OUT ----------
@main.route("/stock/out", methods=["GET", "POST"])
def stock_out():
    products_list = Product.query.order_by(Product.name).all()
    if request.method == "POST":
        product_id = int(request.form["product_id"])
        qty = int(request.form["quantity"])
        p = Product.query.get_or_404(product_id)
        if qty > p.quantity:
            flash("Error: Not enough stock available!")
            return redirect(url_for("main.stock_out"))
        p.quantity -= qty
        movement = StockMovement(product_id=product_id, movement_type="OUT",
                                  quantity=qty,
                                  reference=request.form.get("reference"),
                                  note=request.form.get("note"))
        db.session.add(movement)
        db.session.commit()
        flash(f"Stock OUT recorded for {p.name}!")
        return redirect(url_for("main.stock_out"))
    return render_template("stock_out.html", products=products_list)

# ---------- MOVEMENT HISTORY ----------
@main.route("/movements")
def movements():
    all_movements = StockMovement.query.order_by(StockMovement.created_at.desc()).limit(200).all()
    return render_template("movements.html", movements=all_movements)
