# Zecpath ATS – API Usage Guide

## 1. Introduction

This document explains how to interact with the Zecpath Applicant Tracking System (ATS) REST API.

It covers:

- User registration and authentication
- Employer and candidate profile management
- Job creation and discovery
- Job applications
- Resume uploads and downloads
- Role-based access control
- Pagination, filtering, and common HTTP responses

## 2. Base URL

For local development:

```text
http://127.0.0.1:8000
```

All API endpoints are prefixed with `/api/`, except Django's admin interface.

## 3. Authentication

Zecpath uses JSON Web Token (JWT) authentication through Django REST Framework SimpleJWT.

Authenticated API requests must include an access token in the Authorization header:

```http
Authorization: Bearer <access_token>
```

### 3.1 Register a user

**Endpoint**

```http
POST /api/accounts/register/
```

**Access:** Public

**Request body – JSON**

```json
{
    "username": "candidate1",
    "email": "candidate@example.com",
    "password": "StrongPassword@123",
    "phone": "9876543210",
    "role": "CANDIDATE"
}
```

Supported roles:

- `CANDIDATE`
- `EMPLOYER`

Admin self-registration is not allowed.

**Successful response – 201 Created**

```json
{
    "message": "Registration successful. Please check your email to activate your account.",
    "user": {
        "user_id": 1,
        "username": "candidate1",
        "email": "candidate@example.com",
        "phone": "9876543210",
        "role": "CANDIDATE",
        "is_verified": false,
        "created_at": "2026-11-10T10:00:00Z",
        "updated_at": "2026-11-10T10:00:00Z"
    }
}
```

The timestamps and IDs above are illustrative.

New accounts remain inactive until email verification is completed.

### 3.2 Verify email

**Endpoint**

```http
GET /api/accounts/verify-email/<user_id>/<token>/
```

**Access:** Public

The verification link contains the user ID and verification token.

**Successful response – 200 OK**

```json
{
    "message": "Email verified successfully. Your account is now active."
}
```

Invalid, expired, or unusable verification links return:

```json
{
    "error": "Invalid or expired verification link."
}
```

**Status:** 400 Bad Request

### 3.3 Login

**Endpoint**

```http
POST /api/accounts/login/
```

**Access:** Public

**Request body – JSON**

```json
{
    "username": "candidate1",
    "password": "StrongPassword@123"
}
```

**Successful response – 200 OK**

```json
{
    "refresh": "<refresh_token>",
    "access": "<access_token>"
}
```

Use the access token for authenticated API requests.

### 3.4 Refresh access token

**Endpoint**

```http
POST /api/accounts/token/refresh/
```

**Access:** Public

**Request body – JSON**

```json
{
    "refresh": "<refresh_token>"
}
```

The endpoint returns a new access token. With the configured refresh-token rotation, a new refresh token may also be returned.

### 3.5 Get current user

**Endpoint**

```http
GET /api/accounts/me/
```

**Access:** Authenticated users

**Headers**

```http
Authorization: Bearer <access_token>
```

**Successful response – 200 OK**

```json
{
    "message": "User details retained successfully",
    "user": {
        "user_id": 1,
        "username": "candidate1",
        "email": "candidate@example.com",
        "phone": "9876543210",
        "role": "CANDIDATE",
        "is_verified": true,
        "created_at": "2026-11-10T10:00:00Z",
        "updated_at": "2026-11-10T10:10:00Z"
    }
}
```

### 3.6 Logout

**Endpoint**

```http
POST /api/accounts/logout/
```

**Access:** Authenticated users

**Headers**

```http
Authorization: Bearer <access_token>
```

**Request body – JSON**

```json
{
    "refresh": "<refresh_token>"
}
```

The submitted refresh token must belong to the authenticated user.

**Successful response – 200 OK**

```json
{
    "message": "Logout successful"
}
```

The refresh token is blacklisted to prevent further use. An already-issued access token can remain valid until it expires.

---

## 4. Employer APIs

All employer profile endpoints require an authenticated, active, verified user with the `EMPLOYER` role.

### 4.1 Create employer profile

**Endpoint**

```http
POST /api/employers/profile/
```

**Access:** Employer

**Request body – JSON**

```json
{
    "company_name": "Zecser Business LLP",
    "company_domain": "Software Development",
    "company_size": "11-50",
    "company_description": "Technology and software development company.",
    "website": "https://example.com",
    "location": "Kerala, India"
}
```

**Successful response – 201 Created**

Returns the employer profile.

If a profile already exists, the existing profile is returned with 200 OK. If the profile was soft-deleted, the endpoint returns 409 Conflict and advises contacting an administrator for restoration.

