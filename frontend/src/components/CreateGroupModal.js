import React, { useState } from "react";
import { X, Users, Check } from "lucide-react";

export default function CreateGroupModal({ friends, onClose, onCreate }) {
  const [groupName, setGroupName] = useState("");
  const [selectedMembers, setSelectedMembers] = useState([]);
  const [error, setError] = useState("");
  const [creating, setCreating] = useState(false);

  const toggleMember = (friendId) => {
    setSelectedMembers(prev =>
      prev.includes(friendId)
        ? prev.filter(id => id !== friendId)
        : [...prev, friendId]
    );
  };

  const handleCreate = async () => {
    if (!groupName.trim()) {
      setError("Group name is required");
      return;
    }
    if (selectedMembers.length === 0) {
      setError("Select at least one friend");
      return;
    }
    setError("");
    setCreating(true);
    const result = await onCreate(groupName.trim(), selectedMembers);
    if (!result.success) {
      setError(result.error || "Failed to create group");
      setCreating(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4" data-testid="create-group-overlay">
      <div className="bg-[#0A0A0A] border border-neutral-800 rounded-2xl w-full max-w-md max-h-[80vh] flex flex-col shadow-2xl animate-fade-in" data-testid="create-group-modal">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-neutral-800">
          <div className="flex items-center gap-2">
            <Users className="w-5 h-5 text-red-500" />
            <h2 className="text-base font-bold text-white font-['Cairo']">Create Group</h2>
          </div>
          <button onClick={onClose} data-testid="close-create-group" className="text-gray-400 hover:text-white transition-colors p-1 hover:bg-neutral-800 rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Group Name */}
          <div>
            <label className="block text-sm text-gray-400 mb-1.5 font-['Tajawal']">Group Name</label>
            <input
              data-testid="group-name-input"
              type="text"
              value={groupName}
              onChange={(e) => setGroupName(e.target.value)}
              placeholder="Enter group name..."
              className="w-full bg-[#121212] border border-neutral-800 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-red-600 focus:ring-1 focus:ring-red-600 transition-colors placeholder-gray-600 font-['Tajawal']"
              maxLength={50}
            />
          </div>

          {/* Select Friends */}
          <div>
            <label className="block text-sm text-gray-400 mb-1.5 font-['Tajawal']">
              Select Friends ({selectedMembers.length} selected)
            </label>
            {friends.length === 0 ? (
              <p className="text-gray-600 text-xs font-['Tajawal']">You need friends to create a group. Add friends first!</p>
            ) : (
              <div className="space-y-1 max-h-60 overflow-y-auto">
                {friends.map((friend) => {
                  const isSelected = selectedMembers.includes(friend.id);
                  return (
                    <button
                      key={friend.id}
                      data-testid={`select-member-${friend.username}`}
                      onClick={() => toggleMember(friend.id)}
                      className={`w-full flex items-center gap-3 p-2.5 rounded-lg transition-colors text-left ${
                        isSelected
                          ? "bg-red-600/10 border border-red-600/30"
                          : "bg-[#121212] border border-neutral-800 hover:border-neutral-700"
                      }`}
                    >
                      <div className="w-8 h-8 rounded-full bg-neutral-800 flex items-center justify-center text-sm font-semibold text-gray-200 flex-shrink-0">
                        {friend.username[0].toUpperCase()}
                      </div>
                      <span className="text-sm text-gray-200 flex-1">@{friend.username}</span>
                      {isSelected && (
                        <div className="w-5 h-5 rounded-full bg-red-600 flex items-center justify-center">
                          <Check className="w-3 h-3 text-white" />
                        </div>
                      )}
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          {error && (
            <div className="text-red-400 text-sm bg-red-900/20 border border-red-800/30 rounded-lg p-3" data-testid="create-group-error">
              {error}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-neutral-800">
          <button
            data-testid="create-group-button"
            onClick={handleCreate}
            disabled={creating || friends.length === 0}
            className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-2.5 px-4 rounded-lg transition-all flex justify-center items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed font-['Cairo']"
          >
            {creating ? (
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <>Create Group</>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
