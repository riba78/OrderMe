# OrderMe Troubleshooting Guide

This document contains common issues encountered in the OrderMe application and their solutions.

## Authentication Issues

### 1. "Error fetching users" in Admin Dashboard

**Problem**: Admin users unable to access the Users table at `/admin/users`, receiving a "Network error" or "Error fetching users" message.

**Symptoms**:
- Network error when accessing `/admin/users`
- Admin dashboard loads but user list is empty
- Console shows 401 Unauthorized errors

**Cause**:
The issue was related to token handling and axios configuration conflicts. Multiple axios instances were created with different configurations, leading to authentication failures.

**Solution**:
1. Consolidated axios configuration to use a single instance from `frontend/src/utils/axios.js`
2. Removed duplicate axios configuration from Vuex store
3. Ensured proper token handling in the auth utilities

**Prevention**:
- Always use the configured axios instance from `@/utils/axios`
- Don't create multiple axios configurations
- Verify token storage and retrieval in localStorage
- Check backend logs for token validation issues

### 2. Token Validation Failures

**Problem**: JWT tokens not being properly validated by the backend.

**Solution**:
1. Ensure `SECRET_KEY` environment variable is properly set
2. Verify token format in Authorization header
3. Check token expiration and payload structure

## Environment Setup

### Required Environment Variables

```bash
# Backend (.env)
SECRET_KEY=your-secret-key
ADMIN_EMAIL=admin@orderme.com
ADMIN_PASSWORD=admin123
DB_URL=mysql://user:password@localhost/orderme

# Frontend (.env)
VUE_APP_API_URL=http://localhost:5000
```

## Common Commands

### Start Backend Server
```bash
cd backend
python3 app.py
```

### Start Frontend Development Server
```bash
cd frontend
npm run serve
```

### Clear Browser Cache and Storage
1. Open Developer Tools (⌘⌥I on Mac)
2. Go to Application tab
3. Clear Storage (including localStorage)
4. Hard refresh (⌘⇧R on Mac)

## Debugging Tips

1. Check backend logs for authentication and request details
2. Verify token presence in localStorage
3. Monitor network requests in browser DevTools
4. Ensure CORS configuration matches frontend origin

## Support

For additional support or to report new issues:
1. Check existing issues in this guide
2. Review application logs
3. Contact the development team with:
   - Steps to reproduce
   - Error messages
   - Environment details
   - Relevant logs 