### 4.2 Retrieve employer profile

**Endpoint**

```http
GET /api/employers/profile/
```

**Access:** Employer

Returns the authenticated employer's active profile.

### 4.3 Update employer profile

**Endpoint**

```http
PUT /api/employers/profile/
```

Replaces the profile data. Supply all required fields.

### 4.4 Partial Update Employer Profile

```http
PATCH /api/employers/profile/
```

Supply only the fields that need to be changed.

**Access:** Employer

### 4.5 Delete employer profile

**Endpoint**

```http
DELETE /api/employers/profile/
```

**Access:** Employer

Performs a soft delete. The profile is marked as deleted rather than permanently removed.

**Successful response – 200 OK**

```json
{
    "message": "Employer profile deleted successfully."
}
```

---

## 5. Candidate APIs

Candidate endpoints require an authenticated, active, verified user with the `CANDIDATE` role.

### 5.1 Create candidate profile

**Endpoint**

```http
POST /api/candidates/profile/
```

**Access:** Candidate

**Request body – JSON**

```json
{
    "full_name": "Arun Kumar",
    "skills": "Python, Django, SQL, REST API",
    "location": "Kochi, Kerala",
    "expected_salary": "500000.00"
}
```

**Successful response – 201 Created**

```json
{
    "candidate_id": 1,
    "full_name": "Arun Kumar",
    "resume_name": null,
    "skills": "Python, Django, SQL, REST API",
    "location": "Kochi, Kerala",
    "expected_salary": "500000.00",
    "educations": [],
    "experiences": [],
    "created_at": "2026-11-10T10:00:00Z",
    "updated_at": "2026-11-10T10:00:00Z"
}
```

### 5.2 Retrieve candidate profile

**Endpoint**

```http
GET /api/candidates/profile/
```

**Access:** Candidate

Returns the authenticated candidate's active profile.

### 5.3 Update candidate profile

**Complete update**

```http
PUT /api/candidates/profile/
```

### 5.4 Partial update candidate profile

```http
PATCH /api/candidates/profile/
```

**Access:** Candidate

The `educations` and `experiences` fields are read-only nested response fields in the current candidate profile serializer.

### 5.5 Delete candidate profile

**Endpoint**

```http
DELETE /api/candidates/profile/
```

**Access:** Candidate

Performs a soft delete.

**Successful response – 200 OK**

```json
{
    "message": "Candidate profile deleted successfully."
}
```

The profile and its related records are retained. This preserves application history and resume files.

---

## Candidate Resume APIs

The candidate resume upload accepts PDF, DOC, and DOCX files.

**File restrictions**

- Maximum file size: 5 MB
- Allowed extensions: `.pdf`, `.doc`, `.docx`
- Empty files are rejected.
- File signatures and DOCX archive structure are validated.

### 5.6 Upload or replace candidate resume

**Endpoint**

```http
POST /api/candidates/resume/
```

**Access:** Candidate

**Postman configuration**

1. Select `POST`.
2. Add the candidate's Bearer access token.
3. Select Body → form-data.
4. Add a field named `resume`.
5. Change its type from Text to File.
6. Select the resume file.
7. Send the request.

Do not manually set the multipart `Content-Type` header. Postman generates the required boundary.

**Successful response – 201 Created**

```json
{
    "message": "Resume uploaded successfully.",
    "resume_name": "candidate_resume.pdf",
    "file_size": 245760
}
```

Replacing an existing resume returns 200 OK.

### 5.7 Download candidate resume

**Endpoint**

```http
GET /api/candidates/resume/download/
```

**Access:** Candidate

Downloads the authenticated candidate's own resume as a file attachment.

A candidate cannot use this endpoint to download another candidate's resume.

---

## 6. Job APIs

### 6.1 Create job

**Endpoint**

```http
POST /api/jobs/
```

**Access:** Employer

**Request body – JSON**

```json
{
    "job_title": "Python Developer",
    "description": "Develop and maintain Python-based applications.",
    "location": "Kochi, Kerala",
    "salary": "600000.00",
    "employment_type": "FULL_TIME",
    "work_mode": "HYBRID",
    "is_active": true
}
```

Supported employment types:

| Value | Description |
|---|---|
| `FULL_TIME` | Full Time |
| `PART_TIME` | Part Time |
| `CONTRACT` | Contract |
| `INTERNSHIP` | Internship |
| `REMOTE` | Remote |

Supported work modes:

| Value | Description |
|---|---|
| `ONSITE` | On-site |
| `REMOTE` | Remote |
| `HYBRID` | Hybrid |

