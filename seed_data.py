"""
Seed data for AICTE APAAR ID Student Management and Verification Platform
Contains realistic student data, ABC credit records, and verification states.
"""

INITIAL_STUDENTS = [
    {
        "apaar_id": "9283-4710-8521",
        "abc_id": "ABC-2023-718290",
        "full_name": "Aarav Sharma",
        "dob": "2003-08-14",
        "gender": "Male",
        "email": "aarav.sharma@dtu.ac.in",
        "phone": "+91 98112 45678",
        "institution": "Delhi Technological University",
        "aicte_id": "1-33271891",
        "program": "B.Tech Computer Science & Engineering",
        "branch": "CSE",
        "admission_year": 2022,
        "current_semester": 6,
        "abc_credits_total": 126,
        "cgpa": 8.94,
        "kyc_status": "VERIFIED",
        "status": "Verified",
        "biometric_verified": True,
        "blood_group": "B+",
        "guardian_name": "Rajesh Sharma",
        "address": "Rohini Sector 16, New Delhi 110085",
        "photo_url": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&w=300&q=80",
        "qr_token": "APAAR-AUTH:928347108521:AICTE-1-33271891:SEC994A",
        "academic_history": [
            {"semester": 1, "credits": 22, "sgpa": 8.80, "status": "Passed"},
            {"semester": 2, "credits": 22, "sgpa": 9.10, "status": "Passed"},
            {"semester": 3, "credits": 24, "sgpa": 8.75, "status": "Passed"},
            {"semester": 4, "credits": 24, "sgpa": 9.05, "status": "Passed"},
            {"semester": 5, "credits": 24, "sgpa": 9.00, "status": "Passed"},
            {"semester": 6, "credits": 10, "sgpa": 0.00, "status": "In Progress"}
        ],
        "swayam_nptel_credits": [
            {"course": "Deep Learning by IIT Madras", "credits": 4, "certificate_id": "NPTEL23CS81"},
            {"course": "Cloud Computing by IIT Kharagpur", "credits": 3, "certificate_id": "NPTEL23CS99"}
        ],
        "compliance_notes": "All prerequisites, AICTE curriculum standards, and biometric attendance (87%) compliant."
    },
    {
        "apaar_id": "8412-9034-1187",
        "abc_id": "ABC-2023-994812",
        "full_name": "Priya Patel",
        "dob": "2004-03-22",
        "gender": "Female",
        "email": "priya.patel@vjti.ac.in",
        "phone": "+91 97234 11209",
        "institution": "Veermata Jijabai Technological Institute (VJTI Mumbai)",
        "aicte_id": "1-44910283",
        "program": "B.Tech Artificial Intelligence & Data Science",
        "branch": "AI & DS",
        "admission_year": 2023,
        "current_semester": 4,
        "abc_credits_total": 84,
        "cgpa": 9.35,
        "kyc_status": "VERIFIED",
        "status": "Verified",
        "biometric_verified": True,
        "blood_group": "O+",
        "guardian_name": "Mahesh Patel",
        "address": "Matunga, Mumbai, Maharashtra 400019",
        "photo_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80",
        "qr_token": "APAAR-AUTH:841290341187:AICTE-1-44910283:SEC771B",
        "academic_history": [
            {"semester": 1, "credits": 22, "sgpa": 9.40, "status": "Passed"},
            {"semester": 2, "credits": 22, "sgpa": 9.20, "status": "Passed"},
            {"semester": 3, "credits": 24, "sgpa": 9.45, "status": "Passed"},
            {"semester": 4, "credits": 16, "sgpa": 0.00, "status": "In Progress"}
        ],
        "swayam_nptel_credits": [
            {"course": "Data Mining by IIT Roorkee", "credits": 4, "certificate_id": "NPTEL24CS12"}
        ],
        "compliance_notes": "DigiLocker verified. ABC credits synced from National Academic Depository."
    },
    {
        "apaar_id": "7103-6629-4501",
        "abc_id": "ABC-2022-331092",
        "full_name": "Rahul Verma",
        "dob": "2002-11-05",
        "gender": "Male",
        "email": "rahul.verma@coep.ac.in",
        "phone": "+91 98201 99283",
        "institution": "College of Engineering Pune (COEP)",
        "aicte_id": "1-12093847",
        "program": "B.Tech Electronics & Telecommunication",
        "branch": "ENTC",
        "admission_year": 2022,
        "current_semester": 6,
        "abc_credits_total": 118,
        "cgpa": 8.42,
        "kyc_status": "VERIFIED",
        "status": "Verified",
        "biometric_verified": True,
        "blood_group": "A+",
        "guardian_name": "Sunil Verma",
        "address": "Shivajinagar, Pune, Maharashtra 411005",
        "photo_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&q=80",
        "qr_token": "APAAR-AUTH:710366294501:AICTE-1-12093847:SEC430C",
        "academic_history": [
            {"semester": 1, "credits": 20, "sgpa": 8.20, "status": "Passed"},
            {"semester": 2, "credits": 22, "sgpa": 8.50, "status": "Passed"},
            {"semester": 3, "credits": 24, "sgpa": 8.40, "status": "Passed"},
            {"semester": 4, "credits": 24, "sgpa": 8.60, "status": "Passed"},
            {"semester": 5, "credits": 24, "sgpa": 8.40, "status": "Passed"}
        ],
        "swayam_nptel_credits": [
            {"course": "Embedded Systems by IIT Bombay", "credits": 4, "certificate_id": "NPTEL22EE04"}
        ],
        "compliance_notes": "AICTE approved curriculum, attendance regular."
    },
    {
        "apaar_id": "6029-1144-8832",
        "abc_id": "ABC-2023-102948",
        "full_name": "Ananya Mukherjee",
        "dob": "2004-01-19",
        "gender": "Female",
        "email": "ananya.m@jadavpur.edu.in",
        "phone": "+91 94330 88291",
        "institution": "Jadavpur University Faculty of Engg",
        "aicte_id": "1-55029182",
        "program": "B.Tech Electrical Engineering",
        "branch": "EE",
        "admission_year": 2023,
        "current_semester": 4,
        "abc_credits_total": 78,
        "cgpa": 8.78,
        "kyc_status": "VERIFIED",
        "status": "Verified",
        "biometric_verified": True,
        "blood_group": "AB+",
        "guardian_name": "Debabrata Mukherjee",
        "address": "Salt Lake, Kolkata, West Bengal 700091",
        "photo_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=300&q=80",
        "qr_token": "APAAR-AUTH:602911448832:AICTE-1-55029182:SEC119D",
        "academic_history": [
            {"semester": 1, "credits": 20, "sgpa": 8.70, "status": "Passed"},
            {"semester": 2, "credits": 22, "sgpa": 8.85, "status": "Passed"},
            {"semester": 3, "credits": 24, "sgpa": 8.80, "status": "Passed"}
        ],
        "swayam_nptel_credits": [],
        "compliance_notes": "Clean audit report. Verified via State DigiLocker node."
    },
    {
        "apaar_id": "5512-3390-7764",
        "abc_id": "ABC-2021-449182",
        "full_name": "Karthik Raja",
        "dob": "2001-09-30",
        "gender": "Male",
        "email": "karthik.raja@psgtech.ac.in",
        "phone": "+91 94432 77192",
        "institution": "PSG College of Technology, Coimbatore",
        "aicte_id": "1-66720194",
        "program": "B.Tech Mechanical Engineering",
        "branch": "ME",
        "admission_year": 2021,
        "current_semester": 8,
        "abc_credits_total": 164,
        "cgpa": 8.15,
        "kyc_status": "VERIFIED",
        "status": "Graduated",
        "biometric_verified": True,
        "blood_group": "B-",
        "guardian_name": "Raja Shanmugam",
        "address": "Peelamedu, Coimbatore, Tamil Nadu 641004",
        "photo_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=300&q=80",
        "qr_token": "APAAR-AUTH:551233907764:AICTE-1-66720194:SEC820E",
        "academic_history": [
            {"semester": 1, "credits": 20, "sgpa": 8.00, "status": "Passed"},
            {"semester": 2, "credits": 20, "sgpa": 8.10, "status": "Passed"},
            {"semester": 3, "credits": 22, "sgpa": 8.20, "status": "Passed"},
            {"semester": 4, "credits": 22, "sgpa": 8.15, "status": "Passed"},
            {"semester": 5, "credits": 24, "sgpa": 8.30, "status": "Passed"},
            {"semester": 6, "credits": 24, "sgpa": 8.10, "status": "Passed"},
            {"semester": 7, "credits": 22, "sgpa": 8.25, "status": "Passed"},
            {"semester": 8, "credits": 10, "sgpa": 8.10, "status": "Passed"}
        ],
        "swayam_nptel_credits": [
            {"course": "Robotics & Automation by IIT Delhi", "credits": 4, "certificate_id": "NPTEL21ME33"}
        ],
        "compliance_notes": "Degree conferred. Final transcript uploaded to National Academic Depository."
    },
    {
        "apaar_id": "9999-0000-1111",
        "abc_id": "ABC-FLAG-990011",
        "full_name": "Vikramaditya Rao",
        "dob": "2003-05-12",
        "gender": "Male",
        "email": "v.rao.flagged@fraud-alert.gov.in",
        "phone": "+91 91100 00000",
        "institution": "Apex Institute of Advanced Tech [Disputed]",
        "aicte_id": "1-99887766",
        "program": "B.Tech Computer Science & Engineering",
        "branch": "CSE",
        "admission_year": 2023,
        "current_semester": 3,
        "abc_credits_total": 42,
        "cgpa": 6.10,
        "kyc_status": "FLAGGED",
        "status": "Flagged",
        "biometric_verified": False,
        "blood_group": "O-",
        "guardian_name": "K. Rao",
        "address": "Sector 4, Noida, UP 201301",
        "photo_url": "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?auto=format&fit=crop&w=300&q=80",
        "qr_token": "APAAR-FLAG:DUAL_ENROLLMENT_ALERT:999900001111",
        "academic_history": [
            {"semester": 1, "credits": 20, "sgpa": 6.20, "status": "Passed"}
        ],
        "swayam_nptel_credits": [],
        "compliance_notes": "CRITICAL ALERT: Student APAAR ID found actively enrolled concurrently in 2 separate institutes (Institute ID 1-99887766 and 1-33291044). Academic fraud investigation pending."
    },
    {
        "apaar_id": "3192-8840-5261",
        "abc_id": "ABC-2024-118839",
        "full_name": "Sneha R. Kulkarni",
        "dob": "2005-06-18",
        "gender": "Female",
        "email": "sneha.kulkarni@mitpune.edu.in",
        "phone": "+91 97654 32190",
        "institution": "Maharashtra Institute of Technology (MIT-WPU)",
        "aicte_id": "1-77881920",
        "program": "B.Tech Cyber Security",
        "branch": "Cyber Security",
        "admission_year": 2024,
        "current_semester": 2,
        "abc_credits_total": 24,
        "cgpa": 9.10,
        "kyc_status": "VERIFIED",
        "status": "Verified",
        "biometric_verified": True,
        "blood_group": "B+",
        "guardian_name": "Ramesh Kulkarni",
        "address": "Kothrud, Pune, Maharashtra 411038",
        "photo_url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=300&q=80",
        "qr_token": "APAAR-AUTH:319288405261:AICTE-1-77881920:SEC310F",
        "academic_history": [
            {"semester": 1, "credits": 24, "sgpa": 9.10, "status": "Passed"}
        ],
        "swayam_nptel_credits": [],
        "compliance_notes": "First year verified via AICTE centralized counseling."
    }
]

