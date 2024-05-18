from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

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
    image_url = db.Column(db.String(200))  # Add image URL field
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    owner = db.relationship("User", backref=db.backref("products", lazy=True))


@app.route("/")
def index():
    products = Product.query.all()
    return render_template("index.html", products=products)


# Add routes for user authentication, product CRUD operations, etc.

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        # Add sample data
        if User.query.count() == 0:  # Ensure sample data is added only once
            user = User(username="testuser", password="password")
            db.session.add(user)
            db.session.commit()

            # Adding more products with sample photo URLs
            products = [
                Product(
                    name="Product 1",
                    description="Description for product 1",
                    price=10.99,
                    image_url="https://via.placeholder.com/300",
                    owner=user,
                ),
                Product(
                    name="Product 2",
                    description="Description for product 2",
                    price=20.99,
                    image_url="https://via.placeholder.com/150",
                    owner=user,
                ),
                Product(
                    name="Product 3",
                    description="Description for product 3",
                    price=30.99,
                    image_url="https://via.placeholder.com/150",
                    owner=user,
                ),
                Product(
                    name="Product 4",
                    description="Description for product 4",
                    price=40.99,
                    image_url="https://via.placeholder.com/150",
                    owner=user,
                ),
                Product(
                    name="Product 5",
                    description="Description for product 5",
                    price=50.99,
                    image_url="https://via.placeholder.com/150",
                    owner=user,
                ),
                Product(
                    name="Product 6",
                    description="Description for product 6",
                    price=60.99,
                    image_url="https://via.placeholder.com/150",
                    owner=user,
                ),
                Product(
                    name="Product 7",
                    description="Description for product 7",
                    price=70.99,
                    image_url="https://via.placeholder.com/150",
                    owner=user,
                ),
                Product(
                    name="Product 8",
                    description="Description for product 8",
                    price=80.99,
                    image_url="https://via.placeholder.com/150",
                    owner=user,
                ),
                Product(
                    name="Product 9",
                    description="Description for product 9",
                    price=90.99,
                    image_url="https://via.placeholder.com/150",
                    owner=user,
                ),
                Product(
                    name="Product 10",
                    description="Description for product 10",
                    price=100.99,
                    image_url="https://via.placeholder.com/150",
                    owner=user,
                ),
            ]
            db.session.add_all(products)
            db.session.commit()

    app.run(debug=True)