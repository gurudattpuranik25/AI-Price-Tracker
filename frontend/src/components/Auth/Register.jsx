import React, { useState } from "react";
import axios from "axios";
import { Link, useNavigate } from "react-router-dom";
import "./Register.css"; // Ensure this path is correct
import { ToastContainer, toast } from "react-toastify";

const Register = () => {
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const navigate = useNavigate();

  const notify = (msg, type) => toast[type](msg);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(
        "http://ai-price-tracker-production.up.railway.app/api/auth/register",
        form,
        {
          withCredentials: true,
        }
      );
      navigate("/login");
    } catch (error) {
      console.log(error.response?.data.error);
      notify(error.response?.data.error || "Registration failed", "error");
    }
  };

  return (
    <div className="auth-container">
      <form onSubmit={handleSubmit} className="auth-form">
        <h2 className="form-title">Create Your Account</h2>

        <div className="form-group">
          <input
            type="text"
            placeholder="Name"
            className="form-input"
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            required
          />
        </div>

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
          Register
        </button>

        <p className="auth-prompt">
          Already have an account?{" "}
          <Link to={"/login"} className="auth-link">
            Log In
          </Link>
        </p>
      </form>
      <ToastContainer position="top-center" theme="light" autoClose={1000} />
    </div>
  );
};

export default Register;