INSTITUTIONS = [
    {
        "aicte_id": "1-33271891",
        "name": "Delhi Technological University",
        "state": "Delhi",
        "status": "AICTE Approved - Tier 1",
        "total_enrolled": 4820,
        "compliance_score": 98.4
    },
    {
        "aicte_id": "1-44910283",
        "name": "Veermata Jijabai Technological Institute (VJTI)",
        "state": "Maharashtra",
        "status": "AICTE Approved - Tier 1",
        "total_enrolled": 3950,
        "compliance_score": 99.1
    },
    {
        "aicte_id": "1-12093847",
        "name": "College of Engineering Pune (COEP)",
        "state": "Maharashtra",
        "status": "AICTE Approved - Tier 1",
        "total_enrolled": 4100,
        "compliance_score": 97.8
    },
    {
        "aicte_id": "1-55029182",
        "name": "Jadavpur University Faculty of Engg",
        "state": "West Bengal",
        "status": "AICTE Approved - Tier 1",
        "total_enrolled": 3400,
        "compliance_score": 96.5
    },
    {
        "aicte_id": "1-66720194",
        "name": "PSG College of Technology",
        "state": "Tamil Nadu",
        "status": "AICTE Approved - Autonomous",
        "total_enrolled": 5200,
        "compliance_score": 98.9
    }
]


