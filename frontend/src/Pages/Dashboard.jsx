import React from "react";
import { useNavigate } from "react-router-dom";

export default function Dashboard() {
  const navigate = useNavigate();

  const categories = [
    { title: "HR Round", desc: "General HR questions to test communication." },
    { title: "Software Engineer", desc: "DSA, OOP, System Design, logic." },
    { title: "Frontend Developer", desc: "React, JS, HTML, CSS questions." },
    { title: "Backend Developer", desc: "APIs, Databases, Python/Node.js." },
    { title: "DevOps", desc: "CI/CD, Docker, Kubernetes basics." },
  ];

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">
        Interview Dashboard
      </h1>
      <p className="text-gray-600 mb-8">
        Select a topic to start your mock interview powered by AI.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {categories.map((cat, index) => (
          <div
            key={index}
            className="bg-white p-6 rounded-xl shadow hover:shadow-xl transition cursor-pointer"
            onClick={() => navigate("/interview")}
          >
            <h2 className="text-xl font-semibold text-gray-800">{cat.title}</h2>
            <p className="text-gray-600 mt-2">{cat.desc}</p>
            <button className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
              Start Interview
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
