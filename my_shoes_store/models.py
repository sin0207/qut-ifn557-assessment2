from . import db

class ProductReview(db.Model):
    __tablename__ = 'product_reviews'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"ID: {self.id}\nProduct ID: {self.product_id}\nRating: {self.rating}"

class ProductImage(db.Model):
    __tablename__ = 'product_images'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    filename = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f"ID: {self.id}\nProduct ID: {self.product_id}\nFilename: {self.filename}"

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    price = db.Column(db.Float, nullable=False)
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    images = db.relationship('ProductImage', backref='product', cascade="all, delete-orphan")
    reviews = db.relationship('ProductReview', backref='product', cascade="all, delete-orphan")
    description = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f"ID: {self.id}\nName: {self.name}\nPrice: ${self.price}\nBrand: {self.brand}\nCategory: {self.category}\nImages: {self.images}\nReviews: {self.reviews}"

class Brand(db.Model):
    __tablename__ = 'brands'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    products = db.relationship('Product', backref='brand', cascade="all, delete-orphan")

    def __repr__(self):
        return f"ID: {self.id}\nName: {self.name}"

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    products = db.relationship('Product', backref='category', cascade="all, delete-orphan")

    def __repr__(self):
        return f"ID: {self.id}\nName: {self.name}"


class OrderDetail(db.Model):
    __tablename__ = 'order_details'
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), primary_key=True)
    product = db.relationship('Product', backref='order_details')
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Boolean, default=False)
    first_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)
    email = db.Column(db.String(128), nullable=True)
    phone = db.Column(db.String(32), nullable=True)
    submitted_timestamp = db.Column(db.DateTime, nullable=True)
    total = db.Column(db.Float, nullable=True)
    details = db.relationship('OrderDetail', backref='order')
    products = db.relationship('Product', secondary='order_details', backref='orders')

    def __repr__(self):
        return f"ID: {self.id}\nStatus: {self.status}\nFirst Name: {self.first_name}\nLast Name: {self.last_name}\nEmail: {self.email}\nPhone: {self.phone}\nSubmitted Timestamp: {self.submitted_timestamp}\nTotal: ${self.total}"
