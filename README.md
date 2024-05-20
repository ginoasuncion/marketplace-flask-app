# Harbour Space Bangkok Marketplace Flask Application

This is a simple marketplace web application built using Flask and SQLAlchemy. It allows users to browse, search, filter, and sort products. Each product has details such as name, description, price, tags, and the date it was posted. Users can view individual product details as well.

## Features

- List products with pagination
- Search products by name, description, or tags
- Filter products by tags
- Sort products by price, name, or date posted
- View individual product details
- Professional and responsive UI using Bootstrap

## Technologies Used

- Flask: Web framework for Python
- SQLAlchemy: SQL toolkit and Object-Relational Mapping (ORM) library for Python
- SQLite: Database engine
- Bootstrap: Frontend framework for responsive design

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/marketplace.git
   cd marketplace

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate

4. Install the required packages:
   ```bash
   pip install -r requirements.txt

4. Run the application:
   ```bash
   flask run

The application will be available at http://127.0.0.1:5000/.

## Database Initialization

To initialize the database and create some sample data, run the following command:

```bash
python app.py
```

This will create the necessary database tables and populate them with a test user and sample products.

## Project Structure

```
marketplace-flask-app/
│
├── templates/
│   ├── index.html              # Main page template
│   ├── product_detail.html     # Product detail page template
│
├── app.py                      # Main application file
├── models.py                   # Database models
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── instance/
│   ├── marketplace.db          # SQLite database file (created after running the app)
```

## Usage

### Home Page
Search: Enter keywords in the search bar to find products.
Filter by Tag: Select a tag from the dropdown to filter products.
Sort By: Choose from various sorting options like price, name, or date posted.

### Product Detail
Click on a product to view its detailed information, including description, price, tags, and contact details.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.
