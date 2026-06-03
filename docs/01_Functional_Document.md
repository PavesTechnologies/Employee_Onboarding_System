# Functional Document — Employee Onboarding & Exit Management System

**Document Version:** 1.0
**Date:** 2026-06-03
**Prepared For:** Paves Technologies
**System:** Employee Onboarding & Exit Management System (EOS / EMS)
**Technology Platform:** FastAPI (Python 3) | MySQL (SQLAlchemy Async) | Redis | AWS S3 | DocuSign | PandaDoc | WeasyPrint | Docker

---

## 1. Project Overview & Objective

### 1.1 Background

Paves Technologies operates a unified Human Capital lifecycle platform called the **Employee Onboarding & Exit Management System (EOS / EMS)**. The platform digitises every step of the employee lifecycle from the moment a candidate is identified for an offer, through joining and confirmation, up to the eventual exit and final settlement of dues.

The system is exposed as a secure, JWT-authenticated REST API (`/ems` prefix) and is the backend for a separate React/Vite frontend that consumes the documented OpenAPI contract at `/ems/openapi.json`.

### 1.2 Objective

The primary objective of EOS/EMS is to provide:

1. **A single source of truth** for all candidate, employee, and ex-employee records.
2. **End-to-end automation** of repetitive HR tasks — offer letter generation, multi-approver signoff, joining letter dispatch, document verification, exit clearance, full and final settlement, and post-exit document delivery.
3. **Integration with industry-standard e-sign and document storage providers** (DocuSign primary, PandaDoc legacy fallback, AWS S3 for binaries).
4. **Role-based, auditable workflows** that satisfy compliance, internal-audit, and data-privacy requirements (every CREATE / UPDATE / DELETE is logged in `audit_trail`).
5. **Operational dashboards and analytics** for HR leadership to monitor pipeline velocity, demographic distribution, joining adherence, and exit pipeline state.

### 1.3 Key Business Goals

| # | Goal | KPI Impacted |
|---|------|-------------|
| 1 | Reduce offer-to-acceptance cycle time | Time-to-Hire |
| 2 | Eliminate paper-based document collection | Document Compliance % |
| 3 | Enforce multi-level approval for compensation | Cost-Governance |
| 4 | Standardise exit clearance across departments | Exit TAT |
| 5 | Provide demographics analytics in real time | Diversity Metrics |
| 6 | Ensure auditability of every data mutation | Compliance Audit Pass Rate |

---

## 2. System Scope

### 2.1 In Scope

The system covers the **complete pre-hire to post-exit lifecycle**:

**A. Pre-Hire / Offer Phase**
- Offer letter creation (single and bulk via Excel)
- Compensation component management
- Internal approval workflow (HR → Reporting Manager / Admin)
- DocuSign envelope generation and tracking
- Candidate offer acceptance / rejection capture

**B. Onboarding Phase**
- Secure tokenised onboarding link delivery to candidate
- OTP-based email verification
- Candidate self-service portal for capturing personal, address, identity, education, experience, bank, PF, and social-link details
- Document upload to AWS S3
- HR document-level and profile-level verification
- Joining letter generation, bulk joining, and rescheduling
- Joining-date status engine (Joining → Joining Pending → Rescheduled → Completed)

**C. Active Employee Phase**
- Permanent employee creation (single, bulk via Excel with dropdowns)
- Departments & Designations master data
- Reporting manager hierarchy / Organisation Tree
- Employee profile management (About Me, Social Links)
- Task management (onboarding/exit/IT/Finance/Admin tasks)

**D. Exit Phase**
- Resignation / termination / contract-end / absconding / retirement initiation
- Two-step approval (Manager → HR)
- Multi-department clearance (Manager, IT, HR, Finance, Admin) with line items
- Exit interview capture
- Final settlement computation and approval
- Settlement payment marking
- Exit document generation (Relieving Letter, Experience Letter, F&F, NOC, Resignation Letter, Termination Letter)

**E. Cross-Cutting**
- JWT authentication middleware
- RBAC enforcement (HR, ADMIN, REPORTING_MANAGER, GENERAL)
- Full audit logging
- Email notifications (SMTP)
- PDF generation (WeasyPrint + Jinja2 templates)
- Redis cache layer
- Dashboard summaries (operational & weekly)
- Analytics aggregation
- Integration with external RMS (Resource Management System) and UMS (User Management System) for admin user resolution

### 2.2 Out of Scope

- Payroll computation beyond F&F settlement
- Time and attendance tracking
- Leave-management system (consumed externally; leave-encashment value is taken as input)
- Performance appraisal / KPI management
- Learning Management System (LMS)
- Internal recruitment / ATS (offers are created from already-selected candidates)
- Mobile native application (the API is consumed by a web SPA)

### 2.3 System Boundaries (Integration Points)

```
                +-----------+
   Candidate -->|  EOS API  |<-- HR / Admin (web SPA)
                |  (/ems)   |
                +-----+-----+
                      |
   +---------+--------+--------+----------+----------+
   |         |        |        |          |          |
 MySQL    AWS S3   DocuSign  PandaDoc  SMTP        Redis
(SQLAlc.) (files) (e-sign)  (legacy)  (email)    (cache)
                                                       
 External : UMS  (admin users list), RMS (resources), CDC network (docker)
```

---

## 3. User Roles & Permissions Matrix

### 3.1 Defined Roles

The codebase enforces roles via the `require_roles(*allowed_roles)` dependency in `Backend/API_Layer/utils/role_based.py`. Roles are read from the JWT payload key `roles` (list, case-insensitive comparison).

| Role Code in JWT | Business Role | Description |
|-------------------|---------------|-------------|
| `ADMIN` / `Admin` | Super Admin | Full administrative access across all modules, including master data and approvals. |
| `HR` | HR Admin / HR Manager | Owns offer creation, onboarding verification, joining, exit lifecycle. (The code does not currently distinguish HR Admin from HR Manager — both map to `HR`.) |
| `REPORTING_MANAGER` | Reporting Manager / Manager | Can view candidate offers in their pipeline, view employee documents, approve exit at Manager step, and act as DocuSign first-signer (CC). |
| `GENERAL` | Employee | Authenticated employee — can view documents, submit exit interview, raise exit, etc. |
| (No role) | Candidate | Token-based access (onboarding link token, OTP). No JWT role — gated by `OnboardingLinks.token_hash` + email OTP. |

> **Note on role naming**: the middleware allowlists certain unauthenticated public endpoints (`open_endpoints`) for the candidate journey (OTP, token verification, candidate submit, offer response webhook).

### 3.2 Permissions Matrix

Legend: **R** = Read, **W** = Write/Create/Update, **A** = Approve / Sign-off, **D** = Delete, **—** = No access

