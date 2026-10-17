from flask import Flask, jsonify, request
from sqlalchemy import create_engine, String, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

app = Flask(__name__)

# ---------- Database (SQLAlchemy + SQLite) ----------
engine = create_engine("sqlite:///shopqa.db")
Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    price: Mapped[float] = mapped_column(Float)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "price": self.price}


Base.metadata.create_all(engine)

# ---------- Simple auth ----------
VALID_USER = {"username": "admin", "password": "admin123"}
TOKEN = "secret-token-123"


def is_authorized():
    return request.headers.get("Authorization") == f"Bearer {TOKEN}"


@app.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    if (data.get("username") == VALID_USER["username"]
            and data.get("password") == VALID_USER["password"]):
        return jsonify({"token": TOKEN}), 200
    return jsonify({"error": "Invalid credentials"}), 401


# ---------- Product endpoints ----------
@app.get("/products")
def list_products():
    with Session() as s:
        return jsonify([p.to_dict() for p in s.query(Product).all()]), 200


@app.get("/products/<int:pid>")
def get_product(pid):
    with Session() as s:
        p = s.get(Product, pid)
        if not p:
            return jsonify({"error": "Product not found"}), 404
        return jsonify(p.to_dict()), 200


@app.post("/products")
def create_product():
    if not is_authorized():
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    name, price = data.get("name"), data.get("price")
    if not name or not isinstance(price, (int, float)) or price < 0:
        return jsonify({"error": "name and a valid price are required"}), 400
    with Session() as s:
        p = Product(name=name, price=price)
        s.add(p)
        s.commit()
        return jsonify(p.to_dict()), 201


@app.put("/products/<int:pid>")
def update_product(pid):
    if not is_authorized():
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    with Session() as s:
        p = s.get(Product, pid)
        if not p:
            return jsonify({"error": "Product not found"}), 404
        p.name = data.get("name", p.name)
        p.price = data.get("price", p.price)
        s.commit()
        return jsonify(p.to_dict()), 200


@app.delete("/products/<int:pid>")
def delete_product(pid):
    if not is_authorized():
        return jsonify({"error": "Unauthorized"}), 401
    with Session() as s:
        p = s.get(Product, pid)
        if not p:
            return jsonify({"error": "Product not found"}), 404
        s.delete(p)
        s.commit()
        return jsonify({"message": "Deleted"}), 200


# Deliberate 500 so you can test server-error handling
@app.get("/crash")
def crash():
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=True)