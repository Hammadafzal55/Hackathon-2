---
name: debugging-skill
description: Debug all issues, errors, and bugs related to authentication, frontend, and backend. Use to troubleshoot and fix web applications efficiently.
---

# Debugging Skill

## Instructions

### 1. Identify the Issue
- Reproduce the bug consistently  
- Check browser console for frontend errors  
- Inspect backend logs for server-side errors  
- Verify authentication flows and credentials  

### 2. Frontend Debugging
- Inspect DOM elements and CSS styles  
- Check network requests for failed API calls  
- Debug JavaScript or TypeScript errors  
- Test on multiple browsers and devices  

### 3. Backend Debugging
- Examine server logs and error stack traces  
- Verify database queries and connections  
- Check API routes and middleware  
- Ensure proper environment variables are set  

### 4. Authentication Debugging
- Validate login/signup flows  
- Test token generation and verification  
- Check session and cookie handling  
- Debug OAuth or third-party auth integrations  

### 5. Fix and Test
- Apply code fixes step-by-step  
- Retest all affected functionalities  
- Write automated tests if applicable  
- Confirm bug is fully resolved in all environments  

## Best Practices
- Start with reproducible steps before changing code  
- Debug one issue at a time to avoid confusion  
- Keep logs detailed but readable  
- Use consistent tools for frontend (browser dev tools) and backend (IDE/debugger)  
- Maintain a checklist for common authentication bugs  

## Example Debug Workflow
```bash
# Reproduce the bug
npm run dev

# Check frontend errors
open browser console

# Inspect network requests
# Use Postman or browser network tab

# Check backend logs
tail -f server/logs/error.log

# Apply fix and retest
git checkout -b bugfix/auth-issue
# edit code
npm run test