| Module | Super Admin (ADMIN) | HR | Reporting Manager | Employee (GENERAL) | Candidate (token) |
|---|---|---|---|---|---|
| **Offer Letter Mgmt** | R/W/D | R/W/D | R (own pipeline) | — | R (own offer, via token) |
| **Bulk Offer Upload (Excel)** | R/W | R/W | — | — | — |
| **Offer Approval Request (create)** | R/W | R/W | — | — | — |
| **Offer Approval Action (approve/reject/hold)** | R/W/A | — | R/W/A (when assigned) | — | — |
| **Reassign Approver** | R/W | R/W | — | — | — |
| **DocuSign Send / Preview** | R/W | R/W | R (own as CC) | — | R (own envelope) |
| **Bulk Join (joining letter)** | R/W | R/W | — | — | — |
| **Reassign Joining Date** | R/W | R/W | — | — | — |
| **Candidate Onboarding Submit** | — | — | — | — | W |
| **HR Onboarding Verification (profile)** | R/W/A | R/W/A | — | — | — |
| **HR Document Verification (per doc)** | R/W/A | R/W/A | — | — | — |
| **View Onboarding Documents** | R | R | R | R | — |
| **Personal / Address / Identity / Education / Experience / Bank / PF** | R/W/D | R/W/D | R | R (own) | R/W (own, token-gated) |
| **Permanent Employee (direct create / bulk upload)** | R/W/D | R/W/D | R | R (own) | — |
| **Departments Master** | R/W/D | R/W/D | R | R | — |
| **Designations Master** | R/W/D | R/W/D | R | R | — |
| **Country / Education / Identity / Contact Master** | R/W/D | R/W/D | R | R | — |
| **Organisation Tree** | R | R | R | R | — |
| **Employee Exit (initiate)** | R/W | R/W | R/W | R/W (own resignation) | — |
| **Manager Exit Approval** | A | — | A | — | — |
| **HR Exit Approval** | A | A | — | — | — |
| **Exit Clearance — Manager dept** | — | — | A | — | — |
| **Exit Clearance — HR dept** | A | A | — | — | — |
| **Exit Clearance — IT / Finance / Admin** | A | — | — | A (if dept assigned) | — |
| **Exit Clearance Items (line-item)** | R/W/A | R/W/A | R/W/A | R/W/A (own dept) | — |
| **Exit Interview** | R | R | R | W (own) | — |
| **Exit Final Settlement (create)** | R/W | R/W | — | R (own) | — |
| **Exit F&F (Approve)** | A | A | — | — | — |
| **Exit F&F (Mark Paid)** | A | A | — | — | — |
| **Exit Documents (generate / view / download)** | R/W | R/W | R | R (own) | — |
| **Dashboard — Onboarding Summary** | R | R | R | — | — |
| **Dashboard — Celebrations** | R | R | R | R | — |
| **Weekly Dashboard** | R | R | R | — | — |
| **Analytics (demographics / dept stats)** | R | R | R | — | — |
| **Tasks (Onboarding / Exit / IT / Finance / Admin)** | R/W/D | R/W/D | R/W | R (own) | — |
| **Audit Logs** | R | — | — | — | — |
| **Redis Cache control** | R/W/D | R/W/D | — | — | — |
| **Email Triggers (system)** | system | system | system | system | system |

---

## 4. Module Descriptions

### 4.1 Offer Letter Management

**Purpose:** To capture all candidate-offer details and emit a structured offer letter as a PDF / DocuSign envelope, becoming the seed record for every downstream object (onboarding, employee, exit).

**Entity:** `offer_letter_details` (model `OfferLetterDetails`) — keyed by `user_uuid` (UUIDv7).

**Key Features:**

