import React, { useState, useEffect, useCallback } from "react";
import { useAuth } from "@/contexts/AuthContext";
import FriendsSidebar from "@/components/FriendsSidebar";
import ChatArea from "@/components/ChatArea";
import AdminPanel from "@/components/AdminPanel";
import axios from "axios";
import { Menu, X, Shield } from "lucide-react";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const [friends, setFriends] = useState([]);
  const [selectedFriend, setSelectedFriend] = useState(null);
  const [friendRequests, setFriendRequests] = useState([]);
  const [showSidebar, setShowSidebar] = useState(true);
  const [messages, setMessages] = useState([]);
  const [showAdmin, setShowAdmin] = useState(false);

  const fetchFriends = useCallback(async () => {
    try {
      const { data } = await axios.get(`${API}/friends`, { withCredentials: true });
      setFriends(data);
    } catch {
      // ignore
    }
  }, []);

  const fetchFriendRequests = useCallback(async () => {
    try {
      const { data } = await axios.get(`${API}/friends/requests`, { withCredentials: true });
      setFriendRequests(data);
    } catch {
      // ignore
    }
  }, []);

  const fetchMessages = useCallback(async (friendId) => {
    try {
      const { data } = await axios.get(`${API}/messages/${friendId}`, { withCredentials: true });
      setMessages(data);
    } catch {
      // ignore
    }
  }, []);

  useEffect(() => {
    fetchFriends();
    fetchFriendRequests();
    const interval = setInterval(() => {
      fetchFriends();
      fetchFriendRequests();
      if (selectedFriend) fetchMessages(selectedFriend.id);
    }, 5000);
    return () => clearInterval(interval);
  }, [fetchFriends, fetchFriendRequests, fetchMessages, selectedFriend]);

  useEffect(() => {
    if (selectedFriend) {
      fetchMessages(selectedFriend.id);
    }
  }, [selectedFriend, fetchMessages]);

  const handleSelectFriend = (friend) => {
    setSelectedFriend(friend);
    setShowSidebar(false);
  };

  const handleSendMessage = async (content) => {
    if (!selectedFriend || !content.trim()) return;
    try {
      await axios.post(`${API}/messages`, {
        receiver_id: selectedFriend.id,
        content: content.trim()
      }, { withCredentials: true });
      fetchMessages(selectedFriend.id);
    } catch {
      // ignore
    }
  };

  const handleAcceptRequest = async (username) => {
    try {
      await axios.post(`${API}/friends/accept`, { username }, { withCredentials: true });
      fetchFriends();
      fetchFriendRequests();
    } catch {
      // ignore
    }
  };

  const handleRejectRequest = async (username) => {
    try {
      await axios.post(`${API}/friends/reject`, { username }, { withCredentials: true });
      fetchFriendRequests();
    } catch {
      // ignore
    }
  };

  const handleSendFriendRequest = async (username) => {
    try {
      await axios.post(`${API}/friends/request`, { username }, { withCredentials: true });
      return { success: true };
    } catch (e) {
      const detail = e.response?.data?.detail;
      return { success: false, error: typeof detail === "string" ? detail : "Failed to send request" };
    }
  };

  return (
    <div className="flex h-screen w-full overflow-hidden bg-[#050505] text-gray-100" data-testid="dashboard-page">
      {/* Mobile toggle */}
      <button
        data-testid="toggle-sidebar-mobile"
        onClick={() => setShowSidebar(!showSidebar)}
        className="md:hidden fixed top-3 left-3 z-50 bg-[#121212] border border-neutral-800 rounded-lg p-2 text-gray-400 hover:text-white transition-colors"
      >
        {showSidebar ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
      </button>

      {/* Chat Area */}
      <ChatArea
        selectedFriend={selectedFriend}
        messages={messages}
        onSendMessage={handleSendMessage}
        currentUser={user}
        onLogout={logout}
        onBack={() => { setSelectedFriend(null); setShowSidebar(true); }}
        onOpenAdmin={() => setShowAdmin(true)}
      />

      {/* Friends Sidebar */}
      <div className={`${showSidebar ? 'flex' : 'hidden'} md:flex w-full md:w-80 lg:w-96 flex-shrink-0 border-l border-neutral-800 bg-[#0A0A0A] flex-col absolute md:relative inset-0 z-40 md:z-auto`}>
        <FriendsSidebar
          friends={friends}
          friendRequests={friendRequests}
          selectedFriend={selectedFriend}
          onSelectFriend={handleSelectFriend}
          onAcceptRequest={handleAcceptRequest}
          onRejectRequest={handleRejectRequest}
          onSendFriendRequest={handleSendFriendRequest}
          currentUser={user}
        />
      </div>

      {/* Admin Panel Modal */}
      {showAdmin && <AdminPanel onClose={() => setShowAdmin(false)} />}
    </div>
  );
}
