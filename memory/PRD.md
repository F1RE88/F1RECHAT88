# PRD - F1RECHAT Social Platform

## Original Problem Statement
Build F1RECHAT social platform with auth, friends, groups, chat, notifications, and real online/offline status.

## Architecture
- **Backend**: FastAPI + MongoDB + Object Storage
- **Frontend**: React + Tailwind CSS
- **Auth**: JWT (httpOnly cookies) + bcrypt
- **Storage**: Emergent Object Storage for profile images

## Implemented Features

### v1-v4: Auth, Friends, Groups, Admin Panel, Chat Background
### v5: Notifications + Online/Offline Status (Current)
- [x] Real online/offline status via heartbeat system (30s heartbeat, 60s timeout)
- [x] Login → online, Logout → offline, Page close → offline (beforeunload)
- [x] Green/gray dots on friend avatars
- [x] "Online"/"Offline" text updates in real-time
- [x] Notification system with types: friend_request, friend_accepted, new_message, group_message
- [x] Bell icon with unread count badge
- [x] Notification dropdown panel with "Mark all read"
- [x] Notifications auto-refresh every 5s
- [x] All 56 backend tests passed (100%)

## Admin Credentials
- Admin Control Password: F1RE88HAMZA8ADMIN
- Admin Account: username=admin, password=admin123

## Backlog
### P1 - WebSocket real-time messaging, Profile settings
### P2 - Emoji picker, Push notifications, File sharing in chat
