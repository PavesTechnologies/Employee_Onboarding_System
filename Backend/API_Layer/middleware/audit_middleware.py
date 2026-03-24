# Backend/API_Layer/middleware/audit_middleware.py
from importlib.resources import path
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, StreamingResponse
from ...DAL.utils.dependencies import get_db
from ...DAL.dao.auditlogs_dao import AuditTrails
from ..utils.audit_utils import AuditUtils
import json
import uuid
from typing import Optional
import io
import time

class AuditMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        

        # Endpoints that should not be audited
        self.open_endpoints = [
            "/docs", "/openapi.json",
            "/redoc","/login", "/health", "/masters/country, /employee-details", "/employee-upload, "
            
        ]
        self.entity_mappings = AuditUtils().entity_mappings
        


    async def dispatch(self, request: Request, call_next):

        # Allow preflight OPTIONS requests to pass through
        if request.method == "OPTIONS":
            return await call_next(request)
        
        print("Audit Middleware Entering...")
        start = time.perf_counter()
        # middleware code
        print("Audit middleware:", time.perf_counter() - start)
        path = request.url.path
        method = request.method
        
         # 🔕 Skip OTP routes
        if path.startswith("/otp"):
            return await call_next(request)
        if path.startswith("/token-verification"):
            return await call_next(request)
        
        if path.startswith("/offer-approval-requests"):
            return await call_next(request)
        
        if path.startswith("/offer-approval"):
            return await call_next(request)
        
        if path.startswith("/docusign"):
                return await call_next(request)
        
        if path.startswith("/offerletters"):
                return await call_next(request)
        
        if path.startswith("/hr"):
                return await call_next(request)
        
        # Skip audit for certain methods and endpoints
        # print("Path:", path, "Method:", method)
        # for p in self.open_endpoints:
        #     print("Open Endpoint:", p)
            
        if method in ["GET", "OPTIONS"] or any(path.startswith(p) for p in self.open_endpoints):
            print(f"Skipping Audit: path={path}, method={method}")
            return await call_next(request)

        # Extract user info
        payload = getattr(request.state, "user", None)
        user_id = payload.get("user_id") if payload else "anonymous"
        print("User ID from middleware:", user_id)

        # Get request body
        try:
            body = await request.body()
            req_body = json.loads(body) if body else {}
            # Reset body for downstream consumers
            request._body = body
        except:
            req_body = {}

        # Extract entity information
        entity_name, entity_id = AuditUtils().extract_entity_info(path, req_body, method)
        operation = AuditUtils().get_operation_type(method)

        ip_address_from_request = AuditUtils()._get_ip_address(request = request)
        print("Ip address", ip_address_from_request)

        # Get IP address (handle proxies)
        ip_address = (
            request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or
            request.headers.get("X-Real-IP") or
            request.client.host if request.client else "unknown"
        )
        
        host = request.headers.get("host", "unknown")

        # Fetch old data BEFORE processing request (for UPDATE/DELETE)
        old_data = None
        print(f"Entity Name: {entity_name}, Entity_ID: {entity_id}, Operation: {operation}")
        if operation in ["UPDATE", "DELETE"] and entity_id:
            async for db in get_db():
                old_data = await AuditUtils().get_data(db, entity_name, entity_id)
                break
        print("old data from middleware", old_data)
        # Process the request
        response = await call_next(request)

        # Capture response body without consuming it
        new_data = None
        response_body = b""
        
        async for chunk in response.body_iterator:
            response_body += chunk
        
        try:
            new_data = json.loads(response_body.decode())
        except:
            new_data = None

        print("new data from response", new_data)

        if 200 <= response.status_code < 300:

            # For CREATE operations, fetch the newly created data if we have an ID in response
            new_entity_data = None

            if new_data and operation == "CREATE":
                
                # Step 1: Get ID column name from mapping
                id_field = self.entity_mappings.get(entity_name, {}).get("id_field")
                
                # Step 2: Extract actual ID value from response
                new_entity_id = new_data.get(id_field)
                
                print("ID field:", id_field)
                print("New entity id:", new_entity_id)

                if new_entity_id:
                    async for db in get_db():
                        new_entity_data = await AuditUtils().get_data(db, entity_name, new_entity_id)
                        break

            # For UPDATE
            if operation in ["UPDATE"] and entity_id:
                async for db in get_db():
                    new_entity_data = await AuditUtils().get_data(db, entity_name, entity_id)
                    break
                # Identify which columns changed
                changed_fields = {
                    key for key in old_data.keys()
                    if key in new_entity_data and old_data[key] != new_entity_data[key]
                }

                old_data = {key: old_data[key] for key in changed_fields}
                new_entity_data = {key: new_entity_data[key] for key in changed_fields}
            print("new entity data after query db", new_entity_data)
            # Create new response with captured body
            response = Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
            table_name = self.entity_mappings[entity_name]["table"]
            # my_dict = {
            #     "entity_name": table_name,
            #     "entity_id": entity_id,
            #     "operation": operation,
            #     "user_id": user_id,
            #     "old_data": old_data,
            #     "new_data": new_data,
            #     "ip address": ip_address,
            #     'host': host,
            #     'new_entity_data': new_entity_data
            # }
            # print("Audit Logs:", my_dict)

            # Log audit trail (only if response is successful)
            
            try:
                async for db in get_db():
                    audit = AuditTrails(db)
                    
                    
                    await audit.create_audit_log(
                        entity_name=table_name,
                        entity_id=str(entity_id or "N/A"),
                        operation=operation,
                        user_id=str(user_id),
                        old_data=old_data,
                        new_data=new_entity_data,
                        ip_address=ip_address,
                        host=host,
                        endpoint=path
                    )
                    break
            except Exception as e:
                print(f"Audit logging failed: {e}")
                # Don't fail the request if audit logging fails

            return response
        else:
            # For non-success responses, just return as is
            return Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
        