1. **Single Offer Creation** — `POST /ems/offerletters/create` (HR only). Validates name, email, country code, phone, designation, currency; enforces uniqueness on email; assigns `user_uuid`; persists compensation components (`offer_compensation` table).
2. **Bulk Offer Creation via Excel** — `POST /ems/offerletters/bulk_create`. Accepts `.xlsx / .xls / .csv`; normalises column headers using `_COLUMN_ALIASES`; runs full validation row by row; collects `successful_offers`, `failed_offers`, `skipped_rows`; commits in a single transaction.
3. **List / Read** — `GET /ems/offerletters/`, `GET /ems/offerletters/offer/{user_uuid}`, `GET /ems/offerletters/user_id/details` (creator's pipeline).
4. **Update** — `PUT /ems/offerletters/{user_uuid}` (HR only). Implements "delete-and-re-insert" pattern for compensation components to keep the child table consistent.
5. **Delete** — `DELETE /ems/offerletters/delete/{user_uuid}` (HR only). See business rules below.
6. **PDF Preview** — `GET /ems/offerletters/{user_uuid}/generate-preview` (HR / REPORTING_MANAGER). Uses WeasyPrint + Jinja2 template (`templates/offer_letter.html`) to render a fresh PDF (no caching — to reflect latest data).
7. **DocuSign Preview** — `GET /ems/offerletters/{user_uuid}/docusign-preview` returns a DocuSign recipient view URL for either the employee or a manager (`?signer_email=`).
8. **DocuSign Final Preview** — `GET /ems/offerletters/{user_uuid}/final-preview` streams the signed document PDF directly from DocuSign.

**Status Lifecycle (enum on `offer_letter_details.status`):**

`Created` → `Offered` → (`Accepted` | `Rejected` | `Expired`) → `Submitted` → `Verified` → `Joining` → (`Joining Pending` | `Rescheduled`) → `Completed`

**Business Rules:**

- Email must be globally unique.
- `total_ctc`, `compensation_components`, `employee_type`, `currency` are mandatory.
- The creator (`created_by`) is auto-stamped from JWT `employee_id`.
- `cc_emails` is stored CSV; helper `_cc_emails_to_db` normalises list/str input.
- An offer cannot be deleted if an `offer_approval_request` exists. It can only be deleted if `status` is `Rejected` OR `Created` (i.e., not yet sent for approval, or already rejected).

**Validations:**

- `validate_name`, `validate_email`, `validate_country`, `validate_phone_number`, `validate_designation`, `validate_currency` from `Backend/Business_Layer/utils/validation_utils.py`.
- Excel batch validation: required columns set = `{first_name, last_name, mail, country_code, contact_number, designation, employee_type, total_ctc, currency}`. Duplicate emails within the same batch are flagged.
- Compensation components inside Excel can be supplied as JSON in the `compensation_components` column.

**Workflows:**

1. HR creates offer → status `Created`.
2. HR triggers Approval Request → goes to assigned approver.
3. Once `APPROVED`, HR triggers bulk send via DocuSign → status `Offered`.
4. Candidate signs → webhook updates status to `Accepted`; secure onboarding token emailed.
5. Candidate completes onboarding → status `Submitted`.
6. HR verifies → status `Verified`.
7. HR sends joining letter → status `Joining` (or `Joining Pending` if past date, or `Rescheduled` if changed).
8. Employee joins → HR/Bulk Join cron eventually marks `Completed`.

---

### 4.2 Offer Approval Workflow

**Purpose:** Enforce internal sign-off (typically Reporting Manager or Admin) before a financial offer is dispatched to the candidate.

**Entities:**
- `offer_approval_request` (one per offer, model `OfferApprovalRequest`) — fields: `user_uuid`, `request_by`, `action_taker_id`, `request_time`.
- `offer_approval_action` (zero or more per request, model `OfferApprovalAction`) — fields: `request_id`, `action ∈ {Pending, APPROVED, REJECTED, ON_HOLD}`, `comment`, `action_time`.

**Key Features:**

1. **Bulk Create Approval Requests** (`offer_approval_service.OfferApprovalRequestService.create_offer_approval_requests`) — accepts a list, blocks if a request already exists for that `user_uuid`.
2. **Bulk Update Approval Requests** — change `action_taker_id` (reassign), tracked against current user.
3. **Bulk Delete Approval Requests** — only if no terminal action exists.
4. **Take Action** (`OfferApprovalActionService.create_offer_actions`) — validates: only the assigned `action_taker_id` may act; action must be one of `APPROVED / REJECTED / ON_HOLD`; cannot double-act on the same request.
5. **Update Existing Action** — only when offer status is still `Created` and an action row exists.
6. **Reassign Approver** (`reassign_offer_approval_action`) — cannot reassign if any historical action is `APPROVED`; cannot reassign to the same user.
7. **List My Pending Actions** (`get_admin_actions`) — pulls all requests where current user is the approver; enriches with requester name from UMS (`fetch_admin_users_reformed`).
8. **List All Statuses for a User / Globally** — combines latest action with PENDING fallback message.

**Business Rules:**

- Exactly one approval request per offer.
- Only the assigned approver may APPROVE/REJECT/HOLD.
- A request is terminal once any action exists; updates use a separate "update_action" path.
- Once any action is APPROVED, reassignment is permanently blocked.

**State Machine (Approval Action):**

```
        (no request)
              |
         create request
              v
          PENDING ----(reassign approver, only if not APPROVED)
           |  |  \
       APPROVED REJECTED ON_HOLD
                          |
                   (can be updated to APPROVED/REJECTED
                    while offer.status == 'Created')
```

---

### 4.3 Candidate Portal & Offer Response

**Purpose:** Public-facing (candidate-side) endpoints to capture acceptance and onboarding submission.

**Key Features:**

1. **PandaDoc / DocuSign Webhook Handler** (`OfferResponseService.process_offer_acceptance_webhook`):
   - Only acts when `payload.data.status == "document.completed"`.
   - Extracts PandaDoc / DocuSign document ID and `action_date` timestamp.
   - Updates the offer to `status = Accepted`, sets `offer_response_at`.
   - Generates a tokenised onboarding link (`OnboardingLinks` table, 24-hour expiry) using `OnboardingLinkDAO.get_or_create_onboarding_link`.
   - Sends `send_offer_accepted_email` with the link `{ONBOARDING_LINK_BASE_URL}?token={raw_token}`.
2. **Offer Expiration Webhook** — when `status == "document.voided"`, marks offer as `Expired`.
3. **Token Verification** — `POST /ems/token-verification/...` returns the `user_uuid` associated with a valid, unexpired token.
4. **OTP Verification** — `POST /ems/otp/send`, `POST /ems/otp/verifyOtp`. `Otptable` stores `email`, `otp`, `expirytime`.

**Business Rules:**

- Onboarding token is hashed (`token_hash CHAR(64)`) and unique per user (`uq_onboarding_user_uuid`).
- Token TTL = 24 hours.
- OTP is sent through SMTP, valid for 5 minutes (per email body wording).
- Candidate submit endpoint (`POST /ems/hr/candidate/submit`) requires `user_uuid` only — server-side validates that all mandatory sections exist (`personal_details`, `addresses`, `identity_documents`, `education_documents`, and `experience` if `has_experience == True`).

---

### 4.4 HR Onboarding

**Purpose:** HR-side workflow to read consolidated candidate data, verify each section/document, and progress the offer status.

**Key Features:**

1. **Full Onboarding Aggregator** — `GET /ems/hr/hr/{user_uuid}`: A heavily optimised DAO that fetches OFFER + PERSONAL (Q0), then runs ADDRESSES + IDENTITY + EDUCATION + EXPERIENCE + BANK + PF in parallel (`asyncio.gather`), then resolves all lookups (countries, relations, degrees, identity types, education levels) in a single batch.
2. **Profile-level Verify / Reject** — `POST /ems/hr/verify-profile`: sets `offer_letter_details.status` to `VERIFIED` or `REJECTED`.
3. **Document-level Verify / Reject** — `POST /ems/hr/verify-document`: per `doc_type ∈ {personal, address, education, identity, experience, bank, pf}` — updates `status` and stamps `verified_by`, `verified_at`.
4. **View Document** — `GET /ems/hr/view_documents?file_path=s3://...`: validates S3 path format, ensures the file is owned/registered, returns a pre-signed S3 URL.
5. **Get All Employee Documents** — `GET /ems/hr/employees/documents`: joins offer letters with education / identity / experience tables and returns a flat document list.

**Business Rules:**

- Final candidate submit requires all mandatory sections (`personal`, `address`, `identity`, `education`; `experience` only if `has_experience`).
- After final submit, status becomes `Submitted`.
- Email notifications fire to candidate (confirmation) and HR (`HR_EMAIL` constant `venipriya.p@pavestechnologies.com`).
- Document statuses use enum `uploaded | verified | rejected` (some tables also include `pending`).
- HR cannot view documents that don't exist under the registered S3 path pattern `s3://{bucket}/{folder}/{user_uuid}/{filename}` or `s3://{bucket}/experience_documents/{doc_type}/{user_uuid}/{filename}`.

---

### 4.5 Bulk Join / Bulk Onboarding

**Purpose:** HR action to dispatch joining letters to a batch of verified candidates, attach the PDF, and update their joining metadata.

**Endpoints:**
- `POST /ems/hr/offerletters/bulk-join?preview=true|false`
- `PUT /ems/hr/offerletters/reassign-joining`
- `GET /ems/hr/offerletters/{user_uuid}`
- `GET /ems/hr/offerletters/{user_uuid}/joining-generate-preview`
- `GET /ems/hr/reporting-manager/{employee_id}/employees`

**Key Features:**

1. **Bulk Join** (`HrBulkJoinService.process_bulk_join`):
   - Accepts `user_emails_list`, `joining_date`, `location`, `reporting_time`, `department`, `reporting_manager`, `custom_message`.
   - Filters to VERIFIED users only (`get_verified_users_by_emails`).
   - Resolves the reporting manager via `resolve_reporting_manager` (looks up by `employee_id` or display value).
   - Computes status via `get_joining_status`:
     - `joining_date < today` → `Joining Pending`
     - `is_reassigned` → `Rescheduled`
     - Otherwise → `Joining`
   - Generates PDF (`DocumentService.generate_joining_pdf`) per user, attaches to email via `send_joining_email`.
2. **Preview Mode** — `preview=True` returns the PDF as a FileResponse without DB writes.
3. **Reassign Joining Date** — updates a single user's joining date and triggers a fresh email with new PDF.
4. **Manager Lookup** — `get_employees_under_manager(employee_id)` returns subordinates.

**Business Rules:**

- Only candidates with status `Verified` are considered.
- Past joining date automatically marks `Joining Pending` (the weekly dashboard also enforces this via SQL update for any orphaned `Joining` rows whose date has passed).
- `joining_date` is required.
- Reporting manager must exist; otherwise HTTP 400.

---

### 4.6 Employee Details & Profile Management

**Purpose:** Manage the **permanent** employee record (post-joining) and the rich profile (about, social links).

**Entities:** `employee_details`, `employee_about`, `employee_social_links`.

**Key Features:**

1. **Direct Create Permanent Employee** (`PermanentEmployeeDetailsService.create_employee`):
   - Auto-generates `employee_id` starting from `5100001` (last+1 logic in `generate_employee_id`).
   - Auto-generates a unique `work_email` using combinations of `first_name.last_name@pavestechnologies.com` and fallbacks (`first_initial+last`, suffix counters).
   - Resolves `reporting_manager_uuid` (stored as `employee_id`).
   - Maps department / designation / work_mode / employment_type / employment_status enums.
2. **Bulk Direct Upload** (`bulk_direct_upload`):
   - Parses Excel via `parse_excel`.
   - Within a single outer transaction, runs each row in a `db.begin_nested()` savepoint.
   - Performs Excel duplicate checks (in-memory sets) + DB duplicate checks (`employee_id`, `work_email`).
   - Inserts into `offer_letter_details`, `employee_details`, `personal_details`, `bank_details`, `pf_details`, and two address rows (current + permanent).
   - Reports per-row failures (`failed_records`).
3. **Bulk Template Download** (`download_bulk_template`):
   - Builds an Excel workbook with a hidden `Master` sheet containing named ranges (`CountryCodes`, `EmployeeTypes`, `Currencies`, `Managers`, `WorkModes`, `EmploymentStatuses`, `BloodGroups`, `Genders`, `MaritalStatuses`, `Departments`, plus a per-department designation range).
   - Adds data-validation dropdowns to the data sheet (rows 2..500), with cascading `designation` dropdown that uses `INDIRECT(SUBSTITUTE(department," ","_"))`.
4. **Update / Delete Employee** — fields update one-by-one only when provided (`is not None`).
5. **About Me / Social Links** — CRUD for `EmployeeAbout` and `EmployeeSocialLink`.

**Business Rules:**

- `employee_id` and `work_email` must be globally unique.
- `employee_id` is a String(20) but generated as an integer starting at `5100001`.
- `total_experience` is `DECIMAL(4,1)`.
- `employment_status` enum: `Probation, Active, Resigned, Terminated, Absconded, Exited, On-Notice`.
- `work_mode` enum: `Office, Remote, Hybrid`.
- Bulk upload converts date strings in `dd/MM/yyyy` format if needed.

---

### 4.7 Education Management

**Purpose:** Manage master data (Education Levels, Documents, Degrees) and candidate-level academic records.

**Entities:** `education_level`, `education_document_type`, `country_education_document_mapping`, `degree_master`, `employee_education_document`.

**Key Features:**

1. **Education Level CRUD** — `POST/GET/PUT/DELETE /ems/masters/education-level`.
2. **Degree Master CRUD** — degrees are linked to an `education_uuid` (e.g., B.Tech under "Undergraduate").
3. **Country–Education Document Mapping** — `POST /ems/masters/{educ_level_uuid}/{educ_doc_uuid}/{country_uuid}` creates a mapping that tells the system "for this country, at this education level, this document type is required". Mapping rows carry `is_mandatory`.
4. **Employee Education Document Upload** — multi-part form with file → uploaded to S3 under `education_documents/{user_uuid}/...`. Captures `institution_name`, `institute_location`, `degree_uuid`, `specialization`, `education_mode ∈ {Regular, Distance, Part Time, Online}`, `start_year`, `year_of_passing`, `percentage_cgpa`, `delay_reason`.
5. **Get By Country** — `GET /ems/education/identity-mappings/{country_uuid}` (analogous helper).

**Business Rules:**

- Document name is unique.
- Education name is unique (case- and trim-insensitive via `validate_alphabets_only`).
- Mapping is unique per (`education_uuid`, `education_document_uuid`, `country_uuid`).
- Uploaded files must validate against `validate_alphabets_only` for `institution_name`/`specialization` and `validate_numeric_value` for `percentage_cgpa`.

---

### 4.8 Experience Management

**Purpose:** Capture prior employment history with documentary evidence.

**Entity:** `employee_experience` plus child tables `employee_pay_slips`, `employee_relieving_letter`.

**Key Features:**

1. **Create Experience** (`EmployeeExperienceService.create_experience`):
   - Validates `start_date <= today`, `end_date >= start_date`.
   - Validates only ONE current job per employee.
   - Validates that current job has no `end_date`.
   - Requires `notice_period_days` if `is_current`.
   - Uses `EMPLOYMENT_DOCUMENT_RULES` (per `employment_type ∈ {Full-Time, Part-Time, Intern, Contract, Freelance}`) to enforce mandatory document types per employment type.
   - Allowed file types: `.pdf, .png, .jpg, .jpeg`. Max size 5 MB.
   - Uploads files to S3 in parallel using `asyncio.gather`, organising paths into `exp_certificate_path`, `payslip_path`, `internship_certificate_path`, `contract_aggrement_path`.
2. **Update Experience with Files** — same validation, allows partial file replacement.
3. **Delete Experience** — also deletes associated S3 object for `exp_certificate_path`.
4. **Update / Delete Single Certificate** — granular endpoints for the experience certificate only.
5. **Get Experience by Employee UUID** — fresher logic: when `has_experience=False`, returns empty list rather than 404.

**Business Rules:**

- Status enum: `uploaded | verified | rejected`.
- Future-dated start dates are rejected.
- Multiple current jobs are blocked.
- Document type mapping is enforced strictly (raises HTTP 400 listing missing types).

---

### 4.9 Bank Details Management

**Purpose:** Store and verify employee bank account details for salary credit.

**Entity:** `employee_bank_details` (one-to-one with `offer_letter_details.user_uuid`).

**Key Features:**

1. **Create Bank Details** — validates the employee exists (offer letter), generates `bank_uuid`, stores `account_holder_name`, `bank_name`, `branch_name`, `account_number`, `ifsc_code`, `account_type`.
2. **Read by UUID / User UUID / All**.
3. **Update / Delete**.
4. **Verification** — uses HR verify-document with `doc_type=bank`; status flows `uploaded → verified | rejected`.

**Business Rules:**

- `account_holder_name`, `bank_name`, `account_number`, `ifsc_code`, `account_type` are mandatory.
- Status enum `uploaded | verified | rejected` with default `uploaded`.
- One bank record per `user_uuid` (enforced at the application layer; no DB unique constraint).

---

### 4.10 PF (Provident Fund) Details

**Purpose:** Capture EPF membership status and UAN for compliance reporting.

**Entity:** `employee_pf_details`.

**Key Features:**

1. **Create / Read / Update / Delete** standard CRUD.
2. **Boolean `pf_member`** is mandatory.
3. **`uan_number`** is optional (required only when `pf_member=true`, enforced at frontend).

**Business Rules:**

- Status enum `uploaded | verified | rejected`.
- Verifiable by HR via the same `verify-document` endpoint (`doc_type=pf`).

---

### 4.11 Identity Documents Management

**Purpose:** Track government-issued IDs (passport, Aadhaar, driving license, etc.) per country.

**Entities:** `identity_type`, `country_identity_mapping`, `employee_identity_document`.

**Key Features:**

1. **Identity Type Master** — `POST/GET/PUT/DELETE /ems/identity`.
2. **Country–Identity Mapping** — `POST/PUT/DELETE /ems/identity/country-mapping`. `is_mandatory` flag controls whether a candidate must upload.
3. **Identities by Country Dropdown** — `GET /ems/identity/country-mapping/identities/{country_uuid}`.
4. **Employee Identity Document Update** — `PUT /ems/identity/employee-document/{document_uuid}` (multipart: `mapping_uuid`, `identity_file_number`, `expiry_date`, optional `file`).
5. **Delete Country Mapping** — blocked if any employee already uploaded against it; returns 422 with the list of affected employees.

**Business Rules:**

- One identity document per (`user_uuid`, `mapping_uuid`) is the practical norm (no DB constraint).
- Files stored at S3 under `identity_documents/{user_uuid}/...`.
- Expiry date is optional but tracked.
- Status enum `uploaded | verified | rejected`.

---

### 4.12 Task Management (Onboarding Checklist)

**Purpose:** Lightweight task/checklist module to coordinate Onboarding, Exit, IT Provisioning, Finance Clearance, and Admin tasks per employee.

**Entity:** `employee_tasks`.

**Key Features:**

1. **Create Task** — `POST /ems/api/tasks/create` — fields include `task_title`, `task_type ∈ {Onboarding, Exit, IT Provisioning, Finance Clearance, Admin}`, `description`, `assigned_to`, `assigned_team`, `priority ∈ {High, Medium, Low}`, `status ∈ {To Do, In Progress, Completed, Cancelled}`, `progress %`, `due_date`, `reminder_date`, `send_notification`, `escalation_owner`, `internal_notes`, `comments`.
2. **Update / Delete / List All / List By User**.

**Business Rules:**

- `user_uuid` must exist in `offer_letter_details`.
- Default priority `Medium`, default status `To Do`, default `progress=0`.
- `completed_by` / `completed_at` populated when status moves to `Completed`.

---

### 4.13 Employee Exit Process

**Purpose:** Initiate and track the exit lifecycle of an employee.

**Entity:** `employee_exit`. Status enum:

`Initiated → Manager Approved → HR Approved → Clearance Pending → FnF Pending → Settlement Approved → Paid → Documents Generated → Completed | Rejected`.

**Key Features:**

1. **Create Exit** — `POST /ems/employee-exit/create`. Validates that an active exit does not already exist for the employee.
2. **Get by Employee UUID / Exit UUID / List All**.
3. **Update by Employee UUID / Exit UUID**.
4. **Delete Exit**.

**Business Rules:**

- `exit_type` ∈ {Resignation, Termination, Contract End, Absconded, Retirement}.
- Notice period dates (`notice_start_date`, `notice_end_date`, `notice_period`) tracked.
- `created_by` stamped from JWT.
- Only ONE active exit per employee.
- Upon initiation, manager + HR approvals are auto-created (see 4.14).

---

### 4.14 Exit Approval Workflow

**Purpose:** Two-step exit sign-off (Manager → HR).

**Entity:** `exit_approvals` with `approval_type ∈ {Manager, HR}`, `status ∈ {Pending, Approved, Rejected}`.

**Key Features:**

1. **Create Approvals** (`ExitApprovalDAO.create_exit_approval`) — emits TWO rows per exit (Manager + HR).
2. **Manager Approve** (`manager_approve`):
   - Updates the manager row with status, remarks, `approved_by`, `approved_at`.
   - If `status=Approved`, updates `employee_exit.status` to `Manager Approved`.
3. **HR Approve** (`hr_approve`):
   - Updates the HR row.
   - If approved, sets `employee_exit.status` to `Clearance Pending` AND auto-creates clearance rows via `ExitClearanceService.create_clearances` for all five departments.
4. **Read APIs**: by exit, by employee, history, my pending (by role).

**Business Rules:**

- HR cannot approve before Manager (enforced by frontend; backend records sequence in approvals table).
- Approval rows are deleted-cascade with the parent exit.
- Once approved/rejected, the row is locked (no double-action enforcement built in backend currently — UX driven).

**State Machine (per approval row):**

```
        Pending --(approve)--> Approved
              \--(reject)----> Rejected
```

**Combined Exit State Transitions:**

```
Initiated
   |
   v
Manager Approved (manager_approve → Approved)
   |
   v
HR Approved → Clearance Pending (auto creates 5 clearance rows)
   |
   v
FnF Pending (auto when ALL 5 clearances Approved)
   |
   v
Settlement Approved (approve_settlement)
   |
   v
Paid (mark_paid)
   |
   v
Documents Generated
   |
   v
Completed
```

---

### 4.15 Exit Clearance Management

**Purpose:** Per-department checklist sign-off before F&F is computed.

**Entities:** `exit_clearance` (one row per dept), `exit_clearance_items` (line items inside each dept).

**Key Features:**

1. **Auto-Create Clearances** — fired by HR approval; creates a row per department ∈ `{Manager, IT, HR, Finance, Admin}`.
2. **My Pending** — `get_my_pending(departments)` filters by the current user's allowed departments and `status=Pending`.
3. **Update Clearance** — sets status / remarks / approver. If `Approved`, auto-marks ALL `exit_clearance_items` for that clearance as `Completed`.
4. **Cascade to Exit Status** — once ALL clearances for an exit are `Approved`, the parent exit moves to `FnF Pending`.
5. **Clearance Items CRUD** — `ExitClearanceItemsService` manages the line items inside a department's clearance.

**Business Rules:**

- Status enum (clearance) `Pending | Approved | Rejected`.
- Status enum (item) `Pending | Completed`.
- Approving a clearance auto-completes its items.

---

### 4.16 Exit Interview

**Purpose:** Capture qualitative feedback from the departing employee.

**Entity:** `exit_interview`.

**Key Features:**

1. **Create Interview** — one per exit (enforced); fields `reason_for_leaving`, `company_feedback`, `manager_feedback`, `rating`.
2. **Read / Update / Delete**.

**Business Rules:**

- Exactly one interview per exit (HTTP 400 if duplicate).
- `rating` is an integer (1–5 by convention).
- Updates use `dict(exclude_unset=True)` — only provided fields are modified.

---

### 4.17 Exit Documents (Experience Letter, Relieving Letter, etc.)

**Purpose:** Generate and serve official exit documents.

**Entity:** `exit_documents`. `document_type` ∈ {`Relieving Letter`, `Experience Letter`, `Full & Final`, `NOC`, `Resignation Letter`, `Termination Letter`}.

**Key Features:**

1. **Generate Single Document** (`ExitDocumentsService.generate_single_document`):
   - Loads the exit context (`employee_id`, names, `last_working_day`, current date).
   - Renders the chosen Jinja2 template via `Backend/Business_Layer/utils/document_generator.generate_pdf`.
   - Uploads the resulting PDF bytes to S3 under `exit_documents/{employee_uuid}/{file_name}`.
   - Persists a row in `exit_documents` with `uploaded_by` and `file_path`.
2. **List Documents by Exit / Get Single / View / Download** — pre-signed URLs from S3 with `ResponseContentDisposition` set to `inline` (view) or `attachment` (download).

**Business Rules:**

- File name pattern: `{doc_type}_{employee_id}.pdf`.
- Once all documents required for the exit are generated, the exit can move to `Documents Generated` (caller responsibility).

---

### 4.18 Exit Final Settlement

**Purpose:** Compute the Full and Final settlement.

**Entity:** `exit_final_settlement`. Status enum `Pending | Approved | Paid`.

**Computation:**

```
net_payable = last_salary + leave_encashment + bonus - deductions
```

**Key Features:**

1. **Create Settlement** — DAO auto-computes `net_payable`.
2. **Get Settlement** by exit.
3. **Approve Settlement** — stamps `approved_by`, `approved_at`, sets parent exit status `Settlement Approved`.
4. **Mark Paid** — sets settlement.status=`Paid`, exit.status=`Paid`.

**Business Rules:**

- One settlement per exit (no DB constraint, application norm).
- Deductions are subtracted, never added back.
- Net payable is stored, not recomputed on read (data immutability after approval).

---

### 4.19 Dashboard & Analytics

**Purpose:** Operational and analytical views for HR leadership.

**Endpoints:**

- `GET /ems/dashboard/onboarding-summary?start_date&end_date` — overview, pipeline, pending actions, metrics, documents verified counts, aging buckets, recent activity.
- `GET /ems/dashboard/celebrations` — upcoming birthdays/anniversaries within next 15 days.
- `GET /ems/analytics/dashboard` — returns 4 panels:
  - **demographics**: total, gender, employmentType, workerType, nationality, ageGroups, experience.
  - **workerDept**: permanent vs contingent per department.
  - **genderDept**: female vs male per department.
  - **employmentDept**: full / partTime / intern / contract / freelance per department.

**Analytics Logic (Backend/Business_Layer/services/analytics_service.py):**

- **Age buckets**: `18-21, 22-25, 26-30, 31-40, 41-55`.
- **Experience buckets**: `0-1, 1-2, 2-5, 5-10, 10+`.
- **Worker type**: `Full-Time → Permanent`, everything else → `Contingent`.
- **Gender normalisation**: `M/Male → male`, `F/Female → female`, else `other`.
- Joins `employee_details` ⟕ `offer_letter_details` ⟕ `personal_details` ⟕ `countries` ⟕ `departments` ⟕ `designations`.

---

### 4.20 Weekly Dashboard

**Purpose:** Visualise weekly and monthly joining stats.

**Endpoint:** `GET /ems/weekly-dashboard/?start_date=&end_date=`.

**Logic (Backend/Business_Layer/services/weekly_dashboard_service.py):**

1. Auto-updates any `Joining` rows with past `joining_date` to `Joining Pending` via an SQL `UPDATE` (this is the system's reconciliation routine in lieu of a cron job).
2. Loops filtered offers (those with `joining_date` in `[start_date, end_date]`).
3. Buckets by:
   - Day of week (Mon–Sun) → `weeklyJoinings`.
   - Calendar week within month → `monthlyJoinings` (5 buckets pre-filled).
4. Returns `summary`, `monthlyJoinings`, `weeklyJoinings`, `joinedCandidates`, `activities` (last 6 events).

**Activity Message Templates:**

- Completed: "{name} completed joining for {role}."
- Joining Pending: "{name} missed joining date."
- Joining: "{name} is scheduled for joining as {role}."

---

### 4.21 Master Data Management (Departments, Designations)

**Purpose:** Centralised lookup tables used across the system.

**Entities:** `departments`, `designations` (FK to department), plus master tables `countries`, `education_level`, `education_document_type`, `identity_type`, `relation_master`, `degree_master`, `contacts`, `deliverable_items`, `receivable_items`.

**Key Features:**

- Full CRUD for each (`/ems/departments`, `/ems/designations`, etc.).
- Unique constraints on names (e.g., department_name, education_name, identity_type_name).
- Soft activation flag (`is_active`) for countries and education levels (deactivate/activate via PUT).
- Country dropdown filtered to `is_active=True` by default.
- Designations are cascaded under their department (UI dropdown driven by the per-department named range in the Excel template).

**Business Rules:**

- Departments cannot be deleted while designations or employees reference them (FK `ondelete=RESTRICT`).
- Mappings (country-identity, country-education-document) are blocked from deletion if employee documents reference them.

---

### 4.22 Organisation Tree

**Purpose:** Render the reporting hierarchy under any manager.

**Endpoint:** `GET /ems/api/organisation/...`.

**Logic:** `OrganizationTreeService.get_organization_hierarchy(employee_id)`:

- Fetches the manager record (404 if not found).
- Fetches department + designation names.
- Lists all employees whose `reporting_manager_uuid == manager.employee_id` (the field name says "uuid" but stores `employee_id`).
- Returns:

```
{
  "manager": { employee_id, user_uuid, name, department, designation, location },
  "employees": [ { ... }, { ... } ]
}
```

**Business Rule:** A non-existent manager throws 404. Empty employee list is returned for leaf managers.

---

### 4.23 OTP Verification

**Purpose:** Secondary verification for sensitive candidate actions (e.g., onboarding link access, identity submission).

**Entity:** `otptable`.

**Endpoints:** `POST /ems/otp/send`, `POST /ems/otp/verifyOtp`.

**Logic:**

- `send`: generates a numeric OTP, stores it with `expirytime` (5 minutes per email template), and sends an SMTP email via `send_otp_email`.
- `verifyOtp`: validates OTP matches and is not expired.
- Both endpoints are open (in `JWTMiddleware.open_endpoints`).

---

### 4.24 Token Verification

**Purpose:** Allow the candidate to use a one-time, hashed onboarding link without a JWT.

**Entity:** `onboarding_links` (FK to `offer_letter_details`, unique `token_hash` and `user_uuid`).

**Endpoint:** `POST /ems/token-verification/...`.

**Logic:** `OnboardingVerifyLinkService.verify_token` returns the `user_uuid` after looking up `token_hash` (raises ValueError if invalid or expired). The token TTL defaults to 24 hours.

---

### 4.25 Document Generation (PDF)

**Purpose:** Render branded PDF documents (offer letter, joining letter, exit letters) from Jinja2 + WeasyPrint.

**Components:**

- `Backend/templates/offer_letter.html` (offer letter template).
- `Backend/Business_Layer/utils/document_generator.generate_pdf(template_name, context)` — returns PDF bytes.
- `DocumentService.generate_offer_pdf` and `DocumentService.generate_joining_pdf` orchestrate rendering and writing to `generated_pdfs/`.
- `GET /generate-offer` (top-level, demo route) returns a sample PDF with hard-coded data.

**Storage:** PDFs are written to `generated_pdfs/` (Docker volume `onboarding-pdfs`) before being base64-encoded and shipped to DocuSign.

---

### 4.26 DocuSign Integration

**Purpose:** E-sign offer letters with optional manager CC.

**Configuration (env):** `DOCUSIGN_BASE_URL`, `DOCUSIGN_ACCOUNT_ID`, `DOCUSIGN_TEMPLATE_ID`. Token generated by `generate_docusign_access_token`.

**Key Methods:**

- `send_bulk_offerletters_via_docusign_pdf(request_data, current_user_id)`:
  - Generates token ONCE for the batch.
  - For each `user_uuid`: reads offer, reads PDF from `generated_pdfs/offer_{user_uuid}.pdf`, base64-encodes.
  - Builds signers — Manager (recipientId=1, routingOrder=1) if a CC manager exists, then Employee (recipientId=2, routingOrder=2). If no manager, Employee is recipient 1.
  - Sets sign tabs at fixed coordinates (`pageNumber=5`, x=120/420, y=300).
  - Posts envelope to DocuSign with `status=sent`.
  - Stores returned `envelopeId` in `pandadoc_draft_id` column (legacy name reused for DocuSign).
  - Updates `offer_letter_details.status` to `Offered`.
- `create_docusign_draft` — uses the templated envelope flow (`templateId` + `templateRoles`) with status `created` (for preview/draft scenarios).
- `get_docusign_preview` — returns a recipient view URL using `clientUserId` (embedded signing).
- `get_final_offer_preview` — streams the signed PDF back to the client.

**Business Rules:**

- Only ONE manager (the first CC email) is supported in `send_bulk_offerletters_via_docusign_pdf`.
- DocuSign envelope ID is reused as a generic "draft id" (the column is `pandadoc_draft_id` for historical reasons).
- The legacy PandaDoc methods (`create_offerletter_draft_with_pandadoc`, `poll_pandadoc_draft_status`, `send_pandadoc_offerletter`) remain in code but are not the active path.

---

### 4.27 Email Notifications

**Purpose:** Asynchronous notifications via SMTP (Gmail-compatible). All email helpers live in `Backend/Business_Layer/utils/email_utils.py`.

**Configuration:** `EMAIL_USER`, `EMAIL_PASSWORD`, `EMAIL_HOST`, `EMAIL_PORT` (env vars).

**Email Functions:**

| Function | When Triggered |
|---|---|
| `send_email(to, subject, content, cc)` | Generic helper. |
| `send_offer_accepted_email(to, name, onboarding_url, cc)` | After candidate signs offer via DocuSign/PandaDoc webhook. |
| `send_otp_email(to, otp)` | When OTP requested. |
| `send_candidate_onboarding_submitted_email(to, candidate_name)` | After candidate clicks "Final Submit". |
| `send_hr_onboarding_submitted_email(hr_email, candidate_name, candidate_email, submitted_at)` | Same trigger as above, sent to HR (`HR_EMAIL` constant). |
| `send_joining_email(to, name, joining_date, location, reporting_time, department, reporting_manager, custom_message, attachment_bytes, attachment_filename)` | Bulk Join / Reassign Joining. |
| `send_smtp_email(msg, to_emails, cc_emails)` | Low-level CC helper. |
| `send_joinning_email` (cron) | From `joining_reminder.py` (legacy reminder email). |

---

### 4.28 Audit Logging

**Purpose:** Persist every write operation to a centralised `audit_trail` table for compliance.

**Entity:** `audit_trail` — fields: `audit_uuid`, `entity_name`, `entity_id`, `operation ∈ {CREATE, UPDATE, DELETE}`, `user_id`, `old_data (JSON)`, `new_data (JSON)`, `ip_address`, `host`, `created_at`, `endpoint`.

**Mechanism:** `AuditMiddleware` (currently registered in commented form):
- Skips GET / OPTIONS and any path in its allowlist (`/otp`, `/token-verification`, `/offer-approval-requests`, `/offer-approval`, `/docusign`, `/offerletters`, `/hr`, `/bulk-template`).
- For UPDATE / DELETE, fetches `old_data` BEFORE calling `next`.
- Captures response body and, for CREATE, re-fetches the created entity using the ID it finds in the response JSON.
- For UPDATE, diffs old vs new and stores only the changed columns.
- IP captured from `X-Forwarded-For` → `X-Real-IP` → `request.client.host`.

---

## 5. Business Rules & Validation Rules (Cross-Cutting)

1. **UUIDs**: All primary business records use UUIDv7 (`generate_uuid7()`) for chronological sortability.
2. **Authentication**: JWT bearer token required for all `/ems/*` endpoints except the explicit allowlist in `JWTMiddleware.open_endpoints` (docs, OTP, token verification, candidate submit, offer response webhook, masters seeding, etc.).
3. **RBAC**: `require_roles()` performs **case-insensitive ANY-match** between JWT `roles` list and the route's allowed roles.
4. **Email Uniqueness**: `mail` on `offer_letter_details` and `work_email` on `employee_details` are unique at DB level.
5. **CC Emails**: Stored as comma-separated string; normalised to list at response time.
6. **Phone**: `validate_phone_number(country_code, number, type)` uses `phonenumbers` library; rejects invalid combos.
7. **Date Rules**:
   - DOB validated by `validate_date_of_birth`.
   - Experience start date ≤ today, end date ≥ start date.
   - Joining date drives `Joining → Joining Pending → Rescheduled` transitions.
8. **File Rules**:
   - Identity/Education docs: any size (no explicit limit in code), stored on S3 with `ServerSideEncryption=AES256`.
   - Experience docs: 5 MB max, only `.pdf, .png, .jpg, .jpeg`.
   - File naming: `{name}_{YYYYMMDD_HHMMSS}_{8charUUID}{ext}`.
9. **S3 Path Convention**: `s3://{bucket}/{folder}/{user_uuid}/{filename}` (experience adds doc_type level: `experience_documents/{doc_type}/{user_uuid}/{filename}`).
10. **Approval Locking**: Offer cannot be deleted once an approval request exists; reassignment blocked after any APPROVED action.
11. **Exit Singleton**: Only one `employee_exit` per `employee_uuid`.
12. **Settlement Formula**: `net_payable = last_salary + leave_encashment + bonus - deductions`.
13. **Clearance Cascade**: HR approval → 5 clearance rows auto-created. All 5 approved → exit moves to `FnF Pending`.
14. **Status Reconciliation**: Weekly dashboard reconciles past-due `Joining` rows to `Joining Pending` on every read.
15. **Audit**: Every CREATE/UPDATE/DELETE outside the allowlist is logged.
16. **Postal Code**: `validate_postal_code` (India: 6 digits, regex `^\d{6}$`).
17. **Country Activation**: Inactive countries cannot be used to create new contacts.
18. **Mapping Deletion Protection**: Country–identity / country–education mappings cannot be deleted if any employee document depends on them.
19. **Bulk Excel Header Aliasing**: `_COLUMN_ALIASES` dictionary normalises common column-name variants (e.g., "First Name" → `first_name`, "Annual CTC" → `total_ctc`).
20. **Email Trigger Idempotency**: Email failure does NOT roll back the DB transaction (logs the failure to stdout).

---

## 6. Approval Workflows (State Machine Diagrams in Text)

### 6.1 Offer Letter Approval Workflow

```
        +--------+
        |Created |
        +---+----+
            | HR submits to approver
            v
        +--------+      reassign (if not APPROVED)        +-------------+
        |PENDING |<-----------------------------------> | New Approver|
        +---+----+
       /    |    \
APPROVED  ON_HOLD  REJECTED
   |        |         |
   v        v         v
(can be    (HR may   (HR can
 sent to   reassign  delete offer
 candidate) or take   if status
 via       further    is Created
 DocuSign) action)    or Rejected)

After APPROVED → HR triggers send → status = Offered
```

### 6.2 Candidate Offer Response Workflow

```
Offered
   |
   |---(DocuSign signed) ---> Accepted ----> tokenised onboarding email sent
   |                                              |
   |                                              v
   |                                       Candidate fills profile
   |                                              |
   |                                              v
   |                                          Submitted
   |                                              |
   |                                              v
   |                                          HR verifies
   |                                              |
   |                                              v
   |                                          Verified
   |                                              |
   |                                              v
   |                                       HR bulk-joins
   |                                              |
   |                                              v
   |                                  Joining | Joining Pending | Rescheduled
   |                                              |
   |                                              v
   |                                          Completed
   |
   |---(envelope voided/expired) -----------> Expired
```

### 6.3 Exit Approval & Clearance Workflow

```
Initiated
   |
   v
Manager Approval --(Rejected)--> Rejected (terminal)
   |Approved
   v
Manager Approved
   |
   v
HR Approval --(Rejected)--> Rejected (terminal)
   |Approved
   v
HR Approved
   |
   |--auto-create 5 clearance rows (Manager, IT, HR, Finance, Admin)
   v
Clearance Pending
   |
   |--(each dept approves; all items auto-Completed on dept Approve)
   v
FnF Pending  (all 5 clearances Approved)
   |
   v
Settlement Created (Pending)
   |
   v
Settlement Approved
   |
   v
Paid
   |
   v
Documents Generated
   |
   v
Completed
```

---

## 7. Email Notification Matrix

| # | Event | Trigger Function | Recipient(s) | Subject |
|---|-------|------------------|--------------|---------|
| 1 | Offer letter sent via DocuSign | DocuSign envelope `status=sent` | Candidate (signer) + Manager (CC, 1st signer) | "Please sign the offer letter" |
| 2 | Offer accepted (DocuSign/PandaDoc webhook) | `send_offer_accepted_email` | Candidate | "Offer Accepted – Next Steps" |
| 3 | OTP request | `send_otp_email` | Candidate | "Email Verification OTP" |
| 4 | Candidate onboarding submitted | `send_candidate_onboarding_submitted_email` | Candidate | "Onboarding Submitted Successfully" |
| 5 | Candidate onboarding submitted | `send_hr_onboarding_submitted_email` | HR (`venipriya.p@pavestechnologies.com`) | "Candidate Onboarding Submitted" |
| 6 | Bulk Join processed | `send_joining_email` (with PDF attached) | Each verified candidate | "Joining Letter – Welcome Aboard" |
| 7 | Reassign Joining Date | `send_joining_email` (with new PDF) | Affected candidate | "Joining Letter – Welcome Aboard" |
| 8 | Joining date reminder (cron, currently disabled) | `send_joinning_email` from `joining_reminder.py` | Hard-coded `sumiyapatan2@gmail.com` (placeholder) | "Upcoming Employee Joinings (Next 3 Days)" |

---

## 8. Cron Jobs & Scheduled Tasks

### 8.1 Configured but Disabled

The `AsyncIOScheduler` block in `main.py` is **commented out**. When enabled, it schedules:

- **Job ID**: `joining_reminder`
- **Function**: `send_joining_date_reminders` (from `Backend/corn_jobs/joining_reminder.py`)
- **Cadence in commented config**: every 10 seconds (`second="*/10"`) — clearly a development placeholder; the production intent (also commented) was a daily 9 PM/11 PM run.
- **Behaviour**: Fetches users whose `joining_date == today + 3 days` (via `OfferLetterDAO.get_upcoming_joinings`, which actually computes a fixed 3-day offset), composes a summary HTML body, and sends it to a placeholder email.
- **Max Instances**: 1 (`max_instances=1`, `coalesce=True`).

### 8.2 Implicit Reconciliation (Synchronous, Not a Cron)

`get_dashboard_data` in `weekly_dashboard_service.py` runs an **idempotent UPDATE** on every weekly-dashboard request:

```sql
UPDATE offer_letter_details
SET status = 'Joining Pending'
WHERE joining_date < CURRENT_DATE
  AND status = 'Joining';
```

This effectively replaces a cron in the current deployment.

---

## 9. Integration Points

### 9.1 External Services

| Integration | Direction | Purpose | Configuration |
|---|---|---|---|
| **DocuSign eSignature REST API** | Outbound | Envelope creation, recipient view, signed PDF retrieval | `DOCUSIGN_BASE_URL`, `DOCUSIGN_ACCOUNT_ID`, `DOCUSIGN_TEMPLATE_ID`, JWT token via `generate_docusign_access_token` |
| **PandaDoc API** (legacy) | Outbound | Draft/poll/send (alternative e-sign path retained in code) | `PANDADOC_API_KEY`, `PANDADOC_TEMPLATE_ID`, `PANDADOC_DRAFT_API_URL`, `PANDADOC_POLL_API_URL`, `PANDADOC_SEND_API_URL` |
| **PandaDoc/DocuSign Webhook** | Inbound | `document.completed` → offer Accepted; `document.voided` → offer Expired | Public endpoint allowlisted in JWT middleware |
| **AWS S3** | Outbound | All employee files (identity / education / experience / exit documents) | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `S3_BUCKET_NAME`; uploads encrypted with AES256; pre-signed URLs with `inline` / `attachment` disposition |
| **SMTP (Email)** | Outbound | Transactional emails (offer accepted, joining, OTP, onboarding) | `EMAIL_USER`, `EMAIL_PASSWORD`, `EMAIL_HOST`, `EMAIL_PORT` (TLS) |
| **MySQL** | Bi-directional | Async via SQLAlchemy + `asyncmy`; pool size 15, max overflow 30, recycle 1800s | `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_DRIVER` |
| **Redis** | Outbound | Cache control endpoints exposed under `/ems/cache` | Standard Redis URL via `redis_cache_routes` |
| **UMS (User Management System)** | Outbound HTTP | Fetch admin user list to resolve approver / requester names (`fetch_admin_users_reformed`) | Bearer auth header forwarded |
| **RMS (Resource Management System)** | Outbound | Resource integration routes under `/ems/api/rms-...` | External base URL via env |
| **Docker Networks** | Infra | `intranet-network` (bridge) + `cdc-network` (external) for change-data-capture | `docker-compose.yml` |

### 9.2 Internal Integration Surface

| Surface | Purpose |
|---|---|
| `Backend/API_Layer/middleware/jwt_middleware.py` | Decodes JWT, attaches `request.state.user` (keys: `user_id`, `employee_id`, `roles`) |
| `Backend/API_Layer/middleware/audit_middleware.py` | Captures request/response and writes to `audit_trail` |
| `Backend/API_Layer/utils/role_based.py` | Role enforcement dependency |
| `Backend/DAL/utils/dependencies.get_db` / `Backend/DAL/utils/database.get_read_db` | Async session lifecycle |
| `Backend/DAL/utils/storage_utils.S3StorageService` | Singleton via `get_storage_service()`; all file IO routes through this |
| `Backend/Business_Layer/utils/uuid_generator.generate_uuid7` | UUID generator |
| `Backend/Business_Layer/utils/validation_utils` | Shared validators |
| `Backend/Business_Layer/utils/excel_parcer.parse_excel` | Excel ingestion |
| `Backend/Business_Layer/utils/experience_document_rules.EMPLOYMENT_DOCUMENT_RULES` | Per-employment-type document matrix |
| `Backend/Business_Layer/utils/ums_users_list.fetch_admin_users_reformed` | UMS users fetcher |

### 9.3 Public OpenAPI

The system exposes:
- Swagger UI: `/ems/docs`
- OpenAPI JSON: `/ems/openapi.json`
- Security scheme: `BearerAuth` (JWT) added globally via the custom `custom_openapi` patch.
- Schema patcher (`_patch_schema_node`) rewrites `contentMediaType: application/octet-stream` → `format: binary` so Swagger UI renders correct file-upload widgets.

---

**End of Functional Document.**
