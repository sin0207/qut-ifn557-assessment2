from flask import Flask, render_template
from flask_bootstrap import Bootstrap4
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, static_folder='./static')
    app.debug = True
    app.secret_key = 'd401c954dffcc3ffc175b2cc83073091'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    db.init_app(app)
    Bootstrap4(app)
    
    from . import views
    from . import admin
    app.register_blueprint(views.customer_bp)
    app.register_blueprint(admin.admin_bp)
    
    @app.errorhandler(404) 
    def not_found(e): 
      return render_template("error.html", error=e)

    @app.errorhandler(500)
    def internal_error(e):
      return render_template("error.html", error=e)
   
    return app
