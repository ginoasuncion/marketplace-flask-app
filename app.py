import os
from flask import (
    Flask,
    render_template,
    request,
    session,
    url_for,
    redirect,
    flash,
    send_from_directory,
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
from sample_data import products  # Import sample data
from tag_data import tags  # Import sample tags

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///marketplace.db"
db = SQLAlchemy(app)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["ADMIN_KEY"] = os.getenv("ADMIN_KEY")
app.config["UPLOAD_FOLDER"] = os.path.join(app.instance_path, "product_pictures")
app.config["CUSTOM_STATIC_PATH"] = os.path.join(app.instance_path, "product_pictures")


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200))
    contact_details = db.Column(db.String(200), nullable=False)
    tags = db.Column(db.String(200))
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    owner = db.relationship("User", backref=db.backref("products", lazy=True))


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name


@app.route("/cdn/<path:filename>")
def custom_static(filename):
    return send_from_directory(app.config["CUSTOM_STATIC_PATH"], filename)


@app.route("/", methods=["GET", "POST"])
@app.route("/page/<int:page>", methods=["GET", "POST"])
def index(page=1):
    per_page = 6  # Products per page
    search_query = request.form.get("search")
    filter_tag = request.form.get("filter_tag")
    sort_by = request.form.get("sort_by")

    # Base query
    query = Product.query

    # Apply filters
    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term),
                Product.tags.ilike(search_term),
            )
        )
    if filter_tag:
        query = query.filter(Product.tags.ilike(f"%{filter_tag}%"))

    # Apply sorting
    if sort_by == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort_by == "price_desc":
        query = query.order_by(Product.price.desc())
    elif sort_by == "name_asc":
        query = query.order_by(Product.name.asc())
    elif sort_by == "name_desc":
        query = query.order_by(Product.name.desc())
    elif sort_by == "date_asc":
        query = query.order_by(Product.date_posted.asc())
    elif sort_by == "date_desc":
        query = query.order_by(Product.date_posted.desc())

    products = query.paginate(page=page, per_page=per_page, error_out=False)

    # Get all unique tags
    all_tags = db.session.query(Product.tags).distinct().all()
    unique_tags = set(tag for sublist in all_tags for tag in sublist[0].split(","))

    return render_template(
        "index.html", products=products.items, pagination=products, all_tags=unique_tags
    )


@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("product_detail.html", product=product)


@app.route("/product_management", methods=["GET", "POST"])
def product_management():
    if "user_login" not in session:
        flash("Please log in to manage your products")
        return redirect(url_for("login"))

    user = User.query.filter_by(username=session["user_login"]).first()
    products = Product.query.filter_by(owner_id=user.id).all()

    return render_template("product_management.html", products=products)


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/product/add", methods=["GET", "POST"])
def add_product():
    if "user_login" not in session:
        flash("Please log in to add a product")
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        price = request.form.get("price")
        contact_details = request.form.get("contact_details")
        tags = request.form.get("tags")

        # Handle image upload
        if "image" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["image"]
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            image_url = url_for("custom_static", filename=filename)
        else:
            image_url = None

        user = User.query.filter_by(username=session["user_login"]).first()
        new_product = Product(
            name=name,
            description=description,
            price=price,
            image_url=image_url,
            contact_details=contact_details,
            tags=tags,
            owner_id=user.id,
        )

        db.session.add(new_product)
        db.session.commit()
        flash("Product added successfully")
        return redirect(url_for("product_management"))

    return render_template("add_product.html")


@app.route("/product/edit/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    if "user_login" not in session:
        flash("Please log in to edit a product")
        return redirect(url_for("login"))

    product = Product.query.get_or_404(product_id)
    if product.owner.username != session["user_login"]:
        flash("You do not have permission to edit this product")
        return redirect(url_for("product_management"))

    if request.method == "POST":
        product.name = request.form.get("name")
        product.description = request.form.get("description")
        product.price = request.form.get("price")
        product.image_url = request.form.get("image_url")
        product.contact_details = request.form.get("contact_details")
        product.tags = request.form.get("tags")

        db.session.commit()
        flash("Product updated successfully")
        return redirect(url_for("product_management"))

    return render_template("edit_product.html", product=product)


@app.route("/product/delete/<int:product_id>", methods=["POST"])
def delete_product(product_id):
    if "user_login" not in session:
        flash("Please log in to delete a product")
        return redirect(url_for("login"))

    product = Product.query.get_or_404(product_id)
    if product.owner.username != session["user_login"]:
        flash("You do not have permission to delete this product")
        return redirect(url_for("product_management"))

    db.session.delete(product)
    db.session.commit()
    flash("Product deleted successfully")
    return redirect(url_for("product_management"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Username and password are required")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

        new_user = User(username=username, password=hashed_password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash("User registered successfully")
            return redirect(url_for("login"))
        except IntegrityError:
            db.session.rollback()
            flash("Username already exists")
            return redirect(url_for("register"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session["user_login"] = user.username
            flash("Login successful")
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    session.pop("user_login", None)
    flash("You have been logged out")
    return redirect(url_for("index"))


if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()

        if User.query.count() == 0:
            password = generate_password_hash(
                app.config["ADMIN_KEY"], method="pbkdf2:sha256"
            )
            user = User(username="admin", password=password)
            db.session.add(user)
            db.session.commit()

            # Add sample products to the database
            for product_data in products:
                product = Product(
                    name=product_data["name"],
                    description=product_data["description"],
                    price=product_data["price"],
                    image_url=product_data["image_url"],
                    contact_details=product_data["contact_details"],
                    tags=product_data["tags"],
                    date_posted=product_data["date_posted"],
                    owner=user,
                )
                db.session.add(product)
            db.session.commit()

            for tag_name in tags:
                new_tag = Tag(name=tag_name)
                db.session.add(new_tag)
            db.session.commit()

    app.run(debug=True, port=8088)
