# from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, Response
from fastapi.openapi.utils import get_openapi
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os
from jinja2 import Environment, FileSystemLoader

from Backend.API_Layer.routes import addtask_routes, docusign_token_generation_route, employee_experience_routes, employee_export_routes, hr_bulk_join_router, hr_onboarding_routes, offer_approval_action_routes, otp_routes, redis_cache_routes, weekly_dashboard_routes
from .API_Layer.routes import (master_routes, offerletter_routes, education_routes, offerresponse_routes, employee_details_routes,
                               identity_routes, employee_upload_routes,analytics_routes,)
from .API_Layer.middleware.jwt_middleware import JWTMiddleware
from fastapi.middleware.cors import CORSMiddleware
from .API_Layer.middleware.audit_middleware import AuditMiddleware
from Backend.API_Layer.routes import token_verification_router
from Backend.API_Layer.routes import offer_acceptance_request_routes
# from Backend.API_Layer.routes import offer_approval_action_routes
from Backend.corn_jobs.joining_reminder import send_joining_date_reminders
from Backend.API_Layer.routes import permanent_employee_details_route
from Backend.API_Layer.routes import departments_routes
from Backend.API_Layer.routes import designation_routes
from Backend.API_Layer.routes import employee_pf_routes
from Backend.API_Layer.routes import employee_bank_routes
from Backend.API_Layer.routes import dashboard_routes, employee_exit_routes, exit_approval_routes, exit_clearance_items_routes, exit_clearance_routes, exit_interview_routes
from datetime import date
from weasyprint import HTML
from Backend.API_Layer.routes import addtask_routes
from Backend.API_Layer.routes import exit_final_settlement_routes
from Backend.API_Layer.routes import exit_documents_routes




# from fastapi_cache.backends.redis import RedisBackend
# import redis.asyncio as redis


# from Backend.API_Layer.routes import hr_bulk_join_router

# import redis.asyncio as redis


# models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Employee Onboarding System API")

app.add_middleware(JWTMiddleware)
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173",
                    "http://localhost:3000",
                    "https://employeeonbordingforms.netlify.app",
                    "https://nonprovidentially-xiphisternal-junior.ngrok-free.dev",
                    "https://api.15.134.36.38.sslip.io",
                    "http://13.202.204.204"],

    # allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
    max_age=3600,
)

# Add Audit Middleware globally
# app.add_middleware(AuditMiddleware)
# Add JWT middleware globally


# Add DB session middleware
# app.add_middleware(DBSessionMiddleware)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Employee Onboarding System",
        version="0.1.0",
        description="Secure API with JWT & RBAC",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if method in ["get", "post", "put", "delete"]:
                openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.include_router(offerletter_routes.router, prefix="/offerletters", tags=["Offer Letters"])
app.include_router(master_routes.router, prefix="/masters", tags=["Master (Countries, Education Levels, Contacts)"])
app.include_router(education_routes.router, prefix="/education", tags=["Education Documents"])
app.include_router(offerresponse_routes.router, prefix="/offerresponse", tags=["Offer Response"])
app.include_router(employee_details_routes.router, prefix="/employee-details", tags=["Employee Details"])
app.include_router(identity_routes.router, prefix="/identity", tags=["Identity Details"])
app.include_router(employee_experience_routes.router, prefix="/experience", tags=["Employee Experience"])
app.include_router(employee_pf_routes.router, prefix="/pf", tags=["Employee PF"])
app.include_router(employee_bank_routes.router, prefix="/bank", tags=["Employee Bank"])
app.include_router(employee_upload_routes.router, prefix="/employee-upload", tags=["Employee Uploads"])
app.include_router(otp_routes.router, prefix="/otp", tags=["Otp Verification"])
app.include_router(token_verification_router.router, prefix="/token-verification", tags=["Token Verification"])
app.include_router(offer_acceptance_request_routes.router, prefix="/offer-approval-requests", tags=["Offer Approval Requests"])
app.include_router(offer_approval_action_routes.router, prefix="/offer-approval", tags=["Offer Approval"])
app.include_router(hr_onboarding_routes.router, prefix="/hr", tags=["HR Onboarding"])
app.include_router(docusign_token_generation_route.router, prefix="/docusign", tags=["DocuSign Token Generation"])
app.include_router(redis_cache_routes.router, prefix="/cache", tags=["Redis Cache"])
app.include_router(hr_bulk_join_router.router, prefix="/hr", tags=["HR Bulk Join"])
app.include_router(permanent_employee_details_route.router, prefix="/permanent-employee", tags=["Permanent Employees"])
app.include_router(departments_routes.router)
app.include_router(designation_routes.router)

app.include_router(analytics_routes.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(dashboard_routes.router)
app.include_router(employee_exit_routes.router)
app.include_router(exit_interview_routes.router)
app.include_router(exit_approval_routes.router)
app.include_router(weekly_dashboard_routes.router, prefix="/weekly-dashboard", tags=["Dashboard"])
app.include_router(addtask_routes.router, prefix="/api")
app.include_router(exit_clearance_items_routes.router)
app.include_router(exit_clearance_routes.router)
app.include_router(exit_final_settlement_routes.router)
app.include_router(exit_documents_routes.router)



app.include_router(employee_export_routes.router, prefix="/api", tags=["Employee Export"])


# scheduler = AsyncIOScheduler()

# # Don't remove the comments below - needed for reference
# @app.on_event("startup")
# async def start_scheduler():

#     scheduler.add_job(
#         send_joining_date_reminders,   # ✅ async directly
#         "cron",
#         second="*/10",  # Every 10 minutes
#         # hour=9,          # 11 PM
#         # minute=0, 
#         id="joining_reminder",
#         replace_existing=True,
#         max_instances=1,
#         coalesce=True,
#     )
#     scheduler.start()

# @app.on_event("shutdown")
# async def stop_scheduler():
#     await scheduler.shutdown()



# Base directory of Backend folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Templates directory
template_dir = os.path.join(BASE_DIR, "templates")

# Initialize Jinja environment
env = Environment(loader=FileSystemLoader(template_dir))


@app.get("/generate-offer")
def generate_offer():

    # Load HTML template
    template = env.get_template("offer_letter.html")

    # Absolute path for logo
    logo_path = os.path.join(BASE_DIR, "static", "images", "paves_logo.jpg")

    # Data for template
    data = {
        "logo_path": logo_path,
        "current_date": date.today(),
        "first_name": "Ajay",
        "last_name": "Kumar",
        "mail": "ajay@gmail.com",
        "country_code": "91",
        "contact_number": "9876543210",
        "designation": "Software Engineer",
        "total_ctc": "12,00,000",
        "compensation_components": [
            {"name": "Basic Salary", "type": "Fixed", "frequency": "Monthly", "amount": "50,000"},
            {"name": "HRA", "type": "Fixed", "frequency": "Monthly", "amount": "20,000"},
            {"name": "Bonus", "type": "Variable", "frequency": "Yearly", "amount": "2,00,000"}
        ]
    }

    # Render HTML with data
    html = template.render(data)

    # Convert HTML to PDF
    pdf = HTML(string=html, base_url=BASE_DIR).write_pdf()

    # Return PDF response
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "inline; filename=offer_letter.pdf"
        }
    )