# Multi-Level Verification Workflow Initial Applications
WORKFLOW_APPLICATIONS = [
    {
        "workflow_id": "WF-2026-101",
        "apaar_id": "9123-5544-7788",
        "abc_id": "ABC-2024-554411",
        "full_name": "Rohan Saxena",
        "dob": "2004-05-18",
        "gender": "Male",
        "email": "rohan.saxena@dtu.ac.in",
        "phone": "+91 98101 22334",
        "institution": "Delhi Technological University",
        "aicte_id": "1-33271891",
        "program": "B.Tech Computer Science & Engineering",
        "branch": "CSE",
        "admission_year": 2024,
        "current_semester": 2,
        "abc_credits_total": 24,
        "cgpa": 8.70,
        "status": "SUBMITTED", # SUBMITTED | INSTITUTION_APPROVED | FLAGGED_REVIEW | REJECTED_WITH_REMARKS | AICTE_FINAL_APPROVED
        "submitted_by": "Ramesh Patel (College Operator)",
        "submitted_at": "2026-10-24T10:30:00Z",
        "assigned_to": "Dr. Pradeep Kumar (Institution Verifier)",
        "rejection_remarks": None,
        "flag_notes": None,
        "audit_history": [
            {
                "timestamp": "2026-10-24T10:30:00Z",
                "actor_name": "Ramesh Patel",
                "actor_role": "COLLEGE_OPERATOR",
                "action": "SUBMIT_RECORD",
                "remarks": "Initial student enrollment submission with 10th/12th marksheets & DigiLocker e-KYC.",
                "prev_status": "DRAFT",
                "new_status": "SUBMITTED"
            }
        ]
    },
    {
        "workflow_id": "WF-2026-102",
        "apaar_id": "8901-2233-4455",
        "abc_id": "ABC-2023-890122",
        "full_name": "Meera Iyer",
        "dob": "2003-12-04",
        "gender": "Female",
        "email": "meera.iyer@dtu.ac.in",
        "phone": "+91 98402 11982",
        "institution": "Delhi Technological University",
        "aicte_id": "1-33271891",
        "program": "B.Tech Artificial Intelligence & Data Science",
        "branch": "AI & DS",
        "admission_year": 2023,
        "current_semester": 4,
        "abc_credits_total": 82,
        "cgpa": 9.20,
        "status": "INSTITUTION_APPROVED",
        "submitted_by": "Ramesh Patel (College Operator)",
        "submitted_at": "2026-10-23T14:15:00Z",
        "assigned_to": "AICTE Central Admin Bureau",
        "rejection_remarks": None,
        "flag_notes": None,
        "audit_history": [
            {
                "timestamp": "2026-10-23T14:15:00Z",
                "actor_name": "Ramesh Patel",
                "actor_role": "COLLEGE_OPERATOR",
                "action": "SUBMIT_RECORD",
                "remarks": "Submitted for institution verification.",
                "prev_status": "DRAFT",
                "new_status": "SUBMITTED"
            },
            {
                "timestamp": "2026-10-24T09:45:00Z",
                "actor_name": "Dr. Pradeep Kumar",
                "actor_role": "INSTITUTION_VERIFIER",
                "action": "INSTITUTION_APPROVE",
                "remarks": "Academic credentials, 4 semesters SGPA, and ABC credit ledger verified against DTU ERP.",
                "prev_status": "SUBMITTED",
                "new_status": "INSTITUTION_APPROVED"
            }
        ]
    },
    {
        "workflow_id": "WF-2026-103",
        "apaar_id": "9999-4455-6677",
        "abc_id": "ABC-FLAG-994455",
        "full_name": "Kunal Singhania",
        "dob": "2003-07-29",
        "gender": "Male",
        "email": "kunal.s@vjti.ac.in",
        "phone": "+91 97110 33445",
        "institution": "Veermata Jijabai Technological Institute (VJTI)",
        "aicte_id": "1-44910283",
        "program": "B.Tech Mechanical Engineering",
        "branch": "ME",
        "admission_year": 2023,
        "current_semester": 3,
        "abc_credits_total": 44,
        "cgpa": 7.40,
        "status": "FLAGGED_REVIEW",
        "submitted_by": "Anil Deshpande (Operator, VJTI)",
        "submitted_at": "2026-10-22T11:00:00Z",
        "assigned_to": "Smt. Sunita Rao (Authorized Reviewer)",
        "rejection_remarks": None,
        "flag_notes": "SUSPICIOUS DUAL SEAT: APAAR ID flagged with matching Aadhaar biometric hash in Pune University affiliate.",
        "audit_history": [
            {
                "timestamp": "2026-10-22T11:00:00Z",
                "actor_name": "Anil Deshpande",
                "actor_role": "COLLEGE_OPERATOR",
                "action": "SUBMIT_RECORD",
                "remarks": "Submitted student record.",
                "prev_status": "DRAFT",
                "new_status": "SUBMITTED"
            },
            {
                "timestamp": "2026-10-23T16:20:00Z",
                "actor_name": "Prof. S. K. Mahajan",
                "actor_role": "INSTITUTION_VERIFIER",
                "action": "FLAG_FOR_REVIEW",
                "remarks": "Automated cross-check detected concurrent enrollment in another institute. Escalating to AICTE Reviewer.",
                "prev_status": "SUBMITTED",
                "new_status": "FLAGGED_REVIEW"
            }
        ]
    },
    {
        "workflow_id": "WF-2026-104",
        "apaar_id": "7712-3344-9900",
        "abc_id": "ABC-2024-771233",
        "full_name": "Tanvi Deshmukh",
        "dob": "2005-02-14",
        "gender": "Female",
        "email": "tanvi.d@coep.ac.in",
        "phone": "+91 98220 99881",
        "institution": "College of Engineering Pune (COEP)",
        "aicte_id": "1-12093847",
        "program": "B.Tech Electronics & Telecommunication",
        "branch": "ENTC",
        "admission_year": 2024,
        "current_semester": 1,
        "abc_credits_total": 0,
        "cgpa": 0.0,
        "status": "REJECTED_WITH_REMARKS",
        "submitted_by": "Sachin Kadam (Operator, COEP)",
        "submitted_at": "2026-10-21T09:10:00Z",
        "assigned_to": "Sachin Kadam (College Operator)",
        "rejection_remarks": "DigiLocker 12th Certificate document missing digital signature. ABC ID checksum mismatch (ABC-2024-771233 not found on NAD portal). Please verify and resubmit.",
        "flag_notes": None,
        "audit_history": [
            {
                "timestamp": "2026-10-21T09:10:00Z",
                "actor_name": "Sachin Kadam",
                "actor_role": "COLLEGE_OPERATOR",
                "action": "SUBMIT_RECORD",
                "remarks": "Initial upload.",
                "prev_status": "DRAFT",
                "new_status": "SUBMITTED"
            },
            {
                "timestamp": "2026-10-22T13:40:00Z",
                "actor_name": "Dr. V. N. Pande",
                "actor_role": "INSTITUTION_VERIFIER",
                "action": "REJECT_WITH_REMARKS",
                "remarks": "DigiLocker 12th Certificate document missing digital signature. ABC ID checksum mismatch. Returned to operator for correction.",
                "prev_status": "SUBMITTED",
                "new_status": "REJECTED_WITH_REMARKS"
            }
        ]
    },
    {
        "workflow_id": "WF-2026-105",
        "apaar_id": "9283-4710-8521",
        "abc_id": "ABC-2023-718290",
        "full_name": "Aarav Sharma",
        "dob": "2003-08-14",
        "gender": "Male",
        "email": "aarav.sharma@dtu.ac.in",
        "phone": "+91 98112 45678",
        "institution": "Delhi Technological University",
        "aicte_id": "1-33271891",
        "program": "B.Tech Computer Science & Engineering",
        "branch": "CSE",
        "admission_year": 2022,
        "current_semester": 6,
        "abc_credits_total": 126,
        "cgpa": 8.94,
        "status": "AICTE_FINAL_APPROVED",
        "submitted_by": "Ramesh Patel (College Operator)",
        "submitted_at": "2026-10-15T10:00:00Z",
        "assigned_to": "Completed (National Registry Active)",
        "rejection_remarks": None,
        "flag_notes": None,
        "audit_history": [
            {
                "timestamp": "2026-10-15T10:00:00Z",
                "actor_name": "Ramesh Patel",
                "actor_role": "COLLEGE_OPERATOR",
                "action": "SUBMIT_RECORD",
                "remarks": "Cohort upload.",
                "prev_status": "DRAFT",
                "new_status": "SUBMITTED"
            },
            {
                "timestamp": "2026-10-16T11:20:00Z",
                "actor_name": "Dr. Pradeep Kumar",
                "actor_role": "INSTITUTION_VERIFIER",
                "action": "INSTITUTION_APPROVE",
                "remarks": "Institution verification completed.",
                "prev_status": "SUBMITTED",
                "new_status": "INSTITUTION_APPROVED"
            },
            {
                "timestamp": "2026-10-18T15:00:00Z",
                "actor_name": "Prof. T. G. Sitharam",
                "actor_role": "AICTE_ADMIN",
                "action": "AICTE_FINAL_APPROVE",
                "remarks": "AICTE central cryptographic token granted. Student active on APAAR Scanner.",
                "prev_status": "INSTITUTION_APPROVED",
                "new_status": "AICTE_FINAL_APPROVED"
            }
        ]
    }
]

