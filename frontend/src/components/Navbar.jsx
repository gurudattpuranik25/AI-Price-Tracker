import React from "react";
import { Link } from "react-router-dom";

const Navbar = () => (
  <nav>
    <Link to="/register">Register</Link> | <Link to="/login">Login</Link> |{" "}
    <Link to="/dashboard">Dashboard</Link>
  </nav>
);

export default Navbar;
