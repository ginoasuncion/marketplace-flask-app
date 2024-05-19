from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///marketplace.db"
db = SQLAlchemy(app)


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
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    owner = db.relationship("User", backref=db.backref("products", lazy=True))


@app.route("/", methods=["GET", "POST"])
@app.route("/page/<int:page>", methods=["GET", "POST"])
def index(page=1):
    per_page = 6  # Products per page
    search_query = request.form.get("search")
    if search_query:
        search_term = f"%{search_query}%"
        products = Product.query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term),
                Product.tags.ilike(search_term),
            )
        ).paginate(page=page, per_page=per_page, error_out=False)
    else:
        products = Product.query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template("index.html", products=products.items, pagination=products)


@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("product_detail.html", product=product)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        if User.query.count() == 0:
            user = User(username="testuser", password="password")
            db.session.add(user)
            db.session.commit()

            products = [
                Product(
                    name="Product 1",
                    description="Description for product 1",
                    price=10.99,
                    image_url="https://via.placeholder.com/300",
                    contact_details="contact1@example.com",
                    tags="tag1,tag2",
                    owner=user,
                ),
                Product(
                    name="Product 2",
                    description="Description for product 2",
                    price=20.99,
                    image_url="https://via.placeholder.com/300",
                    contact_details="contact2@example.com",
                    tags="tag2,tag3",
                    owner=user,
                ),
                Product(
                    name="Product 3",
                    description="Description for product 3",
                    price=30.99,
                    image_url="https://via.placeholder.com/300",
                    contact_details="contact3@example.com",
                    tags="tag1,tag3",
                    owner=user,
                ),
                Product(
                    name="Product 4",
                    description="Description for product 4",
                    price=40.99,
                    image_url="https://via.placeholder.com/300",
                    contact_details="contact4@example.com",
                    tags="tag1,tag4",
                    owner=user,
                ),
                Product(
                    name="Product 5",
                    description="Description for product 5",
                    price=50.99,
                    image_url="https://via.placeholder.com/300",
                    contact_details="contact5@example.com",
                    tags="tag2,tag4",
                    owner=user,
                ),
                Product(
                    name="Product 6",
                    description="Description for product 6",
                    price=60.99,
                    image_url="https://via.placeholder.com/300",
                    contact_details="contact6@example.com",
                    tags="tag3,tag4",
                    owner=user,
                ),
                Product(
                    name="Product 7",
                    description="Description for product 7",
                    price=70.99,
                    image_url="https://via.placeholder.com/300",
                    contact_details="contact7@example.com",
                    tags="tag1,tag2",
                    owner=user,
                ),
                Product(
                    name="Product 8",
                    description="Description for product 8",
                    price=80.99,
                    image_url="https://via.placeholder.com/300",
                    contact_details="contact8@example.com",
                    tags="tag2,tag3",
                    owner=user,
                ),
                Product(
                    name="Product 9",
                    description="Description for product 9",
                    price=90.99,
                    image_url="https://via.placeholder.com/300",
                    contact_details="contact9@example.com",
                    tags="tag1,tag3",
                    owner=user,
                ),
                Product(
                    name="Product 10",
                    description="Description for product 10",
                    price=100.99,
                    image_url="https://via.placeholder.com/300",
                    contact_details="contact10@example.com",
                    tags="tag1,tag4",
                    owner=user,
                ),
            ]
            db.session.add_all(products)
            db.session.commit()

    app.run(debug=True)
