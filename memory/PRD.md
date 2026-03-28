# PRD - الفراغ (Social Platform)

## Original Problem Statement
Build a social platform with login/register authentication requiring username, email, password. Users must enter password every time they visit. Friends system using @username to add friends. Dark theme with Arabic RTL interface.

## Architecture
- **Backend**: FastAPI + MongoDB (Motor async driver)
- **Frontend**: React + Tailwind CSS + Shadcn UI
- **Auth**: JWT tokens (httpOnly cookies) + bcrypt password hashing
- **Database**: MongoDB with collections: users, friend_requests, messages, login_attempts

## User Personas
- Arabic-speaking users looking for a private messaging platform
- Users who want a secure, dark-themed social experience

## Core Requirements (Static)
1. Authentication (login/register) with password required every visit
2. Friends system with @username search and friend requests
3. Real-time messaging between friends
4. Dark theme with RTL Arabic interface
5. Brute force protection on login

## What's Been Implemented (March 28, 2026)
- [x] Full JWT authentication (register, login, logout, refresh, me)
- [x] Password hashing with bcrypt
- [x] Brute force login protection (5 attempts = 15 min lockout)
- [x] Admin user seeding
- [x] Friend system: search (@username), send request, accept/reject
- [x] Messaging between friends
- [x] Dark theme UI (#050505 background, #DC2626 red accents)
- [x] Arabic RTL layout with Cairo + Tajawal fonts
- [x] Split layout: Chat area (left) + Friends sidebar (right)
- [x] Login page with "Don't have account?" toggle
- [x] Ghost icon branding (الفراغ)
- [x] Mobile responsive with sidebar toggle
- [x] Auto-refresh for friends list, requests, and messages (5s polling)

## Prioritized Backlog
### P0 (Critical)
- All P0 features implemented

### P1 (Important)
- Real-time messaging via WebSockets (currently polling)
- Profile page with user settings
- Password change functionality
- Message read receipts

### P2 (Nice to have)
- Profile pictures / avatars
- Group chats
- Emoji picker integration
- Push notifications
- Message search
- Block/unblock users
- Online/offline status (real-time)

## Next Tasks
1. Implement WebSocket for real-time messaging
2. Add profile page with user settings
3. Implement message read receipts
4. Add emoji picker to chat input
