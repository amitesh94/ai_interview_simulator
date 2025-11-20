import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./Pages/Login";
import Dashboard from "./Pages/Dashboard";
import Interview from "./Pages/Interview"; // We will create this next
import Register from "./Pages/Register";
import ProtectedRoute from "./Components/ProtectedRoute";
function App() {
  return (
    <Router>
     <Routes>
  <Route path="/" element={<Login />} />
  <Route path="/register" element={<Register />} />

  <Route
    path="/dashboard"
    element={
      <ProtectedRoute>
        <Dashboard />
      </ProtectedRoute>
    }
  />

  <Route
    path="/interview"
    element={
      <ProtectedRoute>
        <Interview />
      </ProtectedRoute>
    }
  />
</Routes>

    </Router>
  );
}

export default App;
