import React, { useState, useRef, useEffect } from "react";
import { Send, Smile, Paperclip, MoreVertical, LogOut, ArrowRight, Shield, Palette, X } from "lucide-react";
import axios from "axios";

const LOGO_URL = "https://customer-assets.emergentagent.com/job_secure-social-hub-2/artifacts/dki0o21d_LOGO.png";
const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const CHAT_BACKGROUNDS = [
  { id: "default", label: "Default", value: "#050505" },
  { id: "dark-gray", label: "Dark Gray", value: "#111111" },
  { id: "midnight", label: "Midnight", value: "#0D1117" },
  { id: "deep-navy", label: "Deep Navy", value: "#0A1628" },
  { id: "charcoal", label: "Charcoal", value: "#1A1A2E" },
  { id: "dark-green", label: "Dark Forest", value: "#0A1A0F" },
  { id: "dark-red", label: "Dark Wine", value: "#1A0A0A" },
  { id: "dark-purple", label: "Dark Purple", value: "#120A1A" },
  { id: "gradient-1", label: "Ember", value: "linear-gradient(135deg, #0A0A0A 0%, #1A0A0A 100%)" },
  { id: "gradient-2", label: "Ocean", value: "linear-gradient(135deg, #0A0A0A 0%, #0A0D1A 100%)" },
  { id: "gradient-3", label: "Forest", value: "linear-gradient(135deg, #0A0A0A 0%, #0A1A0F 100%)" },
  { id: "pattern-dots", label: "Dots", value: "#050505", pattern: "radial-gradient(circle, #1A1A1A 1px, transparent 1px)" },
];

