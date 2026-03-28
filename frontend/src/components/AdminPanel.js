import React, { useState, useEffect } from "react";
import { Shield, X, Trash2, Edit3, Eye, EyeOff, Users, Lock, Check, ArrowLeft } from "lucide-react";
import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function AdminPanel({ onClose }) {
  const [authenticated, setAuthenticated] = useState(false);
  const [adminToken, setAdminToken] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [newUsername, setNewUsername] = useState("");
  const [showPasswords, setShowPasswords] = useState({});

  const handleAdminLogin = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const { data } = await axios.post(`${API}/admin/verify`, { password });
      setAdminToken(data.admin_token);
      setAuthenticated(true);
    } catch (e) {
      setError(e.response?.data?.detail || "Invalid password");
    }
    setLoading(false);
  };

  const fetchUsers = async () => {
    if (!adminToken) return;
    try {
      const { data } = await axios.get(`${API}/admin/users`, {
        headers: { "X-Admin-Token": adminToken }
      });
      setUsers(data);
    } catch {
      // ignore
    }
  };

  useEffect(() => {
    if (authenticated) fetchUsers();
  }, [authenticated]);

  const handleDeleteUser = async (userId, username) => {
    if (!window.confirm(`Are you sure you want to delete @${username}? This cannot be undone.`)) return;
    try {
      await axios.delete(`${API}/admin/users/${userId}`, {
        headers: { "X-Admin-Token": adminToken }
      });
      fetchUsers();
    } catch {
      // ignore
    }
  };

  const handleChangeUsername = async (userId) => {
    if (!newUsername.trim()) return;
    try {
      await axios.put(`${API}/admin/users/${userId}/username`,
        { new_username: newUsername },
        { headers: { "X-Admin-Token": adminToken } }
      );
      setEditingUser(null);
      setNewUsername("");
      fetchUsers();
    } catch (e) {
      setError(e.response?.data?.detail || "Failed to change username");
      setTimeout(() => setError(""), 3000);
    }
  };

  const togglePasswordVisibility = (userId) => {
    setShowPasswords(prev => ({ ...prev, [userId]: !prev[userId] }));
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4" data-testid="admin-panel-overlay">
      <div className="bg-[#0A0A0A] border border-neutral-800 rounded-2xl w-full max-w-3xl max-h-[85vh] flex flex-col shadow-2xl animate-fade-in" data-testid="admin-panel">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-neutral-800">
          <div className="flex items-center gap-3">
            <Shield className="w-6 h-6 text-red-500" />
            <h2 className="text-lg font-bold text-white font-['Cairo']">Admin Control Panel</h2>
          </div>
          <button
            onClick={onClose}
            data-testid="admin-panel-close"
            className="text-gray-400 hover:text-white transition-colors p-2 hover:bg-neutral-800 rounded-lg"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {!authenticated ? (
            <form onSubmit={handleAdminLogin} className="max-w-sm mx-auto space-y-4 py-8">
              <div className="text-center mb-6">
                <Lock className="w-12 h-12 text-red-500/50 mx-auto mb-3" />
                <p className="text-gray-400 text-sm font-['Tajawal']">Enter admin password to access controls</p>
              </div>

              <div className="relative">
                <input
                  data-testid="admin-password-input"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter admin password"
                  className="w-full bg-[#121212] border border-neutral-800 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-red-600 focus:ring-1 focus:ring-red-600 transition-colors placeholder-gray-600 font-['Tajawal']"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>

              {error && (
                <div className="text-red-400 text-sm bg-red-900/20 border border-red-800/30 rounded-lg p-3" data-testid="admin-error">
                  {error}
                </div>
              )}

              <button
                data-testid="admin-login-button"
                type="submit"
                disabled={loading}
                className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-3 px-4 rounded-lg transition-all flex justify-center items-center gap-2 disabled:opacity-50 font-['Cairo']"
              >
                {loading ? (
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <>Access Admin <ArrowLeft className="w-4 h-4" /></>
                )}
              </button>
            </form>
          ) : (
            <div className="space-y-3">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Users className="w-5 h-5 text-red-400" />
                  <span className="text-gray-300 text-sm font-['Cairo']">Total Users: {users.length}</span>
                </div>
                <button
                  onClick={fetchUsers}
                  data-testid="admin-refresh-users"
                  className="text-xs text-gray-400 hover:text-white bg-neutral-800 px-3 py-1.5 rounded-lg transition-colors"
                >
                  Refresh
                </button>
              </div>

              {error && (
                <div className="text-red-400 text-sm bg-red-900/20 border border-red-800/30 rounded-lg p-3 mb-3" data-testid="admin-error">
                  {error}
                </div>
              )}

              {users.map((u) => (
                <div key={u.id} className="bg-[#121212] border border-neutral-800 rounded-xl p-4 hover:border-neutral-700 transition-colors" data-testid={`admin-user-${u.username}`}>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      <div className="w-10 h-10 rounded-full bg-neutral-800 flex items-center justify-center text-sm font-semibold text-gray-200 flex-shrink-0">
                        {u.username ? u.username[0].toUpperCase() : "?"}
                      </div>
                      <div className="min-w-0">
                        {editingUser === u.id ? (
                          <div className="flex items-center gap-2">
                            <input
                              data-testid={`edit-username-input-${u.id}`}
                              type="text"
                              value={newUsername}
                              onChange={(e) => setNewUsername(e.target.value)}
                              placeholder="New username"
                              className="bg-[#0A0A0A] border border-neutral-700 rounded px-2 py-1 text-white text-sm w-32 focus:outline-none focus:border-red-600"
                              autoFocus
                            />
                            <button
                              data-testid={`save-username-${u.id}`}
                              onClick={() => handleChangeUsername(u.id)}
                              className="text-green-400 hover:text-green-300 p-1"
                            >
                              <Check className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => { setEditingUser(null); setNewUsername(""); }}
                              className="text-gray-400 hover:text-gray-300 p-1"
                            >
                              <X className="w-4 h-4" />
                            </button>
                          </div>
                        ) : (
                          <p className="text-sm font-semibold text-white truncate">@{u.username}</p>
                        )}
                        <p className="text-xs text-gray-500 truncate">{u.email}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-xs text-gray-600">Password:</span>
                          <span className="text-xs text-orange-400 font-mono" data-testid={`user-password-${u.id}`}>
                            {showPasswords[u.id] ? (u.plain_password || "N/A") : "••••••••"}
                          </span>
                          <button
                            onClick={() => togglePasswordVisibility(u.id)}
                            data-testid={`toggle-password-${u.id}`}
                            className="text-gray-500 hover:text-gray-300 transition-colors"
                          >
                            {showPasswords[u.id] ? <EyeOff className="w-3 h-3" /> : <Eye className="w-3 h-3" />}
                          </button>
                        </div>
                        <p className="text-xs text-gray-600 mt-0.5">Friends: {u.friends_count} | Created: {new Date(u.created_at).toLocaleDateString()}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-1 flex-shrink-0 ml-2">
                      <button
                        data-testid={`edit-user-${u.id}`}
                        onClick={() => { setEditingUser(u.id); setNewUsername(u.username); }}
                        className="text-blue-400 hover:text-blue-300 p-2 hover:bg-blue-600/10 rounded-lg transition-colors"
                        title="Change username"
                      >
                        <Edit3 className="w-4 h-4" />
                      </button>
                      <button
                        data-testid={`delete-user-${u.id}`}
                        onClick={() => handleDeleteUser(u.id, u.username)}
                        className="text-red-400 hover:text-red-300 p-2 hover:bg-red-600/10 rounded-lg transition-colors"
                        title="Delete user"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
