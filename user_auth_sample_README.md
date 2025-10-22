# Sample User Authentication Database

## Overview
This is a sample user authentication database (`user_auth_sample.db`) for development and testing purposes. The actual production database (`user_auth.db`) is excluded from the repository for security reasons.

## Sample Data
The sample database includes:
- **Demo User**: A test user account for development purposes
- **Sample Tables**: Complete table structure matching the production database

## Sample User Credentials
- **Email**: demo@un.org
- **Name**: Demo User
- **Title**: Research Analyst
- **Office**: OSAA
- **Status**: Approved

## Database Schema

### Users Table
- `id`: Primary key
- `email`: Unique email address
- `password_hash`: Hashed password (demo_hash for sample)
- `full_name`: Full name of the user
- `title`: Job title
- `office`: Office/department
- `purpose`: Purpose of access
- `status`: Account status (pending, approved, rejected)
- `created_at`: Account creation timestamp
- `approved_at`: Approval timestamp
- `last_login`: Last login timestamp
- `login_count`: Number of logins

### Usage Logs Table
- `id`: Primary key
- `user_id`: Foreign key to users table
- `action`: Action performed
- `details`: Additional details
- `timestamp`: Action timestamp

## Security Notice
⚠️ **Important**: This is a sample database for development only. In production:
1. Use strong, unique passwords
2. Implement proper password hashing
3. Store sensitive data securely
4. Use environment variables for database connections
5. Implement proper access controls

## Setup Instructions
1. Copy `user_auth_sample.db` to `user_auth.db` for local development
2. Update the database connection in your application
3. Create additional users as needed for testing
4. Never commit the production database to version control

## Production Database
The production database (`user_auth.db`) contains real user data and is excluded from the repository for security reasons. Always ensure proper security measures are in place when handling user authentication data.
