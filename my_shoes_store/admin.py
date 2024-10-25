'''
CREATING A NEW DATABASE
-----------------------
Read explanation here: https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/contexts/

In the terminal, navigate to the project folder just above the miltontours package
Type 'python' to enter the Python interpreter. You should see '>>>'
In Python interpreter type the following (hitting enter after each line):
    from miltontours import db, create_app
    db.create_all(app=create_app())
The database should be created. Exit Python interpreter by typing:
    quit()
Use DB Browser for SQLite to check that the structure is as expected before 
continuing.

ENTERING DATA INTO THE EMPTY DATABASE
-------------------------------------
# Option 1: Use DB Browser for SQLite
You can enter data directly into the cities or tours table by selecting it in
Browse Data and clicking the New Record button. The id field will be created
automatically. However be careful as you will get errors if you do not abide by
the expected field type and length. In particular the DateTime field must be of
the format: 2023-05-17 00:00:00.000000

# Option 2: Create a database seed function in an Admin Blueprint
See below. This blueprint needs to be enabled in __init__.py and then can be 
accessed via http://127.0.0.1:5000/admin/dbseed/
Database constraints mean that it can only be used on a fresh empty database
otherwise it will error. This blueprint should be removed (or commented out)
from the __init__.py after use.

Use DB Browser for SQLite to check that the data is as expected before 
continuing.
'''

from flask import Blueprint
from . import db
from .models import Product, Brand, Category, ProductReview, ProductImage
import random

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# function to clear all data from the test
@admin_bp.route('/db-clear')
def clear_data():
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        db.session.execute(table.delete())
    db.session.commit()

    return 'DATA CLEARED'

# function to put some seed data in the database
@admin_bp.route('/dbseed')
def dbseed():
    nike = Brand(name='Nike')
    adidas = Brand(name='Adidas')
    puma = Brand(name='Puma')
          
    try:
        db.session.add(nike)
        db.session.add(adidas)
        db.session.add(puma)
        db.session.commit()
    except Exception as error:
        return f'There was an issue adding the brands in dbseed function: \n{error}'

    men_category = Category(name="Men's")
    women_category = Category(name="Women's")
    kids_category = Category(name="Kids'")
    try:
        db.session.add(men_category)
        db.session.add(women_category)
        db.session.add(kids_category)
        db.session.commit()
    except Exception as error:
        return f'There was an issue adding the categories in dbseed function: \n{error}'

    description = "[Only for demo] Amazing style and comfort， the design with  trendy elements and adding a unique color, The boots are designed to offer slip resistance, durability, and a lightweight feel, making them suitable for high-performance sports. star style you deserve it."

    air_force = Product(name='OFF-WHITE x Nike Air Force 1 Virgil OW', description=description, price=100, brand=nike, category=men_category)
    sb = Product(name='Nike Dunk SB Piet Mondrian', description=description, price=180.5, brand=nike, category=men_category)
    court = Product(name='Nike Court Borough', description=description, price=200.00, brand=nike, category=women_category)
    pig = Product(name='Nike Dunk Year Of The Pig', description=description, price=150.3, brand=nike, category=women_category)
    sb_low = Product(name='Verdy x Nike Dunk SB Low', description=description, price=40.3, brand=nike, category=women_category)
    lebron = Product(name='Nike Lebron 21', description=description, price=70.8, brand=nike, category=kids_category)

    neo = Product(name='adidas neo Vl Court 811', description=description, price=100, brand=adidas, category=women_category)
    neo_red = Product(name='adidas neo VL Court 2.0 Thorned', description=description, price=120, brand=adidas, category=women_category)
    originals_pro = Product(name='adidas originals Pro Model', description=description, price=150, brand=adidas, category=men_category)
    superstar = Product(name='melting sadness x adidas originals SUPERSTAR', description=description, price=200, brand=adidas, category=kids_category)
    
    archive = Product(name='PUMA Speedcat Archive', description=description, price=190.9, brand=puma, category=men_category)
    palermo = Product(name='PUMA Palermo', description=description, price=200.5, brand=puma, category=women_category)
    suede = Product(name='PUMA Suede' , description=description, price=150.3, brand=puma, category=kids_category)
    products = [air_force, sb, court, pig, sb_low, lebron, neo, neo_red, originals_pro, superstar, archive, palermo, suede]

    try:
        for product in products:
            db.session.add(product)

            random_review_count = random.randint(1, 5)
            for i in range(random_review_count):
                review = ProductReview(product=product, rating=random.randint(1, 5))
                db.session.add(review)
        db.session.commit()
    except Exception as error:
        return f'There was an issue adding the products in dbseed function: \n{error}'


    try:
        for product in products:
            random_review_count = random.randint(1, 5)
            for i in range(random_review_count):
                review = ProductReview(product=product, rating=random.randint(1, 5))
                db.session.add(review)
            
        db.session.commit()
    except Exception as error:
        return f'There was an issue adding the reviews in dbseed function: \n{error}'


    images = [
            ProductImage(product=air_force, filename='airforce_1.png'),
            ProductImage(product=air_force, filename='airforce1_2.png'),
            ProductImage(product=air_force, filename='airforce1_3.png'),
            ProductImage(product=air_force, filename='airforce1_4.png'),
            ProductImage(product=archive, filename='archive_1.png'),
            ProductImage(product=court, filename='court_1.png'),
            ProductImage(product=court, filename='court_2.png'),
            ProductImage(product=court, filename='court_3.png'),
            ProductImage(product=pig, filename='dunk_pig_1.png'),
            ProductImage(product=pig, filename='dunk_pig_2.png'),
            ProductImage(product=pig, filename='dunk_pig_3.png'),
            ProductImage(product=pig, filename='dunk_pig_4.png'),
            ProductImage(product=sb, filename='dunk_sb_1.png'),
            ProductImage(product=sb, filename='dunk_sb_2.png'),
            ProductImage(product=sb, filename='dunk_sb_3.png'),
            ProductImage(product=sb, filename='dunk_sb_4.png'),
            ProductImage(product=sb_low, filename='dunk_sb_low_1.png'),
            ProductImage(product=sb_low, filename='dunk_sb_low_2.png'),
            ProductImage(product=lebron, filename='lebron_1.png'),
            ProductImage(product=lebron, filename='lebron_2.png'),
            ProductImage(product=lebron, filename='lebron_3.png'),
            ProductImage(product=lebron, filename='lebron_4.png'),
            ProductImage(product=neo, filename='neo_1.png'),
            ProductImage(product=neo, filename='neo_2.png'),
            ProductImage(product=neo_red, filename='neo_red_1.png'),
            ProductImage(product=neo_red, filename='neo_red_2.png'),
            ProductImage(product=originals_pro, filename='origin_1.png'),
            ProductImage(product=originals_pro, filename='origin_2.png'),
            ProductImage(product=palermo, filename='palemo_1.png'),
            ProductImage(product=suede, filename='suede_1.png'),
            ProductImage(product=superstar, filename='superstar_1.png'),
            ProductImage(product=superstar, filename='superstar_2.png')
    ]

    try:
        for image in images:
            db.session.add(image)
        db.session.commit()
    except Exception as error:
        return f'There was an issue adding the images in dbseed function: \n{error}'

    return 'DATA LOADED'
