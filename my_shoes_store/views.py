from flask import Blueprint, render_template, url_for, request, session, flash, redirect, abort
from .models import Product, Brand, Category, Order, OrderDetail
from datetime import datetime
from .forms import CheckoutForm, ContactForm
import math
import traceback
from . import db

customer_bp = Blueprint('main', __name__)

# Home page
@customer_bp.route('/')
def index():
    best_sellers = __get_best_sellers()
    new_arrivals = __get_new_arrivals()
    average_rating_map_of_best_sellers = __get_average_rating(best_sellers)
    form = ContactForm() 

    return __render_template('index.html', best_sellers=best_sellers, average_rating_map=average_rating_map_of_best_sellers, new_arrivals=new_arrivals, form=form)

@customer_bp.route('/products/<int:product_id>')
def product_detail(product_id):
    product = __get_product(product_id)
    if not product:
        abort(404)

    average_rating = __get_average_rating([product])[product.id]

    return __render_template('product_detail.html', product=product, average_rating=average_rating)

# add to cart
@customer_bp.route('/cart', methods=['POST'])
def add_to_cart():
    product = __get_product(request.form.get('product_id'))
    if not product:
        abort(404)

    if 'order_id' in session.keys():
        order = __get_order(session['order_id'])
    else:
        # create new order
        order = Order(status=False, first_name='', last_name='', email='', phone='', total=0.00)
        try:
            db.session.add(order)
            db.session.commit()
            session['order_id'] = order.id
        except:
            print('Failed trying to create a new order!')
            abort(500)
    
    existing_order_detail = __get_order_detail(order.id, product.id)
    if existing_order_detail:
        flash('Item already in shopping cart', category='info')
        return redirect(url_for('main.index'))

    # Calculate total price
    try:
        order_detail = OrderDetail(order_id=order.id, product_id=product.id, quantity=1, price=product.price)
        db.session.add(order_detail)
        order.total += product.price
        db.session.commit()
    except:
        flash('There was an issue adding the item to your shopping cart', category='danger')
        return redirect(url_for('main.index'))

    # If the product is in the favorites, remove it
    __remove_from_favorites(product.id)
        
    return __render_template('cart.html', order=order)

@customer_bp.route('/cart')
def view_cart():
    if 'order_id' in session.keys():
        order = __get_order(session['order_id'])
    else:
        order = None

    return __render_template('cart.html', order=order)

