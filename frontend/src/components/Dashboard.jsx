import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { AuthContext } from "../context/AuthContext.jsx";
import "./Dashboard.css"; // Import the CSS file
import { ToastContainer, toast } from "react-toastify";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

const Dashboard = () => {
  const [products, setProducts] = useState([]);
  const [form, setForm] = useState({
    url: "",
    target_price: "",
    phone_number: "",
  });
  const [editProductId, setEditProductId] = useState(null);
  const [user, setUser] = useState(null);
  const { token, logout } = useContext(AuthContext);
  const [isProductsLoading, setIsProductsLoading] = useState(true);

  const notify = (msg, type) => toast[type](msg);

  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    if (storedUser) setUser(JSON.parse(storedUser));
  }, []);

  const fetchProducts = async () => {
    try {
      const res = await axios.get("http://localhost:5000/api/products/all", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setProducts(res.data);
    } catch (err) {
      console.error("Failed to fetch products", err);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setIsProductsLoading(false);
      if (editProductId) {
        await axios.put(
          `http://localhost:5000/api/products/${editProductId}`,
          form,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );
        setEditProductId(null);
        notify("Product details updated successfully!", "success");
      } else {
        await axios.post("http://localhost:5000/api/products/add", form, {
          headers: { Authorization: `Bearer ${token}` },
        });
        notify("Product added successfully!", "success");
      }
      setIsProductsLoading(true);
      setForm({ url: "", target_price: "", phone_number: "" });
      fetchProducts();
    } catch (err) {
      console.error("Failed to submit product", err);
    }
  };

  const editProduct = (id) => {
    const product = products.find((p) => p._id === id);
    if (product) {
      setForm({
        url: product.url,
        target_price: product.target_price,
        phone_number: product.phone_number,
      });
      setEditProductId(id);
    }
  };

  const deleteProduct = async (id) => {
    try {
      await axios.delete(`http://localhost:5000/api/products/${id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      notify("Product deleted successfully!", "success");
      fetchProducts();
    } catch (err) {
      console.error("Failed to delete product", err);
    }
  };

  const clearForm = () => {
    setForm({ url: "", target_price: "", phone_number: "" });
    setEditProductId(null);
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Welcome, {user?.name || "User"} 👋</h2>
        <button className="logout-btn" onClick={logout}>
          Logout
        </button>
      </div>

      <div className="form-card">
        <h3>{editProductId ? "Edit Product" : "Add Product to Track"}</h3>
        <form onSubmit={handleSubmit} className="product-form">
          <input
            placeholder="Product URL"
            value={form.url}
            onChange={(e) => setForm({ ...form, url: e.target.value })}
            required
          />
          <input
            placeholder="Target Price"
            value={form.target_price}
            onChange={(e) => setForm({ ...form, target_price: e.target.value })}
            required
          />
          <input
            placeholder="Phone Number"
            value={form.phone_number}
            onChange={(e) => setForm({ ...form, phone_number: e.target.value })}
            required
          />
          <div className="form-btn">
            <button className="add-btn" type="submit">
              {editProductId
                ? isProductsLoading
                  ? "Update"
                  : "Updating"
                : isProductsLoading
                ? "Add"
                : "Adding"}
            </button>
            <button className="clear-btn" onClick={clearForm}>
              Clear
            </button>
          </div>
        </form>
      </div>

      <div className="products-list">
        <h3>Tracked Products</h3>
        {products.length === 0 ? (
          <p>No products being tracked.</p>
        ) : (
          <ul>
            {products.map((p) => (
              <li key={p._id} className="product-item">
                <div>
                  <a href={p.url} target="_blank" rel="noreferrer">
                    {p.title}
                  </a>
                  <p>Current Price: ₹{p.current_price}</p>
                  <p>Target Price: ₹{p.target_price}</p>
                </div>
                <div className="actions">
                  <button
                    className="edit-btn"
                    onClick={() => editProduct(p._id)}
                  >
                    <i className="fa-solid fa-pen-to-square"></i>
                  </button>
                  <button
                    className="delete-btn"
                    onClick={() => deleteProduct(p._id)}
                  >
                    <i className="fa-solid fa-trash"></i>
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
      <ToastContainer position="top-center" theme="light" autoClose={1000} />
    </div>
  );
};

export default Dashboard;
