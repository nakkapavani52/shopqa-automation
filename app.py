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
# ---------- Simple web pages (for Selenium UI testing) ----------
LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head><title>ShopQA Login</title></head>
<body>
  <h1>ShopQA Login</h1>
  <input id="username" placeholder="Username"><br>
  <input id="password" type="password" placeholder="Password"><br>
  <button id="login-btn" onclick="login()">Login</button>
  <p id="message"></p>
  <script>
    async function login() {
      const res = await fetch("/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          username: document.getElementById("username").value,
          password: document.getElementById("password").value
        })
      });
      const data = await res.json();
      if (res.status === 200) {
        sessionStorage.setItem("token", data.token);
        window.location.href = "/ui/products";
      } else {
        document.getElementById("message").innerText = "Login failed: " + data.error;
      }
    }
  </script>
</body>
</html>
"""

PRODUCTS_PAGE = """
<!DOCTYPE html>
<html>
<head><title>ShopQA Products</title></head>
<body>
  <h1>Products</h1>
  <input id="product-name" placeholder="Product name">
  <input id="product-price" placeholder="Price">
  <button id="add-btn" onclick="addProduct()">Add Product</button>
  <p id="message"></p>
  <table id="product-table" border="1">
    <thead><tr><th>ID</th><th>Name</th><th>Price</th></tr></thead>
    <tbody id="product-body"></tbody>
  </table>
  <script>
    async function loadProducts() {
      const res = await fetch("/products");
      const items = await res.json();
      const body = document.getElementById("product-body");
      body.innerHTML = "";
      items.forEach(function (p) {
        body.innerHTML += "<tr><td>" + p.id + "</td><td>" + p.name + "</td><td>" + p.price + "</td></tr>";
      });
    }
    async function addProduct() {
      const token = sessionStorage.getItem("token");
      if (!token) {
        document.getElementById("message").innerText = "Please login first";
        return;
      }
      const res = await fetch("/products", {
        method: "POST",
        headers: {"Content-Type": "application/json", "Authorization": "Bearer " + token},
        body: JSON.stringify({
          name: document.getElementById("product-name").value,
          price: parseFloat(document.getElementById("product-price").value)
        })
      });
      const data = await res.json();
      if (res.status === 201) {
        document.getElementById("message").innerText = "Product added";
        loadProducts();
      } else {
        document.getElementById("message").innerText = "Error: " + data.error;
      }
    }
    loadProducts();
  </script>
</body>
</html>
"""


@app.get("/ui/login")
def ui_login():
    return LOGIN_PAGE


@app.get("/ui/products")
def ui_products():
    return PRODUCTS_PAGE


if __name__ == "__main__":
    app.run(debug=True)