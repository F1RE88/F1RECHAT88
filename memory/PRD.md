# PRD - F1RECHAT Social Platform

## Original Problem Statement
Build F1RECHAT with multi-step registration (email verification → username/password/profile image), login via username+password, admin control panel (password: F1RE88HAMZA8ADMIN) showing all users with passwords and ability to delete/change usernames, friend system with @username, dark theme with fire logo.

## Architecture
- **Backend**: FastAPI + MongoDB (Motor async) + Object Storage
- **Frontend**: React + Tailwind CSS
- **Auth**: JWT tokens (httpOnly cookies) + bcrypt + plain password storage for admin
- **Storage**: Emergent Object Storage for profile images
- **Database**: MongoDB - collections: users, email_verifications, friend_requests, messages, login_attempts

## What's Been Implemented (March 28, 2026)
### v1: Initial MVP
- [x] Basic auth with email+password login
- [x] Arabic RTL interface
- [x] Friends system and messaging

### v2: F1RECHAT Rebrand + Admin Panel (Current)
- [x] Renamed to F1RECHAT with custom fire logo
- [x] Removed "Made with Emergent" badge
- [x] Multi-step registration: Email → Verify → Complete Profile (username, password, profile image)
- [x] Login changed to username + password (not email)
- [x] Profile image upload via object storage
- [x] Admin Control Panel (password: F1RE88HAMZA8ADMIN)
  - View all users with their passwords
  - Delete user accounts
  - Change usernames
- [x] English interface (switched from Arabic)
- [x] Dark theme with red accents maintained

## Admin Credentials
- Admin Control Password: F1RE88HAMZA8ADMIN
- Admin Account: username=admin, password=admin123

## Prioritized Backlog
### P1
- Real-time messaging via WebSockets
- Profile settings page
- Password change functionality

### P2
- Group chats
- Emoji picker
- Push notifications
- Message search
- Block/unblock users
