import React, { useState, useContext } from "react";
import axios from "axios";
import { AuthContext } from "../../context/AuthContext.jsx";
import { Link, useNavigate } from "react-router-dom";
import "./Register.css"; // Import the shared CSS file
import { ToastContainer, toast } from "react-toastify";

const Login = () => {
  const [form, setForm] = useState({ email: "", password: "" });
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const notify = (msg, type) => toast[type](msg);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post(
        "http://ai-price-tracker-production.up.railway.app/api/auth/login",
        form,
        {
          withCredentials: true,
        }
      );

      const { token, user } = res.data;
      login(token); // Assuming this stores the token
      localStorage.setItem("user", JSON.stringify(user)); // Store user data
      navigate("/"); // Redirect to home page
    } catch (err) {
      console.error("Login failed:", err.response?.data || err.message);
      notify(err.response?.data.error || "Login failed", "error");
      // Provide a more user-friendly error message
      // alert("Login failed. Please check your email and password.");
    }
  };

  return (
    <div className="auth-container">
      <form onSubmit={handleSubmit} className="auth-form">
        <h2 className="form-title">Welcome Back!</h2>

        <div className="form-group">
          <input
            type="email"
            placeholder="Email"
            className="form-input"
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            required
          />
        </div>
        <div className="form-group">
          <input
            type="password"
            placeholder="Password"
            className="form-input"
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            required
          />
        </div>
        <button type="submit" className="submit-button">
          Login
        </button>
        <p className="auth-prompt">
          Don't have an account?{" "}
          <Link to={"/register"} className="auth-link">
            Register
          </Link>
        </p>
      </form>
      <ToastContainer position="top-center" theme="light" autoClose={1000} />
    </div>
  );
};

export default Login;
