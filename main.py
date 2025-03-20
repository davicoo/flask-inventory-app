from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Database setup
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///art_inventory.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Define Artwork model
class Artwork(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(50), default="Available")  # Available / Sold
    paid = db.Column(db.Boolean, default=False)

# Create database tables
with app.app_context():
    db.create_all()

# Serve the Web UI
@app.route('/')
def index():
    return render_template('index.html')

# API: Add artwork
@app.route('/add', methods=['POST'])
def add_artwork():
    data = request.json
    new_artwork = Artwork(title=data["title"], location=data["location"], price=data["price"])
    db.session.add(new_artwork)
    db.session.commit()
    return jsonify({"message": "Artwork added!", "id": new_artwork.id})

# API: View all artworks
@app.route('/artworks', methods=['GET'])
def get_artworks():
    artworks = Artwork.query.all()
    return jsonify([{
        "id": art.id,
        "title": art.title,
        "location": art.location,
        "price": art.price,
        "status": art.status,
        "paid": art.paid
    } for art in artworks])

# API: Mark artwork as sold
@app.route('/sell/<int:id>', methods=['PUT'])
def sell_artwork(id):
    artwork = Artwork.query.get(id)
    if artwork:
        artwork.status = "Sold"
        db.session.commit()
        return jsonify({"message": "Artwork marked as sold!"})
    return jsonify({"error": "Artwork not found"}), 404

# API: Mark a sale as paid
@app.route('/pay/<int:id>', methods=['PUT'])
def pay_artwork(id):
    artwork = Artwork.query.get(id)
    if artwork:
        artwork.paid = True
        db.session.commit()
        return jsonify({"message": "Payment marked as complete!"})
    return jsonify({"error": "Artwork not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))