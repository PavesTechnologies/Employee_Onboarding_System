from fastapi import Depends, HTTPException, status, Request
 
def require_roles(*allowed_roles: str):
    def role_checker(request: Request):
        # 1. Safely check if 'user' exists in state
        user = getattr(request.state, "user", None)
       
        # DEBUG: See what is actually reaching the checker
        # print(f"DEBUG: User in State: {user}")
 
        if not user:
            # Return 401 instead of crashing (500)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing authentication token"
            )
 
        # 2. Extract roles (ensure your JWT logic uses the key 'roles')
        # Some JWTs use 'role' (singular). Check your token structure!
        user_roles = user.get("roles", [])
       
        # 3. Case-insensitive comparison
        user_roles_upper = [str(r).upper() for r in user_roles]
        required_upper = [str(r).upper() for r in allowed_roles]
 
        if not any(role in user_roles_upper for role in required_upper):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {allowed_roles}"
            )
           
        return user
    return role_checker
 