# Notifications for Authority Roles
INITIAL_NOTIFICATIONS = [
    {
        "id": "NOTIF-1",
        "recipient_role": "INSTITUTION_VERIFIER",
        "institution": "Delhi Technological University",
        "title": "New Student Application Pending Verification",
        "message": "Operator Ramesh Patel submitted Rohan Saxena (APAAR: 9123-5544-7788) for verification.",
        "timestamp": "2026-10-24T10:30:00Z",
        "workflow_id": "WF-2026-101",
        "read": False
    },
    {
        "id": "NOTIF-2",
        "recipient_role": "AUTHORIZED_REVIEWER",
        "institution": "All",
        "title": "Escalated Fraud / Disputed Case",
        "message": "Kunal Singhania (WF-2026-103) flagged for suspected dual-enrollment at VJTI Mumbai.",
        "timestamp": "2026-10-23T16:20:00Z",
        "workflow_id": "WF-2026-103",
        "read": False
    },
    {
        "id": "NOTIF-3",
        "recipient_role": "COLLEGE_OPERATOR",
        "institution": "College of Engineering Pune (COEP)",
        "title": "Record Returned with Correction Remarks",
        "message": "Tanvi Deshmukh (WF-2026-104) returned: Missing digital signature on 12th marksheet.",
        "timestamp": "2026-10-22T13:40:00Z",
        "workflow_id": "WF-2026-104",
        "read": False
    },
    {
        "id": "NOTIF-4",
        "recipient_role": "AICTE_ADMIN",
        "institution": "All",
        "title": "Final Approval Queue",
        "message": "Meera Iyer (DTU - AI&DS) approved by institution, awaiting AICTE national registry seal.",
        "timestamp": "2026-10-24T09:45:00Z",
        "workflow_id": "WF-2026-102",
        "read": False
    }
]

