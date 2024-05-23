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
from PIL import Image
import random
import string

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///marketplace.db"
db = SQLAlchemy(app)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["ADMIN_KEY"] = os.getenv("ADMIN_KEY")
app.config["UPLOAD_FOLDER"] = os.path.join(app.instance_path, "product_pictures")
app.config["CUSTOM_STATIC_PATH"] = os.path.join(app.instance_path, "product_pictures")

tag_colors = {
    "Eco": "#5cb85c",
    "Outdoor": "#5bc0de",
    "Tech": "#f0ad4e",
    "Music": "#d9534f",
    "Gadgets": "#428bca",
    "Beauty": "#5cb85c",
    "Skincare": "#5bc0de",
    "Camping": "#f0ad4e",
    "Travel": "#d9534f",
    "Coffee": "#428bca",
    "Gourmet": "#5cb85c",
    "Fitness": "#5bc0de",
    "Health": "#f0ad4e",
    "Fashion": "#d9534f",
    "Luxury": "#428bca",
    "Art": "#5cb85c",
    "Crafts": "#5bc0de",
    "Stationery": "#f0ad4e",
    "Books": "#d9534f",
    "Photography": "#428bca",
}


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
    per_page = 9  # Products per page
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
        "index.html",
        products=products.items,
        pagination=products,
        all_tags=unique_tags,
        tag_colors=tag_colors,
    )


@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template(
        "product_detail.html", product=product, tag_colors=tag_colors
    )


@app.route("/product_management", methods=["GET", "POST"])
def product_management():
    if "user_login" not in session:
        flash("Please log in to manage your products")
        return redirect(url_for("login"))

    user = User.query.filter_by(username=session["user_login"]).first()
    if user is None:
        flash("Invalid user. Please log in again.")
        return redirect(url_for("login"))
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

    tags = Tag.query.all()  # Load tags for the form selection
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        price = request.form.get("price")
        contact_details = request.form.get("contact_details")
        file = request.files["image"]
        selected_tag_ids = request.form.getlist("tags[]")
        tags_string = ",".join(selected_tag_ids)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            with Image.open(filepath) as img:
                img = img.resize((300, 300), Image.LANCZOS)
                img.save(filepath)  # Save the resized image

            image_url = filename
        else:
            flash("Invalid file type")
            return redirect(request.url)

        # Fetch the user object based on the username in session
        user = User.query.filter_by(username=session["user_login"]).first()
        if not user:
            flash("User not found. Please log in again.")
            return redirect(url_for("login"))

        try:
            new_product = Product(
                name=name,
                description=description,
                price=float(price),
                image_url=image_url,
                contact_details=contact_details,
                tags=tags_string,
                owner_id=user.id,  # Use the user's ID for the owner_id
            )
            db.session.add(new_product)
            db.session.commit()
            flash("Product added successfully!")
        except Exception as e:
            db.session.rollback()
            flash(f"Failed to add product: {str(e)}")
            return redirect(request.url)

        return redirect(url_for("product_management"))

    return render_template("add_product.html", tags=tags)


@app.route("/product/edit/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    all_tags = Tag.query.all()
    product_tag_ids = [
        int(tag_id) for tag_id in product.tags.split(",") if product.tags
    ]

    if request.method == "POST":
        product.name = request.form.get("name")
        product.description = request.form.get("description")
        product.price = request.form.get("price")
        product.contact_details = request.form.get("contact_details")
        selected_tag_ids = request.form.getlist("tags[]")
        product.tags = ",".join(selected_tag_ids)

        image_url = request.form.get("image_url")
        if image_url:
            product.image_url = image_url

        try:
            db.session.commit()
            flash("Product updated successfully!")
            return redirect(url_for("product_management"))
        except Exception as e:
            db.session.rollback()
            flash("Failed to update product: " + str(e))

    return render_template(
        "edit_product.html",
        product=product,
        all_tags=all_tags,
        product_tag_ids=product_tag_ids,
    )


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


def generate_random_string(length=8):
    """Generate a random string of fixed length."""
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Create random users
        for _ in range(10):  # Adjust the number of users as needed
            username = generate_random_string(8)
            password = generate_password_hash(
                generate_random_string(12), method="pbkdf2:sha256"
            )
            user = User(username=username, password=password)
            db.session.add(user)
        db.session.commit()

        # Check if the admin user exists; if not, create one
        if User.query.filter_by(username="admin").count() == 0:
            password = generate_password_hash(
                app.config["ADMIN_KEY"], method="pbkdf2:sha256"
            )
            admin_user = User(username="admin", password=password)
            db.session.add(admin_user)
            db.session.commit()

        # Add sample products to the database (randomly assign owners)
        users = User.query.all()
        for product_data in products:
            product = Product(
                name=product_data["name"],
                description=product_data["description"],
                price=product_data["price"],
                image_url=product_data["image_url"],
                contact_details=product_data["contact_details"],
                tags=product_data["tags"],
                date_posted=product_data["date_posted"],
                owner=random.choice(users),  # Assign a random user as owner
            )
            db.session.add(product)
        db.session.commit()

        for tag_name in tags:
            new_tag = Tag(name=tag_name)
            db.session.add(new_tag)
        db.session.commit()

    app.run(debug=True, port=8088)
