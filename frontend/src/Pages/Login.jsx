import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      const res = await fetch("http://127.0.0.1:8000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (res.ok) {
        // store JWT token
        localStorage.setItem("token", data.access_token);

        alert("Login successful!");
        navigate("/dashboard"); // redirect after login
      } else {
        alert(data.detail || "Invalid credentials!");
      }
    } catch (error) {
      console.error("Login error:", error);
      alert("Server error. Try again.");
    }
  };

  return (
    <div className="flex items-center justify-center h-screen bg-gray-100">
      <div className="w-full max-w-sm bg-white p-8 rounded-2xl shadow-lg">

        <h2 className="text-2xl font-bold mb-6 text-center text-gray-700">
          Login to Account
        </h2>

        <form onSubmit={handleLogin} className="space-y-4">

          <div>
            <label className="text-gray-600 font-medium">Email</label>
            <input
              type="email"
              className="w-full px-3 py-2 border rounded-lg"
              placeholder="example@gmail.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div>
            <label className="text-gray-600 font-medium">Password</label>
            <input
              type="password"
              className="w-full px-3 py-2 border rounded-lg"
              placeholder="Enter password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            className="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            Login
          </button>
        </form>

        <p className="text-center text-gray-600 mt-4">
          Don't have an account?
          <span
            className="text-blue-600 cursor-pointer ml-1"
            onClick={() => navigate("/register")}
          >
            Create Account
          </span>
        </p>

      </div>
    </div>
  );
}