export default function ChatArea({ selectedFriend, messages, onSendMessage, currentUser, onLogout, onBack, onOpenAdmin }) {
  const [messageText, setMessageText] = useState("");
  const [showBgPicker, setShowBgPicker] = useState(false);
  const [chatBg, setChatBg] = useState("default");
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Load saved background
  useEffect(() => {
    const loadBg = async () => {
      try {
        const { data } = await axios.get(`${API}/settings/chat-background`, { withCredentials: true });
        if (data.background && data.background !== "default") {
          setChatBg(data.background);
        }
      } catch {
        // ignore
      }
    };
    loadBg();
  }, []);

  const handleSend = (e) => {
    e.preventDefault();
    if (!messageText.trim()) return;
    onSendMessage(messageText);
    setMessageText("");
  };

  const handleBgChange = async (bgId) => {
    setChatBg(bgId);
    setShowBgPicker(false);
    try {
      await axios.put(`${API}/settings/chat-background`, { background: bgId }, { withCredentials: true });
    } catch {
      // ignore
    }
  };

  const getProfileImageUrl = (friend) => {
    if (friend?.profile_image) {
      return `${API}/files/${friend.profile_image}`;
    }
    return null;
  };

  const getBgStyle = () => {
    const bg = CHAT_BACKGROUNDS.find(b => b.id === chatBg) || CHAT_BACKGROUNDS[0];
    const style = {};
    if (bg.value.startsWith("linear-gradient")) {
      style.background = bg.value;
    } else {
      style.backgroundColor = bg.value;
    }
    if (bg.pattern) {
      style.backgroundImage = bg.pattern;
      style.backgroundSize = "20px 20px";
    }
    return style;
  };

  if (!selectedFriend) {
    return (
      <div className="flex-1 flex flex-col bg-[#050505] relative" data-testid="chat-area-empty">
        {/* Header */}
        <div className="h-14 border-b border-neutral-800 bg-[#0A0A0A] flex items-center justify-between px-4">
          <div className="flex items-center gap-3">
            <img src={LOGO_URL} alt="F1RECHAT" className="w-8 h-8 object-contain" />
            <div>
              <p className="text-sm font-semibold text-white font-['Cairo']">F1RECHAT</p>
              <p className="text-xs text-gray-500 font-['Tajawal']">Waiting for connection...</p>
            </div>
          </div>
          <div className="flex items-center gap-1">
            <button
              data-testid="admin-control-button"
              onClick={onOpenAdmin}
              className="text-orange-400 hover:text-orange-300 transition-colors p-2 hover:bg-orange-600/10 rounded-lg flex items-center gap-1.5 text-xs font-semibold"
              title="Admin Control"
            >
              <Shield className="w-4 h-4" />
              <span className="hidden sm:inline">Admin</span>
            </button>
            <button
              data-testid="bg-picker-button"
              onClick={() => setShowBgPicker(!showBgPicker)}
              className="text-gray-400 hover:text-gray-200 transition-colors p-2 hover:bg-neutral-800 rounded-lg"
              title="Change chat background"
            >
              <Palette className="w-4 h-4" />
            </button>
            <button
              data-testid="logout-button"
              onClick={onLogout}
              className="text-gray-500 hover:text-red-400 transition-colors p-2 hover:bg-neutral-800 rounded-lg"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Background Picker */}
        {showBgPicker && (
          <BackgroundPicker
            current={chatBg}
            onSelect={handleBgChange}
            onClose={() => setShowBgPicker(false)}
          />
        )}

        {/* Empty state */}
        <div className="flex-1 flex items-center justify-center" style={getBgStyle()}>
          <div className="text-center">
            <img src={LOGO_URL} alt="F1RECHAT" className="w-24 h-24 mx-auto mb-4 opacity-30" />
            <p className="text-gray-600 font-['Tajawal']">Select a friend to start chatting</p>
          </div>
        </div>

        {/* Disabled input */}
        <div className="p-4 border-t border-neutral-800 bg-[#0A0A0A]">
          <div className="flex items-center gap-2">
            <button className="text-red-500/30 p-2" disabled>
              <Send className="w-5 h-5" />
            </button>
            <div className="flex-1 bg-[#121212] border border-neutral-800 rounded-2xl px-4 py-3 text-gray-600 text-sm font-['Tajawal']">
              Type a message...
            </div>
            <button className="text-gray-600 p-2" disabled>
              <Smile className="w-5 h-5" />
            </button>
            <button className="text-gray-600 p-2" disabled>
              <Paperclip className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    );
  }

  const friendImageUrl = getProfileImageUrl(selectedFriend);

  return (
    <div className="flex-1 flex flex-col bg-[#050505] relative" data-testid="chat-area-active">
      {/* Chat Header */}
      <div className="h-14 border-b border-neutral-800 bg-[#0A0A0A] flex items-center justify-between px-4">
        <div className="flex items-center gap-3">
          <button
            data-testid="chat-back-button"
            onClick={onBack}
            className="md:hidden text-gray-400 hover:text-white transition-colors p-1"
          >
            <ArrowRight className="w-5 h-5" />
          </button>
          <div className="relative">
            {friendImageUrl ? (
              <img src={friendImageUrl} alt={selectedFriend.username} className="w-9 h-9 rounded-full object-cover" />
            ) : (
              <div className="w-9 h-9 rounded-full bg-neutral-800 flex items-center justify-center text-sm font-semibold text-gray-200">
                {selectedFriend.username[0].toUpperCase()}
              </div>
            )}
            <div className={`absolute bottom-0 left-0 w-2.5 h-2.5 rounded-full border-2 border-[#0A0A0A] ${
              selectedFriend.online ? "bg-green-500" : "bg-gray-600"
            }`} />
          </div>
          <div>
            <p className="text-sm font-semibold text-white font-['Cairo']">@{selectedFriend.username}</p>
            <p className="text-xs text-gray-500 font-['Tajawal']">
              {selectedFriend.online ? "Online" : "Offline"}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button
            data-testid="admin-control-button-chat"
            onClick={onOpenAdmin}
            className="text-orange-400 hover:text-orange-300 transition-colors p-2 hover:bg-orange-600/10 rounded-lg flex items-center gap-1.5 text-xs font-semibold"
            title="Admin Control"
          >
            <Shield className="w-4 h-4" />
            <span className="hidden sm:inline">Admin</span>
          </button>
          <button
            data-testid="bg-picker-button-chat"
            onClick={() => setShowBgPicker(!showBgPicker)}
            className="text-gray-400 hover:text-gray-200 transition-colors p-2 hover:bg-neutral-800 rounded-lg"
            title="Change chat background"
          >
            <Palette className="w-4 h-4" />
          </button>
          <button
            data-testid="logout-button"
            onClick={onLogout}
            className="text-gray-500 hover:text-red-400 transition-colors p-2 hover:bg-neutral-800 rounded-lg"
            title="Logout"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Background Picker */}
      {showBgPicker && (
        <BackgroundPicker
          current={chatBg}
          onSelect={handleBgChange}
          onClose={() => setShowBgPicker(false)}
        />
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3" style={getBgStyle()} data-testid="messages-container">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-gray-600 text-sm font-['Tajawal']">No messages yet, start the conversation!</p>
          </div>
        ) : (
          messages.map((msg, idx) => {
            const isMine = msg.sender_id === currentUser?.id;
            return (
              <div
                key={idx}
                className={`flex ${isMine ? "justify-end" : "justify-start"} animate-fade-in`}
                data-testid={`message-${idx}`}
              >
                <div
                  className={`max-w-[80%] px-4 py-2 ${
                    isMine
                      ? "bg-red-600 text-white rounded-2xl rounded-br-sm"
                      : "bg-[#1A1A1A] text-gray-100 rounded-2xl rounded-bl-sm border border-neutral-800"
                  }`}
                >
                  <p className="text-sm font-['Tajawal']">{msg.content}</p>
                  <p className={`text-[10px] mt-1 ${isMine ? "text-red-200" : "text-gray-500"}`}>
                    {new Date(msg.created_at).toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" })}
                  </p>
                </div>
              </div>
            );
          })
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Message Input */}
      <form onSubmit={handleSend} className="p-4 border-t border-neutral-800 bg-[#0A0A0A]" data-testid="message-form">
        <div className="flex items-center gap-2">
          <button
            type="submit"
            data-testid="send-message-button"
            className="text-red-500 hover:text-red-400 transition-colors p-2 hover:bg-red-600/10 rounded-lg"
          >
            <Send className="w-5 h-5" />
          </button>
          <input
            data-testid="message-input"
            type="text"
            value={messageText}
            onChange={(e) => setMessageText(e.target.value)}
            placeholder="Type a message..."
            className="flex-1 bg-[#121212] border border-neutral-800 rounded-2xl px-4 py-3 text-white text-sm focus:outline-none focus:border-red-600 focus:ring-1 focus:ring-red-600 placeholder-gray-600 font-['Tajawal']"
          />
          <button type="button" className="text-gray-500 hover:text-gray-300 transition-colors p-2">
            <Smile className="w-5 h-5" />
          </button>
          <button type="button" className="text-gray-500 hover:text-gray-300 transition-colors p-2">
            <Paperclip className="w-5 h-5" />
          </button>
        </div>
      </form>
    </div>
  );
}

