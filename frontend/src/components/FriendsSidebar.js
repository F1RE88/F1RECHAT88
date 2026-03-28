import React, { useState } from "react";
import { Search, UserPlus, UserCheck, UserX, Check, X } from "lucide-react";
import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function FriendsSidebar({
  friends,
  friendRequests,
  selectedFriend,
  onSelectFriend,
  onAcceptRequest,
  onRejectRequest,
  onSendFriendRequest,
  currentUser
}) {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [requestStatus, setRequestStatus] = useState("");
  const [showRequests, setShowRequests] = useState(false);

  const handleSearch = async (query) => {
    setSearchQuery(query);
    const cleaned = query.replace("@", "").trim();
    if (cleaned.length < 2) {
      setSearchResults([]);
      return;
    }
    setSearching(true);
    try {
      const { data } = await axios.get(`${API}/friends/search?q=${encodeURIComponent(cleaned)}`, { withCredentials: true });
      setSearchResults(data);
    } catch {
      setSearchResults([]);
    } finally {
      setSearching(false);
    }
  };

  const handleAddFriend = async (username) => {
    const result = await onSendFriendRequest(username);
    if (result.success) {
      setRequestStatus(`تم إرسال طلب صداقة إلى @${username}`);
      setSearchResults([]);
      setSearchQuery("");
    } else {
      setRequestStatus(result.error);
    }
    setTimeout(() => setRequestStatus(""), 3000);
  };

  return (
    <div className="flex flex-col h-full" data-testid="friends-sidebar">
      {/* Header */}
      <div className="p-4 border-b border-neutral-800">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-bold text-white font-['Cairo']">الأصدقاء</h2>
          {friendRequests.length > 0 && (
            <button
              data-testid="show-friend-requests-btn"
              onClick={() => setShowRequests(!showRequests)}
              className="relative bg-red-600/20 text-red-400 px-3 py-1 rounded-full text-xs font-semibold hover:bg-red-600/30 transition-colors"
            >
              {friendRequests.length} طلب
            </button>
          )}
        </div>

        {/* Search Input */}
        <div className="relative">
          <input
            data-testid="friend-search-input"
            type="text"
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            placeholder="البحث عن أصدقاء... @اسم_المستخدم"
            className="w-full bg-[#121212] border border-neutral-800 rounded-lg px-4 py-2.5 pr-10 text-white text-sm focus:outline-none focus:border-red-600 focus:ring-1 focus:ring-red-600 transition-colors placeholder-gray-500 font-['Tajawal']"
          />
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
        </div>

        {/* Status message */}
        {requestStatus && (
          <div className="mt-2 text-xs text-red-400 bg-red-900/20 rounded-lg p-2 animate-fade-in" data-testid="friend-request-status">
            {requestStatus}
          </div>
        )}
      </div>

      {/* Search Results */}
      {searchResults.length > 0 && (
        <div className="border-b border-neutral-800 p-2" data-testid="search-results">
          <p className="text-xs text-gray-500 px-2 mb-1 font-['Tajawal']">نتائج البحث</p>
          {searchResults.map((result) => (
            <div
              key={result.id}
              className="flex items-center justify-between p-2 rounded-lg hover:bg-[#1A1A1A] transition-colors"
            >
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-neutral-800 flex items-center justify-center text-sm text-gray-300">
                  {result.username[0].toUpperCase()}
                </div>
                <span className="text-sm text-gray-200">@{result.username}</span>
              </div>
              <button
                data-testid={`add-friend-${result.username}`}
                onClick={() => handleAddFriend(result.username)}
                className="text-red-400 hover:text-red-300 transition-colors p-1.5 hover:bg-red-600/10 rounded-lg"
              >
                <UserPlus className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Friend Requests */}
      {showRequests && friendRequests.length > 0 && (
        <div className="border-b border-neutral-800 p-2" data-testid="friend-requests-panel">
          <p className="text-xs text-gray-500 px-2 mb-1 font-['Tajawal']">طلبات الصداقة</p>
          {friendRequests.map((req) => (
            <div
              key={req.from_id}
              className="flex items-center justify-between p-2 rounded-lg hover:bg-[#1A1A1A] transition-colors animate-fade-in"
            >
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-neutral-800 flex items-center justify-center text-sm text-gray-300">
                  {req.from_username[0].toUpperCase()}
                </div>
                <span className="text-sm text-gray-200">@{req.from_username}</span>
              </div>
              <div className="flex gap-1">
                <button
                  data-testid={`accept-request-${req.from_username}`}
                  onClick={() => onAcceptRequest(req.from_username)}
                  className="text-green-400 hover:text-green-300 transition-colors p-1.5 hover:bg-green-600/10 rounded-lg"
                >
                  <Check className="w-4 h-4" />
                </button>
                <button
                  data-testid={`reject-request-${req.from_username}`}
                  onClick={() => onRejectRequest(req.from_username)}
                  className="text-red-400 hover:text-red-300 transition-colors p-1.5 hover:bg-red-600/10 rounded-lg"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Friends List */}
      <div className="flex-1 overflow-y-auto p-2" data-testid="friends-list">
        {friends.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center p-6">
            <UserX className="w-16 h-16 text-red-600/30 mb-3" />
            <p className="text-gray-500 text-sm font-['Tajawal']">
              لا يوجد أصدقاء بعد، الهدوء يعم المكان...
            </p>
            <p className="text-gray-600 text-xs mt-2 font-['Tajawal']">
              ابحث عن أصدقاء باستخدام @اسم_المستخدم
            </p>
          </div>
        ) : (
          friends.map((friend) => (
            <button
              key={friend.id}
              data-testid={`friend-item-${friend.username}`}
              onClick={() => onSelectFriend(friend)}
              className={`w-full flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-colors group mb-1 text-right ${
                selectedFriend?.id === friend.id
                  ? "bg-[#1A1A1A] border-r-2 border-red-600"
                  : "hover:bg-[#1A1A1A]"
              }`}
            >
              <div className="relative">
                <div className="w-10 h-10 rounded-full bg-neutral-800 flex items-center justify-center text-base font-semibold text-gray-200">
                  {friend.username[0].toUpperCase()}
                </div>
                <div className={`absolute bottom-0 left-0 w-3 h-3 rounded-full border-2 border-[#0A0A0A] ${
                  friend.online ? "bg-green-500" : "bg-gray-600"
                }`} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-200 truncate">@{friend.username}</p>
                <p className="text-xs text-gray-500">{friend.online ? "متصل" : "غير متصل"}</p>
              </div>
            </button>
          ))
        )}
      </div>
    </div>
  );
}
