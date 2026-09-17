# Sample Input & Output

## Test Scenario 1: Upload Question Paper

### User Input:
```
Role: Question Setter
Username: qs1
Password: password123

Upload Form:
  Title: Mathematics Final Examination
  Subject: Mathematics
  Exam Date & Time: 2026-10-15 14:00:00
  File: mathematics_final_2026.pdf (5.2 MB)
```

### Application Processing:
```
1. User authenticated ✓
2. File received: 5,242,880 bytes
3. Encryption started: AES-256
4. Generating hash: SHA-256
   Hash: a7f3e2d1b5c9f4g6h8i0j2k4l6m8n0o2p4q6r8s0
5. Storing encrypted content in database
6. Creating audit log entry
7. File successfully encrypted and stored
```

### System Response:
```json
{
  "status": "success",
  "message": "Question paper uploaded successfully",
  "paper_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Mathematics Final Examination",
  "status": "draft",
  "created_at": "2026-09-17T10:30:45Z",
  "redirect": "/dashboard"
}
```

### Audit Log Entry:
```
Timestamp: 2026-09-17 10:30:45
User: qs1
Action: qpaper_upload
Resource: question_paper:550e8400-e29b-41d4-a716-446655440000
Status: success
IP Address: 192.168.1.100
```

---

## Test Scenario 2: Reviewer Approves Paper

### User Input:
```
Role: Reviewer
Username: reviewer1
Password: password123

Action: Click "Approve" button on Mathematics paper
```

### Application Processing:
```
1. User authenticated as reviewer ✓
2. Check user role: reviewer ✓
3. Check permission: can approve papers ✓
4. Load question paper: 550e8400-e29b-41d4-a716-446655440000
5. Verify status: draft → can approve ✓
6. Update status: draft → approved
7. Update database
8. Create audit log entry
9. Response sent to user
```

### System Response:
```json
{
  "status": 200,
  "message": "Question paper approved successfully",
  "paper_id": "550e8400-e29b-41d4-a716-446655440000",
  "new_status": "approved",
  "approved_by": "reviewer1",
  "approved_at": "2026-09-17T11:15:30Z"
}
```

### Audit Log Entry:
```
Timestamp: 2026-09-17 11:15:30
User: reviewer1
Action: qpaper_approved
Resource: question_paper:550e8400-e29b-41d4-a716-446655440000
Status: success
IP Address: 192.168.1.102
```

---

## Test Scenario 3: Exam Officer Releases Paper

### User Input:
```
Role: Exam Officer
Username: officer1
Password: password123

Action: Click "Release" button on approved Mathematics paper
```

### Application Processing:
```
1. User authenticated as exam_officer ✓
2. Check user role: exam_officer ✓
3. Check permission: can release papers ✓
4. Load question paper: 550e8400-e29b-41d4-a716-446655440000
5. Verify status: approved → can release ✓
6. Update status: approved → released
7. Set is_released: true
8. Set released_at: 2026-09-17T11:20:00Z
9. Update database
10. Create audit log entry
11. Trigger secure distribution mechanism
```

### System Response:
```json
{
  "status": 200,
  "message": "Question paper released successfully",
  "paper_id": "550e8400-e29b-41d4-a716-446655440000",
  "new_status": "released",
  "released_by": "officer1",
  "released_at": "2026-09-17T11:20:00Z"
}
```

### Audit Log Entry:
```
Timestamp: 2026-09-17 11:20:00
User: officer1
Action: qpaper_released
Resource: question_paper:550e8400-e29b-41d4-a716-446655440000
Status: success
IP Address: 192.168.1.105
```

---

## Test Scenario 4: User Tries to Access Before Exam Time

### User Input:
```
Role: Any user
Action: Click "View" button on Mathematics paper
Exam Time: 2026-10-15 14:00:00
Current Time: 2026-10-15 13:45:00 (15 minutes before exam)
```

### Application Processing:
```
1. User authenticated ✓
2. Check user role and permissions ✓
3. Load question paper: 550e8400-e29b-41d4-a716-446655440000
4. Check time constraint:
   - Exam time: 2026-10-15 14:00:00
   - Current time: 2026-10-15 13:45:00
   - Time remaining: 15 minutes
   - Paper NOT released yet: false
5. TIME CHECK FAILED ❌
6. Access denied - create audit log
7. Return error response
```

### System Response:
```json
{
  "status": 403,
  "error": "Question paper cannot be accessed before exam date",
  "message": "Access will be available on 2026-10-15 at 14:00:00",
  "time_remaining_minutes": 15
}
```

### Audit Log Entry:
```
Timestamp: 2026-10-15 13:45:00
User: qs1
Action: premature_qpaper_access_attempt
Resource: question_paper:550e8400-e29b-41d4-a716-446655440000
Status: failure
IP Address: 192.168.1.100
Details: "Attempted access 15 minutes before exam time"
```

