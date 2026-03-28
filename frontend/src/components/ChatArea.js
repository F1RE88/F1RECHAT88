import React, { useState, useRef, useEffect } from "react";
import { Send, Smile, Paperclip, MoreVertical, Ghost, LogOut, ArrowRight } from "lucide-react";

export default function ChatArea({ selectedFriend, messages, onSendMessage, currentUser, onLogout, onBack }) {
  const [messageText, setMessageText] = useState("");
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = (e) => {
    e.preventDefault();
    if (!messageText.trim()) return;
    onSendMessage(messageText);
    setMessageText("");
  };

  if (!selectedFriend) {
    return (
      <div className="flex-1 flex flex-col bg-[#050505] relative" data-testid="chat-area-empty">
        {/* Header */}
        <div className="h-14 border-b border-neutral-800 bg-[#0A0A0A] flex items-center justify-between px-4">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-red-600/20 flex items-center justify-center">
              <Ghost className="w-5 h-5 text-red-500" />
            </div>
            <div>
              <p className="text-sm font-semibold text-white font-['Cairo']">الفراغ</p>
              <p className="text-xs text-gray-500 font-['Tajawal']">بانتظار الاتصال...</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              data-testid="logout-button"
              onClick={onLogout}
              className="text-gray-500 hover:text-red-400 transition-colors p-2 hover:bg-neutral-800 rounded-lg"
              title="تسجيل الخروج"
            >
              <LogOut className="w-4 h-4" />
            </button>
            <button className="text-gray-500 hover:text-gray-300 transition-colors p-2 hover:bg-neutral-800 rounded-lg">
              <MoreVertical className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Empty state */}
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <Ghost className="w-20 h-20 text-neutral-800 mx-auto mb-4" />
            <p className="text-gray-600 font-['Tajawal']">اختر صديقاً لبدء المحادثة</p>
          </div>
        </div>

        {/* Disabled input */}
        <div className="p-4 border-t border-neutral-800 bg-[#0A0A0A]">
          <div className="flex items-center gap-2">
            <button className="text-red-500/30 p-2" disabled>
              <Send className="w-5 h-5" />
            </button>
            <div className="flex-1 bg-[#121212] border border-neutral-800 rounded-2xl px-4 py-3 text-gray-600 text-sm font-['Tajawal']">
              اكتب رسالة في الفراغ...
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

  return (
    <div className="flex-1 flex flex-col bg-[#050505] relative" data-testid="chat-area-active">
      {/* Chat Header */}
      <div className="h-14 border-b border-neutral-800 bg-[#0A0A0A] flex items-center justify-between px-4">
        <div className="flex items-center gap-3">
          {/* Back button for mobile */}
          <button
            data-testid="chat-back-button"
            onClick={onBack}
            className="md:hidden text-gray-400 hover:text-white transition-colors p-1"
          >
            <ArrowRight className="w-5 h-5" />
          </button>
          <div className="relative">
            <div className="w-9 h-9 rounded-full bg-neutral-800 flex items-center justify-center text-sm font-semibold text-gray-200">
              {selectedFriend.username[0].toUpperCase()}
            </div>
            <div className={`absolute bottom-0 left-0 w-2.5 h-2.5 rounded-full border-2 border-[#0A0A0A] ${
              selectedFriend.online ? "bg-green-500" : "bg-gray-600"
            }`} />
          </div>
          <div>
            <p className="text-sm font-semibold text-white font-['Cairo']">@{selectedFriend.username}</p>
            <p className="text-xs text-gray-500 font-['Tajawal']">
              {selectedFriend.online ? "متصل الآن" : "غير متصل"}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            data-testid="logout-button"
            onClick={onLogout}
            className="text-gray-500 hover:text-red-400 transition-colors p-2 hover:bg-neutral-800 rounded-lg"
            title="تسجيل الخروج"
          >
            <LogOut className="w-4 h-4" />
          </button>
          <button className="text-gray-500 hover:text-gray-300 transition-colors p-2 hover:bg-neutral-800 rounded-lg">
            <MoreVertical className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3" data-testid="messages-container">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-gray-600 text-sm font-['Tajawal']">لا توجد رسائل بعد، ابدأ المحادثة!</p>
          </div>
        ) : (
          messages.map((msg, idx) => {
            const isMine = msg.sender_id === currentUser?.id;
            return (
              <div
                key={idx}
                className={`flex ${isMine ? "justify-start" : "justify-end"} animate-fade-in`}
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
                    {new Date(msg.created_at).toLocaleTimeString("ar-EG", { hour: "2-digit", minute: "2-digit" })}
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
            placeholder="اكتب رسالة في الفراغ..."
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