The employer is assigned by the backend using the authenticated user. Clients cannot assign or change job ownership through `employer_id`.

**Successful response – 201 Created**

```json
{
    "message": "Job created successfully.",
    "job": {
        "job_id": 1,
        "employer_id": 1,
        "job_title": "Python Developer",
        "description": "Develop and maintain Python-based applications.",
        "location": "Kochi, Kerala",
        "salary": "600000.00",
        "employment_type": "FULL_TIME",
        "work_mode": "HYBRID",
        "is_active": true,
        "created_at": "2026-11-10T10:00:00Z",
        "updated_at": "2026-11-10T10:00:00Z"
    }
}
```

### 7.2 List employer jobs

**Endpoint**

```http
GET /api/jobs/
```

**Access:** Employer

Returns paginated jobs belonging to the authenticated employer.

### 6.3 Retrieve, update, or delete an individual job

**Endpoint**

```http
/api/jobs/<job_id>/
```

| Method | Operation |
|---|---|
| GET | Retrieve job |
| PUT | Completely update job |
| PATCH | Partially update job |
| DELETE | Delete job |

**Access:**

- Employers can access only their own jobs.
- Admins can access any job.

Successful update responses include a message and the updated job object. Successful deletion returns:

```json
{
    "message": "Job deleted successfully."
}
```

Job deletion is a permanent delete in the current implementation.

### 6.4 Admin job listing

**Endpoint**

```http
GET /api/jobs/admin/
```

**Access:** Admin

Returns a paginated list of jobs across employers.

### 6.5 Public available-job listing

**Endpoint**

```http
GET /api/jobs/available/
```

**Access:** Public

Returns paginated active jobs, newest first.

Supported query parameters:

| Parameter | Purpose | Example |
|---|---|---|
| `role` | Search job title | `?role=Python` |
| `date` | Filter by posting date | `?date=2026-11-10` |
| `status` | Filter by status | `?status=ACTIVE` |
| `search` | Search title, description, or location | `?search=Python` |
| `page` | Select page number | `?page=2` |
| `page_size` | Set page size | `?page_size=20` |

Examples:

```http
GET /api/jobs/available/?role=Python
```

```http
GET /api/jobs/available/?search=Kochi
```

```http
GET /api/jobs/available/?date=2026-11-10
```

```http
GET /api/jobs/available/?role=Python&search=Kochi&page=1&page_size=20
```

The date format must be `YYYY-MM-DD`.

**Important implementation note:** The public listing starts by filtering `is_active=True`. Therefore, `status=INACTIVE` currently produces no inactive job results, even though the status parameter accepts that value. The public detail endpoint also exposes active jobs only.

### 6.6 Public job detail

**Endpoint**

```http
GET /api/jobs/available/<job_id>/
```

**Access:** Public

Returns the details of an individual active job.

Inactive or nonexistent jobs return 404 Not Found.

---

## 7. Application APIs

### 7.1 Apply for a job

**Endpoint**

```http
POST /api/applications/
```

**Access:** Candidate

The candidate must have an active profile and the job must be active.

**Option A – Apply using the candidate profile resume**

Use JSON:

```json
{
    "job_id": 1,
    "cover_letter": "I am interested in this Python Developer position."
}
```

The API copies the candidate's current profile resume into the application.

**Option B – Apply using a separate resume**

Use Postman Body → form-data:

| Key | Type | Value |
|---|---|---|
| `job_id` | Text | `1` |
| `cover_letter` | Text | I am interested in this position. |
| `resume` | File | Select a PDF, DOC, or DOCX file |

The uploaded application-specific resume is stored independently.

**Successful response – 201 Created**

```json
{
    "application_id": 1,
    "candidate_id": 1,
    "job_id": 1,
    "job_title": "Python Developer",
    "resume_name": "candidate_resume.pdf",
    "cover_letter": "I am interested in this Python Developer position.",
    "status": "PENDING",
    "applied_at": "2026-11-10T10:00:00Z",
    "updated_at": "2026-11-10T10:00:00Z"
}
```

The `resume` field is write-only. The response contains `resume_name`, not a public file URL.

A candidate cannot apply twice for the same job.

### 7.2 List my applications

**Endpoint**

```http
GET /api/applications/my-applications/
```

**Access:** Candidate

Returns the authenticated candidate's applications, newest first, with pagination.

### 7.3 List applications received by employer

**Endpoint**

```http
GET /api/applications/received/
```

**Access:** Employer

Returns applications submitted to jobs owned by the authenticated employer, newest first, with pagination.