---

## Test Scenario 5: User Tries to Access After Exam Time

### User Input:
```
Role: Any authorized user
Action: Click "View" button on released Mathematics paper
Exam Time: 2026-10-15 14:00:00
Current Time: 2026-10-15 15:30:00 (1.5 hours after exam start)
```

### Application Processing:
```
1. User authenticated ✓
2. Check user role and permissions ✓
3. Load question paper: 550e8400-e29b-41d4-a716-446655440000
4. Check time constraint:
   - Exam time: 2026-10-15 14:00:00
   - Current time: 2026-10-15 15:30:00
   - Time check: PASSED ✓
5. Check paper status: released ✓
6. Load encrypted content
7. Get encryption key
8. Decrypt using Fernet (AES-256)
9. Generate current file hash: SHA-256
10. Compare hashes:
    Original: a7f3e2d1b5c9f4g6h8i0j2k4l6m8n0o2p4q6r8s0
    Current:  a7f3e2d1b5c9f4g6h8i0j2k4l6m8n0o2p4q6r8s0
    Match: YES ✓ (File integrity verified)
11. Create audit log entry
12. Send decrypted file to user
```

### System Response:
```
HTTP/1.1 200 OK
Content-Type: application/pdf
Content-Disposition: attachment; filename="Mathematics_Final_Examination.pdf"
Content-Length: 5242880

[Binary PDF content - decrypted and streamed to client]
```

### Audit Log Entry:
```
Timestamp: 2026-10-15 15:30:00
User: officer1
Action: qpaper_view
Resource: question_paper:550e8400-e29b-41d4-a716-446655440000
Status: success
IP Address: 192.168.1.105
Details: "File integrity verified - hash match successful"
```

---

## Test Scenario 6: Unauthorized Access Attempt

### User Input:
```
Role: Exam Officer (officer1)
Action: Try to approve a question paper (reviewer role only)
Paper ID: 550e8400-e29b-41d4-a716-446655440000
```

### Application Processing:
```
1. User authenticated as officer1 ✓
2. Check route permission: @require_role('reviewer')
3. User role: exam_officer
4. Check: exam_officer == reviewer? NO ❌
5. Access denied - log unauthorized attempt
6. Return 403 Forbidden response
```

### System Response:
```json
{
  "status": 403,
  "error": "Insufficient permissions",
  "message": "This action requires reviewer role",
  "required_role": "reviewer",
  "user_role": "exam_officer"
}
```

### Audit Log Entry:
```
Timestamp: 2026-09-17 12:00:00
User: officer1
Action: unauthorized_role_access
Resource: question_paper:550e8400-e29b-41d4-a716-446655440000
Status: failure
IP Address: 192.168.1.105
Details: "User tried to approve paper without reviewer role"
```

---

## Test Scenario 7: Admin Views Audit Logs

### User Input:
```
Role: Admin
Username: admin
Password: admin@123

Action: Click "Audit Logs" in navigation
```

### Application Processing:
```
1. User authenticated as admin ✓
2. Check user role: admin ✓
3. Query audit logs (last 100 entries)
4. Order by timestamp DESC
5. Format for display
6. Load user information for each log
7. Render HTML page
```

### System Response (Partial Audit Log Table):
```
┌─────────────────────┬──────────┬─────────────────────┬──────────────────────┬───────────┐
│ Timestamp           │ User     │ Action              │ Resource             │ Status    │
├─────────────────────┼──────────┼─────────────────────┼──────────────────────┼───────────┤
│ 2026-09-17 15:30:00 │ officer1 │ qpaper_view         │ question_paper:550.. │ ✓ success │
│ 2026-09-17 15:20:00 │ officer1 │ qpaper_released     │ question_paper:550.. │ ✓ success │
│ 2026-09-17 15:15:00 │ reviewer1│ qpaper_approved     │ question_paper:550.. │ ✓ success │
│ 2026-09-17 15:00:00 │ qs1      │ qpaper_upload       │ question_paper:550.. │ ✓ success │
│ 2026-09-17 13:45:00 │ qs1      │ premature_access..  │ question_paper:550.. │ ✗ failure │
│ 2026-09-17 10:30:00 │ qs1      │ user_login          │ auth                 │ ✓ success │
└─────────────────────┴──────────┴─────────────────────┴──────────────────────┴───────────┘
```

---

## Dashboard Display Examples

### Question Setter's Dashboard:
```
Question Papers
───────────────────────────────────────────────────────────────────
Title                  Subject      Created              Status   Actions
───────────────────────────────────────────────────────────────────
Mathematics Final      Mathematics  2026-09-17 10:30    DRAFT    [View]
Physics Midterm        Physics      2026-09-16 14:20    APPROVED [View]
Chemistry Practical    Chemistry    2026-09-15 09:00    RELEASED [View]
───────────────────────────────────────────────────────────────────
```

