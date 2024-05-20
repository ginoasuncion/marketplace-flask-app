from flask import Flask, render_template, request, session, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///marketplace.db"
db = SQLAlchemy(app)
app.secret_key = '123'

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


user_list = {'a':'1'}


def login_check(username, password):
    try:
        if user_list[username] == password:
            return True
    except KeyError:
        return False

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if login_check(username, password):
            session['user_login'] = username
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_login', None)
    return redirect(url_for('index'))




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
                    date_posted=datetime.utcnow(),
                ),
                Product(
                    name="Product 2",
                    description="Description for product 2",
                    price=20.99,
                    image_url="https://via.placeholder.com/300",
                    contact_details="contact2@example.com",
                    tags="tag2,tag3",
                    owner=user,
                    date_posted=datetime.utcnow(),
                ),
                Product(
                    name="Product 3",
                    description="Description for product 3",
                    price=30.99,
                    image_url="https://via.placeholder.com/300",
                    contact_details="contact3@example.com",
                    tags="tag1,tag3",
                    owner=user,
                    date_posted=datetime.utcnow(),
                ),
                Product(
                    name="Product 4",
                    description="Description for product 4",
                    price=40.99,
                    image_url="https://via.placeholder.com/300",
                    contact_details="contact4@example.com",
                    tags="tag1,tag4",
                    owner=user,
                    date_posted=datetime.utcnow(),
                ),
                Product(
                    name="Product 5",
                    description="Description for product 5",
                    price=50.99,
                    image_url="https://via.placeholder.com/300",
                    contact_details="contact5@example.com",
                    tags="tag2,tag4",
                    owner=user,
                    date_posted=datetime.utcnow(),
                ),
                Product(
                    name="Product 6",
                    description="Description for product 6",
                    price=60.99,
                    image_url="https://via.placeholder.com/300",
                    contact_details="contact6@example.com",
                    tags="tag3,tag4",
                    owner=user,
                    date_posted=datetime.utcnow(),
                ),
                Product(
                    name="Product 7",
                    description="Description for product 7",
                    price=70.99,
                    image_url="https://via.placeholder.com/300",
                    contact_details="contact7@example.com",
                    tags="tag1,tag2",
                    owner=user,
                    date_posted=datetime.utcnow(),
                ),
                Product(
                    name="Product 8",
                    description="Description for product 8",
                    price=80.99,
                    image_url="https://via.placeholder.com/300",
                    contact_details="contact8@example.com",
                    tags="tag2,tag3",
                    owner=user,
                    date_posted=datetime.utcnow(),
                ),
                Product(
                    name="Product 9",
                    description="Description for product 9",
                    price=90.99,
                    image_url="https://via.placeholder.com/300",
                    contact_details="contact9@example.com",
                    tags="tag1,tag3",
                    owner=user,
                    date_posted=datetime.utcnow(),
                ),
                Product(
                    name="Product 10",
                    description="Description for product 10",
                    price=100.99,
                    image_url="https://via.placeholder.com/300",
                    contact_details="contact10@example.com",
                    tags="tag1,tag4",
                    owner=user,
                    date_posted=datetime.utcnow(),
                ),
            ]
            db.session.add_all(products)
            db.session.commit()

    app.run(debug=True)