Employers cannot retrieve another employer's applications through this endpoint.

### 7.4 Update application status

**Endpoint**

```http
PATCH /api/applications/<application_id>/status/
```

**Access:** Employer

The employer can update applications only for their own jobs.

**Request body – JSON**

```json
{
    "status": "SHORTLISTED"
}
```

Supported application statuses:

- `PENDING`
- `REVIEWING`
- `SHORTLISTED`
- `REJECTED`
- `ACCEPTED`

Only the `status` field is accepted by the status-update serializer.

### 7.5 Download application resume

**Endpoint**

```http
GET /api/applications/<application_id>/resume/
```

**Access:**

- Employer: only applications for their own jobs.
- Admin: applications across all employers.

The endpoint returns the resume as a file attachment.

Candidates cannot use this endpoint.

---

## 8. Pagination

The reusable pagination class is `StandardResultsSetPagination`.

| Setting | Value |
|---|---|
| Default page size | 10 |
| Page parameter | `page` |
| Page-size parameter | `page_size` |
| Maximum page size | 100 |

Example:

```http
GET /api/applications/my-applications/?page=2&page_size=20
```

Paginated responses follow this structure:

```json
{
    "count": 45,
    "next": "http://127.0.0.1:8000/api/applications/my-applications/?page=2",
    "previous": null,
    "results": []
}
```

The `results` array contains the records for the requested page.

Pagination is used by:

- Employer job listing
- Admin job listing
- Public available-job listing
- Candidate's application listing
- Employer's received-application listing

---

## 9. Role-Based Access Control

Zecpath uses role-based permissions.

| Role | Main permissions |
|---|---|
| ADMIN | Administrative job listing, job management, application resume downloads |
| EMPLOYER | Manage own profile, create and manage own jobs, view received applications, update application statuses, download resumes for own jobs |
| CANDIDATE | Manage own profile, upload/download own resume, browse jobs, apply for jobs, view own applications |
| PUBLIC | Register, verify email, log in, browse active jobs and view active job details |

Authenticated role-specific endpoints also require the account to be active and email-verified.

Object ownership is checked separately from role permissions. For example, an employer cannot access another employer's job or application resume.

### RBAC testing endpoints

The following endpoints are available for access-control testing:

| Endpoint | Access |
|---|---|
| `GET /api/accounts/test/role/` | Authenticated user |
| `GET /api/accounts/test/admin/` | Admin |
| `GET /api/accounts/test/employer/` | Employer |
| `GET /api/accounts/test/candidate/` | Candidate |

These are testing endpoints, not core ATS business operations.

---

## 10. Common HTTP Status Codes

| Status | Meaning | Typical situation |
|---|---|---|
| 200 | OK | Successful retrieval, update, or action |
| 201 | Created | Successful registration, profile creation, job creation, or application |
| 400 | Bad Request | Invalid input, duplicate application, invalid token, or missing required data |
| 401 | Unauthorized | Missing, invalid, or expired authentication credentials |
| 403 | Forbidden | Authenticated user does not have the required role |
| 404 | Not Found | Resource does not exist or is outside the user's permitted scope |
| 409 | Conflict | Attempt to create a profile that is already soft-deleted |
| 500 | Internal Server Error | Unexpected server-side error |

Validation errors are generally returned as JSON containing the relevant field errors or an error message.

---

## 11. Resume and Media Security

Resume files are stored using Django's local media storage during development.

The API does not expose resume URLs through candidate or application serializers.

Resume access is handled through authenticated download endpoints:

- Candidates can download their own profile resume.
- Employers can download resumes attached to applications for their own jobs.
- Admins can download application resumes across employers.

Uploaded files are validated for extension, size, and file structure before storage.

Replacing a candidate profile resume does not replace the independent resume copies attached to existing applications.

**Production note:** Local media storage is intended for development. Production deployment should use private file storage, authenticated download access, appropriate server configuration, and secure storage credentials. The media directory must not be exposed as a public static-file directory.

---

## 12. Postman Testing

Recommended Postman collection organization:

1. Accounts
2. Employers
3. Candidates
4. Jobs
5. Applications
6. RBAC & Security
7. Error Handling

For authenticated requests, select:

**Authorization → Bearer Token**

Paste the access token into the token field.

For file uploads, select:

**Body → form-data**

Use the correct field name and select the File type. Allow Postman to generate the multipart Content-Type header.

---

## 13. Development Server

Run the development server from the project root:

```powershell
python manage.py runserver
```

Default local API base URL:

```text
http://127.0.0.1:8000
```

Use the endpoint paths and request examples in this guide to test the API through Postman.