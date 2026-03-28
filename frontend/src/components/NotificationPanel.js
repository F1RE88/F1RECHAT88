import React from "react";
import { X, UserPlus, UserCheck, MessageSquare, Users } from "lucide-react";

const NOTIF_ICONS = {
  friend_request: UserPlus,
  friend_accepted: UserCheck,
  new_message: MessageSquare,
  group_message: Users,
};

const NOTIF_COLORS = {
  friend_request: "text-blue-400 bg-blue-600/10",
  friend_accepted: "text-green-400 bg-green-600/10",
  new_message: "text-red-400 bg-red-600/10",
  group_message: "text-orange-400 bg-orange-600/10",
};

export default function NotificationPanel({ notifications, onClose, onMarkRead }) {
  const Icon = ({ type }) => {
    const IconComp = NOTIF_ICONS[type] || MessageSquare;
    const color = NOTIF_COLORS[type] || "text-gray-400 bg-neutral-800";
    return (
      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${color}`}>
        <IconComp className="w-4 h-4" />
      </div>
    );
  };

  const timeAgo = (dateStr) => {
    const now = new Date();
    const then = new Date(dateStr);
    const diff = Math.floor((now - then) / 1000);
    if (diff < 60) return "just now";
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
  };

  return (
    <div className="absolute top-14 right-0 z-30 w-80 bg-[#0A0A0A] border border-neutral-800 rounded-xl shadow-2xl shadow-black/60 animate-fade-in" data-testid="notification-panel">
      <div className="flex items-center justify-between p-3 border-b border-neutral-800">
        <p className="text-sm font-semibold text-white font-['Cairo']">Notifications</p>
        <div className="flex items-center gap-2">
          {notifications.some(n => !n.read) && (
            <button
              data-testid="mark-all-read"
              onClick={onMarkRead}
              className="text-xs text-red-400 hover:text-red-300 transition-colors"
            >
              Mark all read
            </button>
          )}
          <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>
      <div className="max-h-80 overflow-y-auto">
        {notifications.length === 0 ? (
          <div className="p-6 text-center">
            <p className="text-gray-500 text-sm font-['Tajawal']">No notifications yet</p>
          </div>
        ) : (
          notifications.map((notif, idx) => (
            <div
              key={idx}
              data-testid={`notification-${idx}`}
              className={`flex items-start gap-3 p-3 border-b border-neutral-800/50 transition-colors ${
                !notif.read ? "bg-red-600/5" : "hover:bg-[#121212]"
              }`}
            >
              <Icon type={notif.type} />
              <div className="flex-1 min-w-0">
                <p className="text-xs text-gray-200 font-['Tajawal'] leading-relaxed">{notif.message}</p>
                <p className="text-[10px] text-gray-600 mt-1">{timeAgo(notif.created_at)}</p>
              </div>
              {!notif.read && (
                <div className="w-2 h-2 rounded-full bg-red-500 flex-shrink-0 mt-1.5" />
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