### Reviewer's Dashboard:
```
Question Papers (Reviewable)
───────────────────────────────────────────────────────────────────
Title                  Subject      Exam Date        Status   Actions
───────────────────────────────────────────────────────────────────
Mathematics Final      Mathematics  2026-10-15       DRAFT    [Approve]
English Essay          English      2026-10-18       DRAFT    [Approve]
History Essay          History      2026-10-20       DRAFT    [Approve]
───────────────────────────────────────────────────────────────────
```

### Exam Officer's Dashboard:
```
Question Papers (Ready for Release)
───────────────────────────────────────────────────────────────────
Title                  Subject      Exam Date        Status    Actions
───────────────────────────────────────────────────────────────────
Physics Midterm        Physics      2026-09-18       APPROVED  [Release]
Chemistry Lab          Chemistry    2026-09-20       APPROVED  [Release]
Biology Practicals     Biology      2026-09-25       RELEASED  [View]
───────────────────────────────────────────────────────────────────
```

---

## Error Response Examples

### Invalid Login:
```json
{
  "status": 401,
  "error": "Invalid credentials",
  "message": "Username or password is incorrect"
}
```

### Question Paper Not Found:
```json
{
  "status": 404,
  "error": "Question paper not found",
  "message": "The requested question paper does not exist"
}
```

### Integrity Verification Failed:
```json
{
  "status": 403,
  "error": "Integrity verification failed - file may have been tampered",
  "message": "The question paper hash does not match. File integrity cannot be verified."
}
```

### Database Error:
```json
{
  "status": 500,
  "error": "Internal server error",
  "message": "An unexpected error occurred. Please try again later."
}
```

---

## API Response Examples

### Upload Endpoint Response:
```
POST /upload
Content-Type: multipart/form-data

Response:
HTTP/1.1 302 Found
Location: /dashboard
Set-Cookie: session=...

[Redirect to dashboard with success message]
```

### Approve Endpoint Response:
```
POST /qpaper/550e8400-e29b-41d4-a716-446655440000/approve

Response:
HTTP/1.1 200 OK
Content-Type: application/json

{
  "message": "Question paper approved"
}
```

### Release Endpoint Response:
```
POST /qpaper/550e8400-e29b-41d4-a716-446655440000/release

Response:
HTTP/1.1 200 OK
Content-Type: application/json

{
  "message": "Question paper released"
}
```

### View Endpoint Response:
```
GET /qpaper/550e8400-e29b-41d4-a716-446655440000/view

Response:
HTTP/1.1 200 OK
Content-Type: application/pdf
Content-Disposition: attachment; filename="Mathematics_Final_Examination.pdf"
Content-Length: 5242880

[Binary PDF content]
```

---

## Database Records Created

### User Table Entry:
```sql
INSERT INTO user (username, email, password, role, is_active, created_at)
VALUES ('qs1', 'qs1@example.com', 'pbkdf2:sha256:...', 'question_setter', true, '2026-09-17 10:00:00');
```

### Question Paper Table Entry:
```sql
INSERT INTO question_paper (
  id, title, subject, encrypted_content, file_hash, created_by, 
  created_at, exam_date, is_released, status, encryption_key
)
VALUES (
  '550e8400-e29b-41d4-a716-446655440000',
  'Mathematics Final Examination',
  'Mathematics',
  [encrypted blob data],
  'a7f3e2d1b5c9f4g6h8i0j2k4l6m8n0o2p4q6r8s0',
  1,
  '2026-09-17 10:30:45',
  '2026-10-15 14:00:00',
  false,
  'draft',
  'gAAAAABl9p...[encrypted key]'
);
```

### Audit Log Table Entry:
```sql
INSERT INTO audit_log (user_id, action, resource_type, resource_id, details, timestamp, ip_address, status)
VALUES (
  1,
  'qpaper_upload',
  'question_paper',
  '550e8400-e29b-41d4-a716-446655440000',
  'Uploaded Mathematics_Final_Examination.pdf (5.2 MB)',
  '2026-09-17 10:30:45',
  '192.168.1.100',
  'success'
);
```

---

## Performance & Security Metrics

### Encryption Performance:
- File size: 5 MB
- Encryption time: ~200ms
- Hash generation time: ~50ms
- Total processing time: ~250ms

### Database Performance:
- Query response time: <50ms
- Insert audit log: <10ms
- Login validation: <20ms

### Security Verification:
- AES-256: ✓ 256-bit symmetric encryption
- SHA-256: ✓ 256-bit cryptographic hash
- Password hashing: ✓ PBKDF2 with Werkzeug
- Session security: ✓ HttpOnly, Secure cookies
- HTTPS ready: ✓ TLS/HTTPS support