# SIH Demo Friendly "Dirty Dataset" for AI-Powered Data Quality Assistant
DIRTY_BATCH_DATA = [
    {
        "id": "DIRTY-01",
        "raw_apaar_id": "9283-471-852", # Format error: 11 digits instead of 12
        "raw_full_name": "  aARAV   sHARMA ", # Formatting & casing issue
        "raw_institution": "Deli Tech Univ", # Common typo
        "raw_branch": "Comp Sci Engg", # Non-standard branch name
        "raw_email": "aarav.sharma@@dtu..ac.in", # Malformed email
        "raw_phone": "9811245678", # Missing country code
        "raw_cgpa": 11.2, # Out of bounds (scale of 10.0)
        "raw_abc_id": "ABC2023718290", # Missing hyphens
        "department": "Computer Science",
        "batch": "2022-2026"
    },
    {
        "id": "DIRTY-02",
        "raw_apaar_id": "8412-9034-1187",
        "raw_full_name": "Priya Patel",
        "raw_institution": "VJIT Mumbai", # Typo: VJTI spelled as VJIT
        "raw_branch": "Artificial Intel", # Non-standard branch
        "raw_email": "priya.patel@vjti.ac.in",
        "raw_phone": "+91 97234 11209",
        "raw_cgpa": 9.35,
        "raw_abc_id": "", # Missing mandatory field
        "department": "Artificial Intelligence",
        "batch": "2023-2027"
    },
    {
        "id": "DIRTY-03",
        "raw_apaar_id": "7103-6629-XXXX", # Masked / incomplete characters
        "raw_full_name": "Rahul", # Incomplete name (no surname)
        "raw_institution": "College of Engineering Pune (COEP)",
        "raw_branch": "ENTC",
        "raw_email": "rahul.verma@coep.ac.in",
        "raw_phone": "+91 98201 99283",
        "raw_cgpa": -1.5, # Negative CGPA
        "raw_abc_id": "ABC-2022-331092",
        "department": "Electronics",
        "batch": "2022-2026"
    },
    {
        "id": "DIRTY-04",
        "raw_apaar_id": "6029-1144-8832",
        "raw_full_name": "Ananya Mukherjee",
        "raw_institution": "Jadavpur Univ", # Abbreviation
        "raw_branch": "EE",
        "raw_email": "ananya.m@jadavpur.edu.in",
        "raw_phone": "0000000000", # Dummy phone number
        "raw_cgpa": 8.78,
        "raw_abc_id": "ABC-2023-102948",
        "department": "Electrical Engineering",
        "batch": "2023-2027"
    },
    {
        "id": "DIRTY-05",
        "raw_apaar_id": "5512-3390-7764",
        "raw_full_name": "Karthik Raja",
        "raw_institution": "PSG Tech", # Abbreviation
        "raw_branch": "Mechanical",
        "raw_email": "karthik.raja@psgtech.ac.in",
        "raw_phone": "+91 94432 77192",
        "raw_cgpa": 8.15,
        "raw_abc_id": "ABC-2021-449182",
        "department": "Mechanical Engineering",
        "batch": "2021-2025"
    }
]

