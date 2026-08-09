import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import NewRecord from "./pages/NewRecord";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<Login />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/records/new" element={<NewRecord />} />
      {/* Records list, Companies, Users, Reports, Settings land in later modules */}
    </Routes>
  );
}