@customer_bp.route('/order/product/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if 'order_id' in session.keys():
        order = __get_order(session['order_id'])
        if not order:
            flash("There's no order to delete!")
            return redirect(url_for('main.view_cart'))

        order_detail = __get_order_detail(order.id, product_id)
        if not order_detail:
            flash("Product not found in order!")
            return redirect(url_for('main.view_cart'))

        try:
            order.total -= (order_detail.price * order_detail.quantity)
            db.session.delete(order_detail)
            db.session.commit()
        except:
            flash("Delete from shopping cart failed!")
            return redirect(url_for('main.view_cart'))

    return redirect(url_for('main.view_cart'))

@customer_bp.route('/order/products/<int:product_id>', methods=['POST'])
def update_quantity(product_id):
    if 'order_id' in session.keys():
        order = __get_order(session['order_id'])
        if not order:
            flash("There's no order to update!")
            return redirect(url_for('main.view_cart'))

        order_detail = __get_order_detail(order.id, product_id)
        if not order_detail:
            flash("Product not found in order!")
            return redirect(url_for('main.view_cart'))

        quantity = int(request.form.get('quantity'))
        if quantity < 1:
            remove_from_cart(product_id)
        else:
            try:
                original_quantity = order_detail.quantity
                order_detail.quantity = quantity
                order_detail.price = order_detail.product.price
                order.total += (order_detail.price * (quantity - original_quantity))
                db.session.commit()
            except:
                flash("Update quantity failed!")

    return redirect(url_for('main.view_cart'))

@customer_bp.route('/products', methods=['GET'])
def products():
    search_keyword = request.args.get('search_keyword')
    if search_keyword:
        products = db.session.scalars(db.select(Product).where(Product.name.ilike(f'%{search_keyword}%'))).all()
    else:
        products = db.session.scalars(db.select(Product)).all()

    category_name = request.args.get('category')
    category = None
    if category_name:
        category = __get_category(category_name)
        if category:
            products = [product for product in products if product.category_id == category.id]

    brand_name = request.args.get('brand')
    brand = None
    if brand_name:
        brand = __get_brand(brand_name)
        if brand:
            products = [product for product in products if product.brand_id == brand.id]

    average_rating_map = __get_average_rating(products)

    return __render_template('product_list.html', category=category, brand=brand, search_keyword=search_keyword, products=products, average_rating_map=average_rating_map)

# Complete the order
@customer_bp.route('/checkout', methods=['GET'])
def review_checkout_detail():
    form = CheckoutForm() 
    if 'order_id' in session:
        order = __get_order(session['order_id'])
        if not order.products:
            flash('You need to add some products to your shopping cart first!')
            return(redirect(request.referrer))

    return __render_template('checkout.html', form=form)

@customer_bp.route('/checkout', methods=['POST'])
def checkout():
    form = CheckoutForm() 
    if 'order_id' in session:
        order = __get_order(session['order_id'])
        if not order.products:
            flash('You need to add some products to your shopping cart first!')
            return(redirect(request.referrer))

        if form.validate_on_submit():
            order.status = True
            order.first_name = form.first_name.data
            order.last_name = form.last_name.data
            order.email = form.email.data
            order.phone = form.phone.data

            total = 0
            order_details = db.session.scalars(db.select(OrderDetail).where(OrderDetail.order_id==order.id)).all()
            for detail in order_details:
                # using the price from the product table to avoid price manipulation
                total += (detail.product.price * detail.quantity)
            order.total = total
            order.submitted_timestamp = datetime.now()

            try:
                db.session.commit()
                session.pop('order_id')
                flash('Thank you! One of our team members will contact you soon.')
                return redirect(url_for('main.index'))
            except:
                flash('There was an issue completing your order')
                return (redirect(request.referrer))

    return redirect(url_for('main.review_checkout_detail'))

@customer_bp.route("/search", methods=['POST'])
def search():
    search_keyword = request.form.get('search_keyword')

    return redirect(url_for('main.products', search_keyword=search_keyword))

@customer_bp.route('/favorites', methods=['GET'])
def view_favorites():
    product_ids = session.get('favorites', [])
    products = db.session.scalars(db.select(Product).where(Product.id.in_(product_ids))).all()

    return __render_template('favorites.html', products=products)

@customer_bp.route('/favorites', methods=['POST'])
def add_to_favorites():
    if 'favorites' not in session:
        session['favorites'] = []

    product_id = int(request.form.get('product_id'))
    if product_id not in session['favorites']:
        session['favorites'].append(product_id)
        flash('Product added to favorites', category='success')
    else:
        flash('Product already in favorites', category='info')

    return redirect(url_for('main.view_favorites'))

@customer_bp.route('/favorites/<int:product_id>', methods=['POST'])
def remove_from_favorites(product_id):
    __remove_from_favorites(product_id)
    flash('Product removed from favorites', category='success')

    return redirect(url_for('main.view_favorites'))


@customer_bp.route('/contact', methods=['POST'])
def contact():
    form = ContactForm() 

    if form.validate_on_submit():
        flash(f'Thank you {form.first_name.data}! One of our team members will contact you soon.')
    else:
        flash('There was an issue submitting your question')
    
    return redirect(url_for('main.index'))

def __render_template(template, **kwargs):
    # append categories and brands for top navigation bar
    return render_template(template, **kwargs, categories=__get_categories(), brands=__get_brands())

def __get_categories():
    return db.session.scalars(db.select(Category)).all()

def __get_brands():
    return db.session.scalars(db.select(Brand)).all()

def __get_best_sellers():
    # get the 3 best sellers based on the number of purchased in order details
    best_seller_sql = (
            db.select(Product)
            .join(OrderDetail, Product.id == OrderDetail.product_id)
            .group_by(Product.id)
            .order_by(db.func.count(OrderDetail.product_id).desc()).limit(3)
            )
    best_sellers = db.session.scalars(best_seller_sql).all()

    # If there are less than 3 best sellers, add more products
    if len(best_sellers) < 3:
        more_products_sql = (
            db.select(Product)
            .where(Product.id.notin_([product.id for product in best_sellers]))
            .order_by(Product.id.desc()).limit(3 - len(best_sellers))
                )
        best_sellers += db.session.scalars(more_products_sql).all()

    return best_sellers

def __get_new_arrivals():
    # get the 3 newest products
    return db.session.scalars(db.select(Product).order_by(Product.id.desc()).limit(3)).all()

def __get_average_rating(products):
    average_rating_map = {}
    for product in products:
        reviews = product.reviews
        average_rating = 0
        if reviews:
            ratings = [review.rating for review in reviews]
            average_rating = math.ceil(sum(ratings) / len(ratings))
        average_rating_map[product.id] = average_rating
    
    return average_rating_map

def __get_product(id):
    return db.session.scalar(db.select(Product).where(Product.id==id))

def __get_order(id, status=False):
    return db.session.scalar(db.select(Order).where(Order.id==id, Order.status==status))

def __get_order_detail(order_id, product_id):
    return db.session.scalar(db.select(OrderDetail).where(OrderDetail.order_id==order_id, OrderDetail.product_id==product_id))

def __get_category(name):
    return db.session.scalar(db.select(Category).where(Category.name==name))

def __get_brand(name):
    return db.session.scalar(db.select(Brand).where(Brand.name==name))

def __remove_from_favorites(product_id):
    if 'favorites' in session:
        if product_id in session['favorites']:
            session['favorites'].remove(product_id)