function BackgroundPicker({ current, onSelect, onClose }) {
  return (
    <div className="absolute top-14 right-0 z-30 w-72 bg-[#0A0A0A] border border-neutral-800 rounded-xl shadow-2xl shadow-black/60 p-3 animate-fade-in" data-testid="bg-picker-panel">
      <div className="flex items-center justify-between mb-3">
        <p className="text-sm font-semibold text-white font-['Cairo']">Chat Background</p>
        <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
          <X className="w-4 h-4" />
        </button>
      </div>
      <div className="grid grid-cols-4 gap-2">
        {CHAT_BACKGROUNDS.map((bg) => (
          <button
            key={bg.id}
            data-testid={`bg-option-${bg.id}`}
            onClick={() => onSelect(bg.id)}
            className={`w-full aspect-square rounded-lg border-2 transition-all hover:scale-105 ${
              current === bg.id ? "border-red-500 ring-1 ring-red-500/50" : "border-neutral-700 hover:border-neutral-500"
            }`}
            style={{
              background: bg.value.startsWith("linear") ? bg.value : bg.value,
              backgroundImage: bg.pattern || undefined,
              backgroundSize: bg.pattern ? "10px 10px" : undefined,
            }}
            title={bg.label}
          />
        ))}
      </div>
      <p className="text-xs text-gray-500 mt-2 text-center font-['Tajawal']">Choose your chat background</p>
    </div>
  );
}