# Authority User Accounts for Role-Based Login
AUTHORITY_USERS = [
    {
        "id": "USR-OP-01",
        "name": "Ramesh Patel",
        "email": "operator@dtu.ac.in",
        "password": "operator123",
        "role": "COLLEGE_OPERATOR",
        "role_title": "College Data Operator",
        "institution": "Delhi Technological University",
        "permissions": ["SUBMIT_STUDENT", "EDIT_REJECTED", "VIEW_COLLEGE_ROSTER"]
    },
    {
        "id": "USR-VER-02",
        "name": "Dr. Pradeep Kumar",
        "email": "verifier@dtu.ac.in",
        "password": "verifier123",
        "role": "INSTITUTION_VERIFIER",
        "role_title": "Institution Verifier & Dean Academics",
        "institution": "Delhi Technological University",
        "permissions": ["VERIFY_RECORDS", "APPROVE_INSTITUTION", "FLAG_RECORD", "REJECT_WITH_REMARKS"]
    },
    {
        "id": "USR-REV-03",
        "name": "Smt. Sunita Rao",
        "email": "reviewer@aicte.gov.in",
        "password": "reviewer123",
        "role": "AUTHORIZED_REVIEWER",
        "role_title": "Authorized Reviewer (Grievance & Fraud Cell)",
        "institution": "AICTE National Review Bureau",
        "permissions": ["RESOLVE_FLAGS", "INVESTIGATE_DUAL_SEATS", "CLEAR_REVIEW", "CONFIRM_FRAUD"]
    },
    {
        "id": "USR-ADM-04",
        "name": "Prof. T. G. Sitharam",
        "email": "admin@aicte.gov.in",
        "password": "admin123",
        "role": "AICTE_ADMIN",
        "role_title": "AICTE Central Administrator & Chairman",
        "institution": "All India Council for Technical Education (HQ)",
        "permissions": ["ALL_PERMISSIONS", "FINAL_APPROVE", "OVERRIDE", "NATIONAL_AUDIT"]
    }
]
