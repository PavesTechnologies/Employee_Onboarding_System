# Backend/API_Layer/middleware/db_session_middleware.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from ...DAL.utils.database import set_db_session, remove_db_session
import time


class DBSessionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to manage database session lifecycle per request.
    Ensures session creation before processing and cleanup after.
    """

    async def dispatch(self, request: Request, call_next):
        t_start = time.time()
        print("🟢 DB Middleware - ENTERING")

        db = None
        try:
            # Await the async session creator
            db = await set_db_session()
            # attach to request.state for quick access
            request.state.db = db
            print("🟢 DB Middleware - DB session initialized")

            response = await call_next(request)
            return response

        except SQLAlchemyError as e:
            print(f"🔴 DB Middleware - SQLAlchemyError: {e}")
            # can't call rollback synchronously; check db presence
            if db:
                try:
                    await db.rollback()
                except Exception:
                    pass
            return JSONResponse(
                {"detail": "A database error occurred."}, status_code=500
            )

        except Exception as e:
            print(f"🔴 DB Middleware - Unexpected Error: {e}")
            return JSONResponse({"detail": "Internal server error."}, status_code=500)

        finally:
            # Always remove DB session after request completes
            await remove_db_session()
            t_end = time.time()
            elapsed = (t_end - t_start) * 1000
            print(f"⏱ DB Middleware: {elapsed:.2f}ms")
            print("🟢 DB Middleware - Session removed and EXITING")
