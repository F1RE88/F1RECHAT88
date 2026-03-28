import React, { useState, useEffect, useCallback } from "react";
import { useAuth } from "@/contexts/AuthContext";
import FriendsSidebar from "@/components/FriendsSidebar";
import ChatArea from "@/components/ChatArea";
import AdminPanel from "@/components/AdminPanel";
import CreateGroupModal from "@/components/CreateGroupModal";
import axios from "axios";
import { Menu, X } from "lucide-react";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const [friends, setFriends] = useState([]);
  const [selectedFriend, setSelectedFriend] = useState(null);
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [friendRequests, setFriendRequests] = useState([]);
  const [showSidebar, setShowSidebar] = useState(true);
  const [messages, setMessages] = useState([]);
  const [groupMessages, setGroupMessages] = useState([]);
  const [groups, setGroups] = useState([]);
  const [showAdmin, setShowAdmin] = useState(false);
  const [showCreateGroup, setShowCreateGroup] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  // --- Heartbeat (online/offline) ---
  useEffect(() => {
    const sendHeartbeat = async () => {
      try {
        await axios.post(`${API}/auth/heartbeat`, {}, { withCredentials: true });
      } catch {}
    };
    sendHeartbeat(); // immediate
    const interval = setInterval(sendHeartbeat, 30000); // every 30s
    return () => clearInterval(interval);
  }, []);

  // --- Set offline on page unload ---
  useEffect(() => {
    const handleUnload = () => {
      navigator.sendBeacon(`${API}/auth/logout`);
    };
    window.addEventListener("beforeunload", handleUnload);
    return () => window.removeEventListener("beforeunload", handleUnload);
  }, []);

  const fetchFriends = useCallback(async () => {
    try {
      const { data } = await axios.get(`${API}/friends`, { withCredentials: true });
      setFriends(data);
      // Update selected friend's online status
      if (selectedFriend) {
        const updated = data.find(f => f.id === selectedFriend.id);
        if (updated) setSelectedFriend(updated);
      }
    } catch {}
  }, [selectedFriend]);

  const fetchFriendRequests = useCallback(async () => {
    try {
      const { data } = await axios.get(`${API}/friends/requests`, { withCredentials: true });
      setFriendRequests(data);
    } catch {}
  }, []);

  const fetchMessages = useCallback(async (friendId) => {
    try {
      const { data } = await axios.get(`${API}/messages/${friendId}`, { withCredentials: true });
      setMessages(data);
    } catch {}
  }, []);

  const fetchGroups = useCallback(async () => {
    try {
      const { data } = await axios.get(`${API}/groups`, { withCredentials: true });
      setGroups(data);
    } catch {}
  }, []);

  const fetchGroupMessages = useCallback(async (groupId) => {
    try {
      const { data } = await axios.get(`${API}/groups/${groupId}/messages`, { withCredentials: true });
      setGroupMessages(data);
    } catch {}
  }, []);

  const fetchNotifications = useCallback(async () => {
    try {
      const [notifResp, countResp] = await Promise.all([
        axios.get(`${API}/notifications`, { withCredentials: true }),
        axios.get(`${API}/notifications/unread-count`, { withCredentials: true })
      ]);
      setNotifications(notifResp.data);
      setUnreadCount(countResp.data.count);
    } catch {}
  }, []);

  useEffect(() => {
    fetchFriends();
    fetchFriendRequests();
    fetchGroups();
    fetchNotifications();
    const interval = setInterval(() => {
      fetchFriends();
      fetchFriendRequests();
      fetchGroups();
      fetchNotifications();
      if (selectedFriend) fetchMessages(selectedFriend.id);
      if (selectedGroup) fetchGroupMessages(selectedGroup.id);
    }, 5000);
    return () => clearInterval(interval);
  }, [fetchFriends, fetchFriendRequests, fetchMessages, fetchGroups, fetchGroupMessages, fetchNotifications, selectedFriend, selectedGroup]);

  useEffect(() => {
    if (selectedFriend) fetchMessages(selectedFriend.id);
  }, [selectedFriend, fetchMessages]);

  useEffect(() => {
    if (selectedGroup) fetchGroupMessages(selectedGroup.id);
  }, [selectedGroup, fetchGroupMessages]);

  const handleSelectFriend = (friend) => {
    setSelectedFriend(friend);
    setSelectedGroup(null);
    setGroupMessages([]);
    setShowSidebar(false);
  };

  const handleSelectGroup = (group) => {
    setSelectedGroup(group);
    setSelectedFriend(null);
    setMessages([]);
    setShowSidebar(false);
  };

  const handleSendMessage = async (content) => {
    if (!selectedFriend || !content.trim()) return;
    try {
      await axios.post(`${API}/messages`, { receiver_id: selectedFriend.id, content: content.trim() }, { withCredentials: true });
      fetchMessages(selectedFriend.id);
    } catch {}
  };

  const handleSendGroupMessage = async (content) => {
    if (!selectedGroup || !content.trim()) return;
    try {
      await axios.post(`${API}/groups/${selectedGroup.id}/messages`, { content: content.trim() }, { withCredentials: true });
      fetchGroupMessages(selectedGroup.id);
    } catch {}
  };

  const handleAcceptRequest = async (username) => {
    try {
      await axios.post(`${API}/friends/accept`, { username }, { withCredentials: true });
      fetchFriends();
      fetchFriendRequests();
    } catch {}
  };

  const handleRejectRequest = async (username) => {
    try {
      await axios.post(`${API}/friends/reject`, { username }, { withCredentials: true });
      fetchFriendRequests();
    } catch {}
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

  const handleCreateGroup = async (name, memberIds) => {
    try {
      await axios.post(`${API}/groups`, { name, member_ids: memberIds }, { withCredentials: true });
      setShowCreateGroup(false);
      fetchGroups();
      return { success: true };
    } catch (e) {
      const detail = e.response?.data?.detail;
      return { success: false, error: typeof detail === "string" ? detail : "Failed to create group" };
    }
  };

  const handleMarkNotificationsRead = async () => {
    try {
      await axios.put(`${API}/notifications/read`, {}, { withCredentials: true });
      setUnreadCount(0);
      setNotifications(prev => prev.map(n => ({ ...n, read: true })));
    } catch {}
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
        selectedGroup={selectedGroup}
        messages={messages}
        groupMessages={groupMessages}
        onSendMessage={handleSendMessage}
        onSendGroupMessage={handleSendGroupMessage}
        currentUser={user}
        onLogout={logout}
        onBack={() => { setSelectedFriend(null); setSelectedGroup(null); setShowSidebar(true); }}
        onOpenAdmin={() => setShowAdmin(true)}
        notifications={notifications}
        unreadCount={unreadCount}
        onMarkNotificationsRead={handleMarkNotificationsRead}
      />

      {/* Friends/Groups Sidebar */}
      <div className={`${showSidebar ? 'flex' : 'hidden'} md:flex w-full md:w-80 lg:w-96 flex-shrink-0 border-l border-neutral-800 bg-[#0A0A0A] flex-col absolute md:relative inset-0 z-40 md:z-auto`}>
        <FriendsSidebar
          friends={friends}
          friendRequests={friendRequests}
          selectedFriend={selectedFriend}
          selectedGroup={selectedGroup}
          groups={groups}
          onSelectFriend={handleSelectFriend}
          onSelectGroup={handleSelectGroup}
          onAcceptRequest={handleAcceptRequest}
          onRejectRequest={handleRejectRequest}
          onSendFriendRequest={handleSendFriendRequest}
          onCreateGroup={() => setShowCreateGroup(true)}
          currentUser={user}
        />
      </div>

      {/* Admin Panel */}
      {showAdmin && <AdminPanel onClose={() => setShowAdmin(false)} />}

      {/* Create Group Modal */}
      {showCreateGroup && (
        <CreateGroupModal
          friends={friends}
          onClose={() => setShowCreateGroup(false)}
          onCreate={handleCreateGroup}
        />
      )}
    </div>
  );
}
