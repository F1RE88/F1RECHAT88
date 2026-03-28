# PRD - F1RECHAT Social Platform

## Original Problem Statement
Build F1RECHAT with multi-step registration (email verification → username/password/profile image), login via username+password, admin control panel (password: F1RE88HAMZA8ADMIN) showing all users with passwords and ability to delete/change usernames, friend system with @username, dark theme with fire logo, chat background customization.

## Architecture
- **Backend**: FastAPI + MongoDB (Motor async) + Object Storage
- **Frontend**: React + Tailwind CSS
- **Auth**: JWT tokens (httpOnly cookies) + bcrypt + plain password storage for admin
- **Storage**: Emergent Object Storage for profile images
- **Database**: MongoDB - collections: users, email_verifications, friend_requests, messages, login_attempts

## What's Been Implemented (March 28, 2026)
### v1: Initial MVP - Arabic RTL social platform
### v2: F1RECHAT Rebrand + Admin Panel
### v3: Bug Fixes + Chat Background (Current)
- [x] Fixed message direction bug (messages were appearing swapped after re-login)
- [x] Root cause: /auth/me returned `_id` while login returned `id` - normalized to `id`
- [x] Added chat background customization (12 background options, saved per user)
- [x] Removed "Made with Emergent" badge
- [x] All tests passing 100%

## Admin Credentials
- Admin Control Password: F1RE88HAMZA8ADMIN
- Admin Account: username=admin, password=admin123

## Test Users
- usera140401 / test123456
- userb140401 / test123456

## Prioritized Backlog
### P1 - Real-time WebSocket messaging, Profile settings page
### P2 - Group chats, Emoji picker, Push notifications, Message search, Block/unblock users
