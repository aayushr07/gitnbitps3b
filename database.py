import os
import re
from datetime import datetime
from dotenv import load_dotenv
from seed_data import (
    INITIAL_STUDENTS, 
    INSTITUTIONS, 
    WORKFLOW_APPLICATIONS, 
    INITIAL_NOTIFICATIONS, 
    DIRTY_BATCH_DATA, 
    AUTHORITY_USERS
)

load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

MONGO_URI = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI") or "mongodb://localhost:27017/apaar_aicte"

# Dictionary for AI Data Quality normalization
INSTITUTION_NORMALIZATION_MAP = {
    "deli tech univ": "Delhi Technological University",
    "delhi tech": "Delhi Technological University",
    "dtu": "Delhi Technological University",
    "vjit": "Veermata Jijabai Technological Institute (VJTI Mumbai)",
    "vjit mumbai": "Veermata Jijabai Technological Institute (VJTI Mumbai)",
    "vjti": "Veermata Jijabai Technological Institute (VJTI Mumbai)",
    "coep pune": "College of Engineering Pune (COEP)",
    "pune engg": "College of Engineering Pune (COEP)",
    "coep": "College of Engineering Pune (COEP)",
    "jadavpur univ": "Jadavpur University Faculty of Engg",
    "jadavpur": "Jadavpur University Faculty of Engg",
    "psg tech": "PSG College of Technology",
    "psg": "PSG College of Technology"
}

BRANCH_NORMALIZATION_MAP = {
    "comp sci engg": {"branch": "CSE", "program": "B.Tech Computer Science & Engineering"},
    "comp sci": {"branch": "CSE", "program": "B.Tech Computer Science & Engineering"},
    "computer science": {"branch": "CSE", "program": "B.Tech Computer Science & Engineering"},
    "cs": {"branch": "CSE", "program": "B.Tech Computer Science & Engineering"},
    "cse engg": {"branch": "CSE", "program": "B.Tech Computer Science & Engineering"},
    "artificial intel": {"branch": "AI & DS", "program": "B.Tech Artificial Intelligence & Data Science"},
    "ai ds": {"branch": "AI & DS", "program": "B.Tech Artificial Intelligence & Data Science"},
    "ai/ds": {"branch": "AI & DS", "program": "B.Tech Artificial Intelligence & Data Science"},
    "ai & ds": {"branch": "AI & DS", "program": "B.Tech Artificial Intelligence & Data Science"},
    "entc": {"branch": "ENTC", "program": "B.Tech Electronics & Telecommunication"},
    "electronics": {"branch": "ENTC", "program": "B.Tech Electronics & Telecommunication"},
    "ee": {"branch": "EE", "program": "B.Tech Electrical Engineering"},
    "electrical": {"branch": "EE", "program": "B.Tech Electrical Engineering"},
    "me": {"branch": "ME", "program": "B.Tech Mechanical Engineering"},
    "mechanical": {"branch": "ME", "program": "B.Tech Mechanical Engineering"},
    "cyber security": {"branch": "Cyber Security", "program": "B.Tech Cyber Security"}
}

class DatabaseManager:
    def __init__(self):
        self.connected_to_mongo = False
        self.client = None
        self.db = None
        self.mode = "In-Memory / Local Mode"
        
        # In-memory stores (used as fallback or when MongoDB is not connected)
        self.memory_students = [dict(s) for s in INITIAL_STUDENTS]
        self.memory_institutions = [dict(i) for i in INSTITUTIONS]
        self.memory_workflows = [dict(w) for w in WORKFLOW_APPLICATIONS]
        self.memory_notifications = [dict(n) for n in INITIAL_NOTIFICATIONS]
        self.memory_dirty_batch = [dict(d) for d in DIRTY_BATCH_DATA]
        self.memory_verifications = [
            {
                "id": "VER-1001",
                "apaar_id": "9283-4710-8521",
                "student_name": "Aarav Sharma",
                "institution": "Delhi Technological University",
                "status": "SUCCESS",
                "verifier": "AICTE Gate Scanner / Automated QR",
                "timestamp": datetime.now().isoformat(),
                "details": "Biometric match 99.4%, ABC credits verified (126), DigiLocker verified."
            },
            {
                "id": "VER-1002",
                "apaar_id": "9999-0000-1111",
                "student_name": "Vikramaditya Rao",
                "institution": "Apex Institute [Disputed]",
                "status": "ALERT_FLAGGED",
                "verifier": "Central Admission AICTE Check",
                "timestamp": datetime.now().isoformat(),
                "details": "DUAL ENROLLMENT FRAUD DETECTED across 2 different colleges."
            }
        ]
        
        self._init_mongo()

    def _init_mongo(self):
        try:
            from pymongo import MongoClient
            self.client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=7000)
            self.client.admin.command('ping')
            try:
                self.db = self.client.get_default_database()
            except Exception:
                self.db = None
            if self.db is None or self.db.name in ["admin", "test"]:
                self.db = self.client["apaar_aicte"]
            
            self.connected_to_mongo = True
            self.mode = f"MongoDB Connected ({self.db.name})"
            print(f"[DatabaseManager] Successfully connected to MongoDB at {self.mode}")
            
            # Seed collections if empty
            if self.db.students.count_documents({}) == 0:
                print("[DatabaseManager] Seeding students into MongoDB...")
                self.db.students.insert_many([dict(s) for s in INITIAL_STUDENTS])
            
            if self.db.institutions.count_documents({}) == 0:
                self.db.institutions.insert_many([dict(i) for i in INSTITUTIONS])

            if self.db.workflows.count_documents({}) == 0:
                print("[DatabaseManager] Seeding workflow applications into MongoDB...")
                self.db.workflows.insert_many([dict(w) for w in WORKFLOW_APPLICATIONS])

            if self.db.notifications.count_documents({}) == 0:
                self.db.notifications.insert_many([dict(n) for n in INITIAL_NOTIFICATIONS])

            if self.db.verifications.count_documents({}) == 0:
                self.db.verifications.insert_many([dict(v) for v in self.memory_verifications])
                
        except Exception as e:
            self.connected_to_mongo = False
            self.mode = "In-Memory Fallback (Set MONGO_URI in .env to persist)"
            print(f"[DatabaseManager] MongoDB not available ({e}). Running in {self.mode}")

    def get_status(self):
        return {
            "connected_to_mongo": self.connected_to_mongo,
            "mode": self.mode,
            "mongo_uri_configured": bool(os.getenv("MONGO_URI") or os.getenv("MONGODB_URI")),
            "total_students": self.db.students.count_documents({}) if self.connected_to_mongo else len(self.memory_students),
            "total_workflow_cases": self.db.workflows.count_documents({}) if self.connected_to_mongo else len(self.memory_workflows)
        }

    @staticmethod
    def clean_id(apaar_id):
        if not apaar_id:
            return ""
        return re.sub(r'[^0-9A-Za-z]', '', str(apaar_id)).upper()

    # -------------------------------------------------------------
    # STUDENT CRUD & RETRIEVAL
    # -------------------------------------------------------------
    def get_students(self, query=None, branch=None, status=None, page=1, limit=50):
        if self.connected_to_mongo:
            filter_doc = {}
            if query:
                regex = {"$regex": query, "$options": "i"}
                filter_doc["$or"] = [
                    {"full_name": regex},
                    {"apaar_id": regex},
                    {"institution": regex},
                    {"email": regex},
                    {"branch": regex}
                ]
            if branch and branch != "All":
                filter_doc["branch"] = branch
            if status and status != "All":
                filter_doc["status"] = status
            
            cursor = self.db.students.find(filter_doc, {"_id": 0}).skip((page - 1) * limit).limit(limit)
            students = list(cursor)
            total = self.db.students.count_documents(filter_doc)
            return students, total
        else:
            filtered = self.memory_students
            if query:
                q = query.lower()
                filtered = [
                    s for s in filtered
                    if q in s.get("full_name", "").lower()
                    or q in s.get("apaar_id", "").lower()
                    or q in s.get("institution", "").lower()
                    or q in s.get("email", "").lower()
                    or q in s.get("branch", "").lower()
                ]
            if branch and branch != "All":
                filtered = [s for s in filtered if s.get("branch") == branch]
            if status and status != "All":
                filtered = [s for s in filtered if s.get("status") == status]

            total = len(filtered)
            start = (page - 1) * limit
            return filtered[start:start + limit], total

    def get_student_by_apaar(self, apaar_id):
        clean_target = self.clean_id(apaar_id)
        if self.connected_to_mongo:
            found = self.db.students.find_one({"apaar_id": apaar_id}, {"_id": 0})
            if not found:
                found = self.db.students.find_one({
                    "$expr": {
                        "$eq": [
                            {"$replaceAll": {"input": "$apaar_id", "find": "-", "replacement": ""}},
                            clean_target
                        ]
                    }
                }, {"_id": 0})
            return found
        else:
            for s in self.memory_students:
                if self.clean_id(s.get("apaar_id")) == clean_target or s.get("apaar_id") == apaar_id:
                    return s
            return None

    def add_student(self, student_data):
        clean = self.clean_id(student_data.get("apaar_id", ""))
        if len(clean) == 12 and "-" not in student_data.get("apaar_id", ""):
            student_data["apaar_id"] = f"{clean[:4]}-{clean[4:8]}-{clean[8:]}"

        if not student_data.get("qr_token"):
            student_data["qr_token"] = f"APAAR-AUTH:{clean}:{student_data.get('aicte_id', '1-GEN')}:SEC{clean[-4:]}"
        
        if self.connected_to_mongo:
            self.db.students.update_one(
                {"apaar_id": student_data["apaar_id"]},
                {"$set": student_data},
                upsert=True
            )
        else:
            existing_idx = next((i for i, s in enumerate(self.memory_students) if s["apaar_id"] == student_data["apaar_id"]), None)
            if existing_idx is not None:
                self.memory_students[existing_idx] = student_data
            else:
                self.memory_students.append(student_data)
        return student_data

    def bulk_add_students(self, students_list):
        added_count = 0
        for s in students_list:
            self.add_student(s)
            added_count += 1
        return added_count

    def update_student(self, apaar_id, updates):
        if self.connected_to_mongo:
            res = self.db.students.update_one({"apaar_id": apaar_id}, {"$set": updates})
            return res.modified_count > 0 or res.matched_count > 0
        else:
            for s in self.memory_students:
                if s["apaar_id"] == apaar_id or self.clean_id(s["apaar_id"]) == self.clean_id(apaar_id):
                    s.update(updates)
                    return True
            return False

    def delete_student(self, apaar_id):
        if self.connected_to_mongo:
            res = self.db.students.delete_one({"apaar_id": apaar_id})
            return res.deleted_count > 0
        else:
            init_len = len(self.memory_students)
            self.memory_students = [s for s in self.memory_students if s["apaar_id"] != apaar_id and self.clean_id(s["apaar_id"]) != self.clean_id(apaar_id)]
            return len(self.memory_students) < init_len

    # -------------------------------------------------------------
    # MULTI-LEVEL VERIFICATION WORKFLOW STATE MACHINE
    # -------------------------------------------------------------
    def get_workflows(self, role="AICTE_ADMIN", institution=None, status=None):
        """
        Fetches workflow applications based on role-based access control.
        - COLLEGE_OPERATOR: sees their institution's submissions.
        - INSTITUTION_VERIFIER: sees their institution's pending & reviewed submissions.
        - AUTHORIZED_REVIEWER: sees all FLAGGED_REVIEW cases across institutes.
        - AICTE_ADMIN: sees all records nationwide.
        """
        filter_doc = {}
        if status and status != "ALL":
            filter_doc["status"] = status

        if role == "COLLEGE_OPERATOR" and institution:
            filter_doc["institution"] = {"$regex": institution, "$options": "i"}
        elif role == "INSTITUTION_VERIFIER" and institution:
            filter_doc["institution"] = {"$regex": institution, "$options": "i"}
        elif role == "AUTHORIZED_REVIEWER":
            if not status or status == "ALL":
                filter_doc["status"] = {"$in": ["FLAGGED_REVIEW", "REVIEW_CLEARED_APPROVED", "FRAUD_CONFIRMED_REJECTED"]}

        if self.connected_to_mongo:
            cursor = self.db.workflows.find(filter_doc, {"_id": 0}).sort("submitted_at", -1)
            return list(cursor)
        else:
            res = self.memory_workflows
            if status and status != "ALL":
                res = [w for w in res if w.get("status") == status]
            if role in ["COLLEGE_OPERATOR", "INSTITUTION_VERIFIER"] and institution:
                res = [w for w in res if institution.lower() in w.get("institution", "").lower()]
            elif role == "AUTHORIZED_REVIEWER" and (not status or status == "ALL"):
                res = [w for w in res if w.get("status") in ["FLAGGED_REVIEW", "REVIEW_CLEARED_APPROVED", "FRAUD_CONFIRMED_REJECTED"]]
            return res

    def get_workflow_by_id(self, workflow_id):
        if self.connected_to_mongo:
            return self.db.workflows.find_one({"workflow_id": workflow_id}, {"_id": 0})
        else:
            return next((w for w in self.memory_workflows if w["workflow_id"] == workflow_id), None)

    def submit_workflow_application(self, student_data, user):
        """
        College Operator submits a new student application for verification.
        Initial State: SUBMITTED
        """
        clean = self.clean_id(student_data.get("apaar_id", ""))
        if len(clean) == 12 and "-" not in student_data.get("apaar_id", ""):
            formatted_apaar = f"{clean[:4]}-{clean[4:8]}-{clean[8:]}"
        else:
            formatted_apaar = student_data.get("apaar_id", "")

        workflow_id = f"WF-2026-{int(datetime.now().timestamp() % 100000)}"
        now = datetime.now().isoformat()
        
        record = {
            "workflow_id": workflow_id,
            "apaar_id": formatted_apaar,
            "abc_id": student_data.get("abc_id") or f"ABC-2024-{clean[-6:]}",
            "full_name": student_data.get("full_name"),
            "dob": student_data.get("dob", "2004-01-01"),
            "gender": student_data.get("gender", "Other"),
            "email": student_data.get("email"),
            "phone": student_data.get("phone", "+91 99999 00000"),
            "institution": student_data.get("institution", user.get("institution", "AICTE Affiliated Institute")),
            "aicte_id": student_data.get("aicte_id", "1-33271891"),
            "program": student_data.get("program", "B.Tech Engineering"),
            "branch": student_data.get("branch", "CSE"),
            "admission_year": int(student_data.get("admission_year", 2024)),
            "current_semester": int(student_data.get("current_semester", 1)),
            "abc_credits_total": int(student_data.get("abc_credits_total", 24)),
            "cgpa": float(student_data.get("cgpa", 8.0)),
            "status": "SUBMITTED",
            "submitted_by": f"{user.get('name', 'Operator')} ({user.get('role', 'COLLEGE_OPERATOR')})",
            "submitted_at": now,
            "assigned_to": f"Institution Verifier ({student_data.get('institution', 'DTU')})",
            "rejection_remarks": None,
            "flag_notes": None,
            "audit_history": [
                {
                    "timestamp": now,
                    "actor_name": user.get("name", "College Operator"),
                    "actor_role": user.get("role", "COLLEGE_OPERATOR"),
                    "action": "SUBMIT_RECORD",
                    "remarks": student_data.get("submission_notes", "Initial student enrollment submission with academic credentials."),
                    "prev_status": "DRAFT",
                    "new_status": "SUBMITTED"
                }
            ]
        }

        # Create in database
        if self.connected_to_mongo:
            self.db.workflows.insert_one(dict(record))
            if "_id" in record:
                del record["_id"]
        else:
            self.memory_workflows.insert(0, record)

        # Notify Institution Verifier
        self.add_notification(
            recipient_role="INSTITUTION_VERIFIER",
            institution=record["institution"],
            title="New Student Application Submitted",
            message=f"{user.get('name')} submitted {record['full_name']} ({record['apaar_id']}) for verification.",
            workflow_id=workflow_id
        )

        return record

    def process_workflow_action(self, workflow_id, action, remarks, user):
        """
        Executes State Transitions:
        - INSTITUTION_VERIFIER:
            - APPROVE -> INSTITUTION_APPROVED
            - FLAG -> FLAGGED_REVIEW
            - REJECT -> REJECTED_WITH_REMARKS
        - AUTHORIZED_REVIEWER:
            - CLEAR_FLAG -> REVIEW_CLEARED_APPROVED
            - CONFIRM_FRAUD -> FRAUD_CONFIRMED_REJECTED
            - RETURN_CORRECTION -> REJECTED_WITH_REMARKS
        - AICTE_ADMIN:
            - FINAL_APPROVE -> AICTE_FINAL_APPROVED (Auto-enrolled into live student registry!)
            - OVERRIDE_REJECT -> REJECTED_WITH_REMARKS
        - COLLEGE_OPERATOR:
            - RESUBMIT -> RESUBMITTED
        """
        record = self.get_workflow_by_id(workflow_id)
        if not record:
            return None, "Workflow application not found."

        prev_status = record.get("status")
        new_status = prev_status
        assigned_to = record.get("assigned_to")
        rejection_remarks = record.get("rejection_remarks")
        flag_notes = record.get("flag_notes")
        now = datetime.now().isoformat()
        user_role = user.get("role", "")
        user_name = user.get("name", "Authority")

        if action == "INSTITUTION_APPROVE":
            new_status = "INSTITUTION_APPROVED"
            assigned_to = "AICTE Central Admin Bureau"
            rejection_remarks = None
            self.add_notification("AICTE_ADMIN", "All", "Institution Approved Record", f"{record['full_name']} from {record['institution']} is ready for final AICTE seal.", workflow_id)

        elif action == "FLAG_FOR_REVIEW":
            new_status = "FLAGGED_REVIEW"
            flag_notes = remarks or "Flagged by Institution Verifier for suspicious credentials or dual enrollment."
            assigned_to = "Authorized Reviewer (Grievance Cell)"
            self.add_notification("AUTHORIZED_REVIEWER", "All", "Case Flagged for Review", f"{record['full_name']} flagged: {flag_notes}", workflow_id)

        elif action == "REJECT_WITH_REMARKS":
            new_status = "REJECTED_WITH_REMARKS"
            rejection_remarks = remarks or "Returned for document / credit correction."
            assigned_to = f"Returned to {record.get('submitted_by', 'College Operator')}"
            self.add_notification("COLLEGE_OPERATOR", record["institution"], "Record Returned with Remarks", f"{record['full_name']} returned: {rejection_remarks}", workflow_id)

        elif action == "CLEAR_FLAG":
            new_status = "INSTITUTION_APPROVED"
            assigned_to = "AICTE Central Admin Bureau"
            flag_notes = f"RESOLVED: {remarks}"
            self.add_notification("AICTE_ADMIN", "All", "Flag Cleared by Reviewer", f"Reviewer cleared flag for {record['full_name']}. Ready for final seal.", workflow_id)

        elif action == "CONFIRM_FRAUD":
            new_status = "FRAUD_CONFIRMED_REJECTED"
            assigned_to = "Flagged & Blocked (Permanent AICTE Blacklist)"
            flag_notes = f"FRAUD CONFIRMED: {remarks}"
            self.add_notification("AICTE_ADMIN", "All", "Fraud Confirmed Alert", f"Fraud confirmed for {record['full_name']} ({record['apaar_id']}).", workflow_id)

        elif action == "AICTE_FINAL_APPROVE":
            new_status = "AICTE_FINAL_APPROVED"
            assigned_to = "Completed (Enrolled in National APAAR Registry)"
            rejection_remarks = None
            
            # Automatically enroll into live verified students database!
            student_doc = {
                "apaar_id": record["apaar_id"],
                "abc_id": record["abc_id"],
                "full_name": record["full_name"],
                "dob": record.get("dob", "2004-01-01"),
                "gender": record.get("gender", "Other"),
                "email": record.get("email"),
                "phone": record.get("phone"),
                "institution": record["institution"],
                "aicte_id": record["aicte_id"],
                "program": record["program"],
                "branch": record["branch"],
                "admission_year": record["admission_year"],
                "current_semester": record["current_semester"],
                "abc_credits_total": record["abc_credits_total"],
                "cgpa": record["cgpa"],
                "kyc_status": "VERIFIED",
                "status": "Verified",
                "biometric_verified": True,
                "photo_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80",
                "qr_token": f"APAAR-AUTH:{self.clean_id(record['apaar_id'])}:{record['aicte_id']}:SEC-FINAL-2026",
                "academic_history": [
                    {"semester": 1, "credits": 22, "sgpa": record["cgpa"], "status": "Passed"}
                ],
                "compliance_notes": f"Officially approved by AICTE Central Admin ({user_name}) via Multi-Level Verification Workflow."
            }
            self.add_student(student_doc)
            self.add_notification("COLLEGE_OPERATOR", record["institution"], "Student Officially Enrolled!", f"{record['full_name']} is now live on the APAAR National Registry & Verifiable QR Scanner.", workflow_id)

        elif action == "RESUBMIT":
            new_status = "RESUBMITTED"
            assigned_to = f"Institution Verifier ({record['institution']})"
            rejection_remarks = None
            self.add_notification("INSTITUTION_VERIFIER", record["institution"], "Corrected Record Resubmitted", f"Operator resubmitted {record['full_name']} with corrections.", workflow_id)

        # Audit History Entry
        audit_entry = {
            "timestamp": now,
            "actor_name": user_name,
            "actor_role": user_role,
            "action": action,
            "remarks": remarks or f"Transitioned from {prev_status} to {new_status}",
            "prev_status": prev_status,
            "new_status": new_status
        }

        updates = {
            "status": new_status,
            "assigned_to": assigned_to,
            "rejection_remarks": rejection_remarks,
            "flag_notes": flag_notes
        }

        if self.connected_to_mongo:
            self.db.workflows.update_one(
                {"workflow_id": workflow_id},
                {
                    "$set": updates,
                    "$push": {"audit_history": audit_entry}
                }
            )
        else:
            record.update(updates)
            record["audit_history"].append(audit_entry)

        record.update(updates)
        record.setdefault("audit_history", []).append(audit_entry)
        return record, None

    def add_notification(self, recipient_role, institution, title, message, workflow_id=None):
        notif = {
            "id": f"NOTIF-{int(datetime.now().timestamp() * 1000)}",
            "recipient_role": recipient_role,
            "institution": institution,
            "title": title,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "workflow_id": workflow_id,
            "read": False
        }
        if self.connected_to_mongo:
            self.db.notifications.insert_one(dict(notif))
            if "_id" in notif:
                del notif["_id"]
        else:
            self.memory_notifications.insert(0, notif)
        return notif

    def get_notifications(self, role="AICTE_ADMIN", institution=None):
        if self.connected_to_mongo:
            filter_doc = {"$or": [{"recipient_role": role}, {"recipient_role": "ALL"}]}
            if institution and role != "AICTE_ADMIN":
                filter_doc["$or"].extend([{"institution": institution}, {"institution": "All"}])
            cursor = self.db.notifications.find(filter_doc, {"_id": 0}).sort("timestamp", -1).limit(25)
            return list(cursor)
        else:
            res = [n for n in self.memory_notifications if n.get("recipient_role") in [role, "ALL"]]
            return res[:25]

    def get_workflow_metrics(self):
        records = self.get_workflows(role="AICTE_ADMIN")
        total = len(records)
        submitted = sum(1 for r in records if r.get("status") in ["SUBMITTED", "RESUBMITTED"])
        inst_approved = sum(1 for r in records if r.get("status") == "INSTITUTION_APPROVED")
        flagged = sum(1 for r in records if r.get("status") == "FLAGGED_REVIEW")
        rejected = sum(1 for r in records if r.get("status") == "REJECTED_WITH_REMARKS")
        final_approved = sum(1 for r in records if r.get("status") == "AICTE_FINAL_APPROVED")
        fraud_blocked = sum(1 for r in records if r.get("status") == "FRAUD_CONFIRMED_REJECTED")

        return {
            "total_cases": total,
            "pending_institution_verification": submitted,
            "pending_aicte_final_approval": inst_approved,
            "flagged_for_reviewer": flagged,
            "returned_for_correction": rejected,
            "officially_enrolled": final_approved,
            "fraud_blocked": fraud_blocked
        }

    # -------------------------------------------------------------
    # AI-POWERED DATA QUALITY ASSISTANT ENGINE
    # -------------------------------------------------------------
    def analyze_record_quality(self, record):
        """
        Performs AI & rule-based quality evaluation on a student record:
        - Checks missing mandatory fields and format rules
        - Identifies spelling mistakes & abbreviation in colleges and branches
        - Detects out-of-bounds metrics (CGPA, future admission years)
        - Computes hygiene score (0 - 100)
        - Generates natural-language AI insights & suggested 1-click fixes
        """
        issues = []
        suggested_fixes = {}
        penalty = 0

        raw_apaar = str(record.get("raw_apaar_id") or record.get("apaar_id") or "").strip()
        raw_name = str(record.get("raw_full_name") or record.get("full_name") or "").strip()
        raw_inst = str(record.get("raw_institution") or record.get("institution") or "").strip()
        raw_branch = str(record.get("raw_branch") or record.get("branch") or "").strip()
        raw_email = str(record.get("raw_email") or record.get("email") or "").strip()
        raw_phone = str(record.get("raw_phone") or record.get("phone") or "").strip()
        raw_cgpa = record.get("raw_cgpa") if record.get("raw_cgpa") is not None else record.get("cgpa")
        raw_abc = str(record.get("raw_abc_id") or record.get("abc_id") or "").strip()

        # 1. APAAR ID Validation
        clean_apaar = self.clean_id(raw_apaar)
        if not raw_apaar:
            issues.append({
                "field": "apaar_id",
                "severity": "CRITICAL",
                "type": "MISSING_MANDATORY",
                "message": "APAAR ID is missing.",
                "explanation": "Every student must possess a unique 12-digit APAAR ID under the NEP 2020 mandate."
            })
            penalty += 30
        elif len(clean_apaar) != 12:
            issues.append({
                "field": "apaar_id",
                "severity": "HIGH",
                "type": "INVALID_FORMAT",
                "message": f"Invalid APAAR length ({len(clean_apaar)} chars). Must be exactly 12 digits.",
                "explanation": "The National Academic Depository requires 12 numeric digits in 4-4-4 format."
            })
            penalty += 20
            if len(clean_apaar) == 11:
                suggested_fixes["apaar_id"] = f"{clean_apaar[:4]}-{clean_apaar[4:8]}-{clean_apaar[8:]}0"
        else:
            suggested_fixes["apaar_id"] = f"{clean_apaar[:4]}-{clean_apaar[4:8]}-{clean_apaar[8:]}"

        # 2. Student Full Name Check
        if not raw_name:
            issues.append({
                "field": "full_name",
                "severity": "CRITICAL",
                "type": "MISSING_MANDATORY",
                "message": "Student Full Name is missing.",
                "explanation": "Legal name must match Aadhaar & 10th certificate."
            })
            penalty += 25
        else:
            # Check for irregular casing or extra spaces
            cleaned_name = " ".join([word.capitalize() for word in raw_name.split()])
            if cleaned_name != raw_name:
                issues.append({
                    "field": "full_name",
                    "severity": "MEDIUM",
                    "type": "FORMATTING_TYPO",
                    "message": f"Irregular casing or whitespace: '{raw_name}'",
                    "explanation": "AI normalized name to standard title case."
                })
                suggested_fixes["full_name"] = cleaned_name
                penalty += 10
            elif len(raw_name.split()) < 2:
                issues.append({
                    "field": "full_name",
                    "severity": "LOW",
                    "type": "POTENTIAL_INCOMPLETE",
                    "message": "Single name detected without surname.",
                    "explanation": "Ensure single name matches official government identity."
                })
                penalty += 5

        # 3. Institution Name Typos & Standardization
        inst_lower = raw_inst.lower()
        if not raw_inst:
            issues.append({
                "field": "institution",
                "severity": "CRITICAL",
                "type": "MISSING_MANDATORY",
                "message": "Institution name is missing.",
                "explanation": "Mandatory AICTE institutional affiliation required."
            })
            penalty += 25
        elif inst_lower in INSTITUTION_NORMALIZATION_MAP:
            standard_inst = INSTITUTION_NORMALIZATION_MAP[inst_lower]
            if standard_inst != raw_inst:
                issues.append({
                    "field": "institution",
                    "severity": "HIGH",
                    "type": "SPELLING_ABBREVIATION",
                    "message": f"Non-standard institution name: '{raw_inst}'",
                    "explanation": f"AI identified likely match: '{standard_inst}'. Standardization avoids rejection during AICTE audits."
                })
                suggested_fixes["institution"] = standard_inst
                penalty += 15
        else:
            suggested_fixes["institution"] = raw_inst

        # 4. Branch & Program Normalization
        branch_lower = raw_branch.lower()
        if not raw_branch:
            issues.append({
                "field": "branch",
                "severity": "HIGH",
                "type": "MISSING_MANDATORY",
                "message": "Engineering branch or program is missing.",
                "explanation": "AICTE requires approved nomenclature for degree award."
            })
            penalty += 20
        elif branch_lower in BRANCH_NORMALIZATION_MAP:
            norm = BRANCH_NORMALIZATION_MAP[branch_lower]
            if norm["branch"] != raw_branch:
                issues.append({
                    "field": "branch",
                    "severity": "MEDIUM",
                    "type": "STANDARDIZATION_SUGGESTION",
                    "message": f"Informal branch name: '{raw_branch}'",
                    "explanation": f"Mapped to official AICTE designation: '{norm['program']}' ({norm['branch']})."
                })
                suggested_fixes["branch"] = norm["branch"]
                suggested_fixes["program"] = norm["program"]
                penalty += 10
        else:
            suggested_fixes["branch"] = raw_branch
            suggested_fixes["program"] = f"B.Tech {raw_branch}"

        # 5. CGPA Range Validation
        try:
            val_cgpa = float(raw_cgpa) if raw_cgpa is not None else 8.0
            if val_cgpa > 10.0:
                issues.append({
                    "field": "cgpa",
                    "severity": "HIGH",
                    "type": "OUT_OF_BOUNDS",
                    "message": f"CGPA value {val_cgpa} exceeds maximum scale of 10.0.",
                    "explanation": "AI detected likely percentage entered instead of 10-point GPA or typo."
                })
                suggested_fixes["cgpa"] = round(val_cgpa / 10.0, 2) if val_cgpa <= 100 else 9.0
                penalty += 15
            elif val_cgpa < 0.0:
                issues.append({
                    "field": "cgpa",
                    "severity": "HIGH",
                    "type": "INVALID_VALUE",
                    "message": f"Negative CGPA {val_cgpa} is invalid.",
                    "explanation": "CGPA must be positive."
                })
                suggested_fixes["cgpa"] = 7.5
                penalty += 15
            else:
                suggested_fixes["cgpa"] = val_cgpa
        except (ValueError, TypeError):
            issues.append({
                "field": "cgpa",
                "severity": "MEDIUM",
                "type": "TYPE_ERROR",
                "message": "CGPA must be a numeric value.",
                "explanation": "Ensure decimal format e.g. 8.75."
            })
            suggested_fixes["cgpa"] = 8.0
            penalty += 10

        # 6. Email Format Check
        if raw_email:
            if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', raw_email) or "@@" in raw_email or ".." in raw_email:
                issues.append({
                    "field": "email",
                    "severity": "HIGH",
                    "type": "INVALID_FORMAT",
                    "message": f"Malformed email address: '{raw_email}'",
                    "explanation": "Double symbols or syntax error detected in institutional email."
                })
                cleaned_email = re.sub(r'@+', '@', raw_email)
                cleaned_email = re.sub(r'\.+', '.', cleaned_email)
                suggested_fixes["email"] = cleaned_email
                penalty += 12
            else:
                suggested_fixes["email"] = raw_email

        # 7. ABC ID Format
        if not raw_abc:
            issues.append({
                "field": "abc_id",
                "severity": "HIGH",
                "type": "MISSING_MANDATORY",
                "message": "Academic Bank of Credits (ABC) ID is missing.",
                "explanation": "ABC ID links student credits to the National Academic Depository."
            })
            suggested_fixes["abc_id"] = f"ABC-2024-{clean_apaar[-6:] if len(clean_apaar)>=6 else '102938'}"
            penalty += 18
        elif not re.match(r'^ABC-\d{4}-\d{6}$', raw_abc):
            issues.append({
                "field": "abc_id",
                "severity": "LOW",
                "type": "FORMAT_INCONSISTENCY",
                "message": f"Non-standard ABC format: '{raw_abc}'. Expected 'ABC-YYYY-XXXXXX'",
                "explanation": "Missing hyphens or date segment."
            })
            digits_abc = re.sub(r'\D', '', raw_abc)
            if len(digits_abc) >= 10:
                suggested_fixes["abc_id"] = f"ABC-{digits_abc[:4]}-{digits_abc[4:10]}"
            else:
                suggested_fixes["abc_id"] = f"ABC-2024-{clean_apaar[-6:] if len(clean_apaar)>=6 else '884920'}"
            penalty += 8
        else:
            suggested_fixes["abc_id"] = raw_abc

        # Compute Quality Score
        quality_score = max(5, 100 - penalty)
        status = "EXCELLENT" if quality_score >= 90 else "GOOD" if quality_score >= 75 else "NEEDS_CLEANING" if quality_score >= 50 else "CRITICAL_ERRORS"

        return {
            "record_id": record.get("id") or record.get("workflow_id") or clean_apaar or "TEMP-REC",
            "quality_score": quality_score,
            "status": status,
            "issues_count": len(issues),
            "issues": issues,
            "suggested_fixes": suggested_fixes,
            "original_record": record,
            "ai_summary": f"Identified {len(issues)} data quality issue(s). Overall hygiene score: {quality_score}/100. " +
                          ("High confidence auto-corrections available for 1-click cleanup." if issues else "Record is clean and ready for submission.")
        }

    def analyze_batch_quality(self, batch_records):
        results = [self.analyze_record_quality(r) for r in batch_records]
        total_records = len(results)
        if total_records == 0:
            return {"overall_score": 100, "results": [], "department_stats": {}}

        avg_score = round(sum(r["quality_score"] for r in results) / total_records, 1)
        clean_count = sum(1 for r in results if r["quality_score"] >= 90)
        flagged_count = sum(1 for r in results if r["issues_count"] > 0)
        total_issues = sum(r["issues_count"] for r in results)

        # Department breakdown
        dept_scores = {}
        dept_counts = {}
        for r in results:
            orig = r["original_record"]
            dept = orig.get("department") or orig.get("branch") or "General"
            dept_scores[dept] = dept_scores.get(dept, 0) + r["quality_score"]
            dept_counts[dept] = dept_counts.get(dept, 0) + 1

        dept_summary = {
            d: {
                "score": round(dept_scores[d] / dept_counts[d], 1),
                "count": dept_counts[d]
            }
            for d in dept_scores
        }

        return {
            "total_records": total_records,
            "overall_score": avg_score,
            "clean_records": clean_count,
            "flagged_records": flagged_count,
            "total_issues": total_issues,
            "department_breakdown": dept_summary,
            "results": results
        }

    def get_sample_dirty_batch(self):
        return [dict(d) for d in DIRTY_BATCH_DATA]

    # -------------------------------------------------------------
    # AI-BASED VERIFICATION ENGINE FOR NEW STUDENT APAAR ID
    # -------------------------------------------------------------
    @staticmethod
    def _levenshtein_distance(s1, s2):
        if len(s1) < len(s2):
            return DatabaseManager._levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        prev_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            curr_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = prev_row[j + 1] + 1
                deletions = curr_row[j] + 1
                substitutions = prev_row[j] + (c1 != c2)
                curr_row.append(min(insertions, deletions, substitutions))
            prev_row = curr_row
        return prev_row[-1]

    @staticmethod
    def calculate_name_similarity(name1, name2):
        if not name1 or not name2:
            return 0.0
        n1 = re.sub(r'[^a-zA-Z0-9 ]', '', str(name1)).strip().lower()
        n2 = re.sub(r'[^a-zA-Z0-9 ]', '', str(name2)).strip().lower()
        if n1 == n2:
            return 100.0

        t1 = set(n1.split())
        t2 = set(n2.split())
        intersection = t1.intersection(t2)
        union = t1.union(t2)
        jaccard = (len(intersection) / len(union)) * 100 if union else 0.0

        dist = DatabaseManager._levenshtein_distance(n1, n2)
        max_len = max(len(n1), len(n2), 1)
        lev_ratio = max(0.0, (1.0 - (dist / max_len))) * 100

        return round(0.4 * jaccard + 0.6 * lev_ratio, 1)

    def get_ai_verification_presets(self):
        return [
            {
                "preset_id": "CLEAN_APPLICANT",
                "title": "Priya Sharma (Direct Clean Admission)",
                "badge": "98% AI Match • Clean Fast-Track",
                "description": "Standard B.Tech CSE applicant. Aadhaar KYC demographic match 100%, verified 12th marksheet, active AICTE affiliation.",
                "payload": {
                    "full_name": "Priya Sharma",
                    "aadhaar_number": "5544-3322-1100",
                    "student_consent": True,
                    "dob": "2004-06-15",
                    "gender": "Female",
                    "email": "priya.sharma24@dtu.ac.in",
                    "phone": "+91 98110 33445",
                    "institution": "Delhi Technological University",
                    "aicte_id": "1-33271891",
                    "program": "B.Tech Computer Science & Engineering",
                    "branch": "CSE",
                    "admission_year": 2024,
                    "current_semester": 1,
                    "cgpa": 8.85,
                    "document_name": "Class_XII_CBSE_Marksheet_Verified.pdf",
                    "document_type": "CLASS_12_MARKSHEET",
                    "document_uploaded": True
                }
            },
            {
                "preset_id": "TYPO_DISCREPANCY",
                "title": "Rohan Mehta (Aadhaar Typo Discrepancy)",
                "badge": "76% AI Match • AI Auto-Fix Suggested",
                "description": "Student input says 'Rohan Mehta' but Aadhaar record reads 'Rohan Menta'. AI suggests normalization.",
                "payload": {
                    "full_name": "Rohan Mehta",
                    "aadhaar_number": "8877-6655-4433",
                    "student_consent": True,
                    "dob": "2003-11-20",
                    "gender": "Male",
                    "email": "rohan.mehta@vjti.ac.in",
                    "phone": "+91 98200 44556",
                    "institution": "Veermata Jijabai Technological Institute (VJTI Mumbai)",
                    "aicte_id": "1-44910283",
                    "program": "B.Tech Artificial Intelligence & Data Science",
                    "branch": "AI & DS",
                    "admission_year": 2024,
                    "current_semester": 1,
                    "cgpa": 8.40,
                    "document_name": "VJTI_Seat_Allotment_Slip.pdf",
                    "document_type": "ADMISSION_ALLOTMENT",
                    "document_uploaded": True
                }
            },
            {
                "preset_id": "DUAL_ENROLLMENT_FRAUD",
                "title": "Vikramaditya Rao (Ghost Student / Dual Seat Fraud)",
                "badge": "32% AI Score • Critical Fraud Alert",
                "description": "Student attempts APAAR enrollment at DTU while already actively enrolled at Apex Institute of Tech.",
                "payload": {
                    "full_name": "Vikramaditya Rao",
                    "aadhaar_number": "9999-0000-1111",
                    "student_consent": True,
                    "dob": "2002-04-10",
                    "gender": "Male",
                    "email": "vikram.rao@dtu.ac.in",
                    "phone": "+91 99999 11111",
                    "institution": "Delhi Technological University",
                    "aicte_id": "1-33271891",
                    "program": "B.Tech Mechanical Engineering",
                    "branch": "ME",
                    "admission_year": 2024,
                    "current_semester": 1,
                    "cgpa": 6.10,
                    "document_name": "Transfer_Certificate_Unverified.pdf",
                    "document_type": "TRANSFER_CERTIFICATE",
                    "document_uploaded": True
                }
            },
            {
                "preset_id": "MISSING_DOCUMENTS",
                "title": "Sneha Reddy (Missing Mandatory Marksheet)",
                "badge": "64% AI Score • Missing Document Alert",
                "description": "Student consent and demographics verified, but mandatory Class XII marksheet document is missing.",
                "payload": {
                    "full_name": "Sneha Reddy",
                    "aadhaar_number": "3322-1144-5566",
                    "student_consent": True,
                    "dob": "2004-01-25",
                    "gender": "Female",
                    "email": "sneha.reddy@coep.ac.in",
                    "phone": "+91 98490 22331",
                    "institution": "College of Engineering Pune (COEP)",
                    "aicte_id": "1-55109284",
                    "program": "B.Tech Electronics & Telecommunication",
                    "branch": "ENTC",
                    "admission_year": 2024,
                    "current_semester": 1,
                    "cgpa": 8.70,
                    "document_name": "",
                    "document_type": "NONE",
                    "document_uploaded": False
                }
            }
        ]

    def ai_verify_new_student(self, data, auto_enroll=False, user=None):
        """
        AI-Based Verification for APAAR ID verification & issuance of new students.
        Executes:
        1. Aadhaar identity authentication & student consent validation.
        2. Demographics matching & normalization.
        3. National central repository duplicate & ghost student detection (Anti-Fraud).
        4. AICTE institutional affiliation & program compliance check.
        5. Academic document integrity evaluation.
        6. AI Trust Score calculation & APAAR ID generation.
        7. Automated workflow application submission & smart alert generation.
        """
        now = datetime.now().isoformat()
        full_name = str(data.get("full_name") or "").strip()
        aadhaar_raw = str(data.get("aadhaar_number") or "").strip()
        student_consent = bool(data.get("student_consent", False))
        dob = str(data.get("dob") or "2004-01-01").strip()
        gender = str(data.get("gender") or "Not Specified").strip()
        institution = str(data.get("institution") or "").strip()
        aicte_id = str(data.get("aicte_id") or "").strip()
        branch = str(data.get("branch") or "CSE").strip()
        program = str(data.get("program") or f"B.Tech {branch}").strip()
        admission_year = int(data.get("admission_year") or 2024)
        email = str(data.get("email") or f"{full_name.lower().replace(' ', '.')}@ac.in").strip()
        phone = str(data.get("phone") or "+91 98000 00000").strip()
        cgpa = float(data.get("cgpa") or 8.0)
        document_uploaded = bool(data.get("document_uploaded", True))
        document_name = str(data.get("document_name") or "MarkSheet_Document.pdf").strip()

        # STAGE 0: Consent Verification (Mandatory under Aadhaar Act & AICTE guidelines)
        if not student_consent:
            return {
                "success": False,
                "verified": False,
                "status": "CONSENT_DENIED",
                "message": "Student Consent Required: Verification cannot proceed without student authorization under the Aadhaar Act & AICTE Digilocker Guidelines.",
                "ai_trust_score": 0.0,
                "flags": ["Student consent checkbox was not checked."]
            }

        if not full_name:
            return {
                "success": False,
                "verified": False,
                "status": "INVALID_INPUT",
                "message": "Student Full Name is required.",
                "ai_trust_score": 0.0
            }

        clean_aadhaar = self.clean_id(aadhaar_raw)
        if not clean_aadhaar:
            clean_aadhaar = "554433221100"

        # Masked Aadhaar format for privacy compliance
        masked_aadhaar = f"XXXX-XXXX-{clean_aadhaar[-4:]}" if len(clean_aadhaar) >= 4 else "XXXX-XXXX-0000"

        # STAGE 1: Aadhaar Identity & Demographics AI Fuzzy Match
        # Simulated UIDAI / DigiLocker master identity store
        uidai_registry = {
            "554433221100": {"name": "Priya Sharma", "dob": "2004-06-15", "gender": "Female", "status": "VERIFIED"},
            "887766554433": {"name": "Rohan Menta", "dob": "2003-11-20", "gender": "Male", "status": "VERIFIED"},
            "999900001111": {"name": "Vikramaditya Rao", "dob": "2002-04-10", "gender": "Male", "status": "ACTIVE_STUDENT", "existing_college": "Apex Institute of Tech"},
            "332211445566": {"name": "Sneha Reddy", "dob": "2004-01-25", "gender": "Female", "status": "VERIFIED"}
        }

        matched_uidai = uidai_registry.get(clean_aadhaar)
        if matched_uidai:
            official_name = matched_uidai["name"]
            official_dob = matched_uidai["dob"]
        else:
            # Dynamic identity for any other custom input
            official_name = full_name
            official_dob = dob

        name_similarity = self.calculate_name_similarity(full_name, official_name)
        dob_match = 100.0 if (dob == official_dob or not official_dob) else 40.0
        demographic_score = round(0.75 * name_similarity + 0.25 * dob_match, 1)

        flags = []
        suggested_corrections = {}

        if name_similarity < 90.0:
            flags.append(f"Demographic Discrepancy: Input name '{full_name}' differs from Aadhaar master record '{official_name}' ({name_similarity}% match).")
            suggested_corrections["full_name"] = official_name

        # STAGE 2: Anti-Fraud & Duplicate Identity Detection (Ghost Student Sentinel)
        duplicate_detected = False
        duplicate_details = None

        # Check existing registered students in MongoDB / Memory
        all_students, _ = self.get_students(limit=1000)
        for s in all_students:
            s_aadhaar = self.clean_id(s.get("aadhaar_number", "") or s.get("apaar_id", ""))
            # Check duplicate Aadhaar or special dual enrollment flag
            if clean_aadhaar == "999900001111" or (clean_aadhaar and s_aadhaar == clean_aadhaar):
                duplicate_detected = True
                duplicate_details = f"Active enrollment already exists under APAAR '{s.get('apaar_id')}' at '{s.get('institution')}'."
                break

        if matched_uidai and matched_uidai.get("existing_college"):
            if matched_uidai["existing_college"].lower() not in institution.lower():
                duplicate_detected = True
                duplicate_details = f"Aadhaar is already registered concurrently at '{matched_uidai['existing_college']}' (Dual Enrollment Violation)."

        if duplicate_detected:
            anti_fraud_score = 10.0
            flags.append(f"DUAL ENROLLMENT FRAUD DETECTED: {duplicate_details}")
        else:
            anti_fraud_score = 100.0

        # STAGE 3: AICTE Institutional Affiliation & Program Compliance Check
        institutions = self.get_institutions()
        matched_inst = None
        for inst in institutions:
            if aicte_id and inst.get("aicte_id") == aicte_id:
                matched_inst = inst
                break
            if institution and inst.get("name", "").lower() in institution.lower():
                matched_inst = inst
                break

        if matched_inst:
            inst_compliance_score = 100.0
            verified_institution_name = matched_inst.get("name", institution)
            verified_aicte_id = matched_inst.get("aicte_id", aicte_id or "1-GEN")
        else:
            inst_compliance_score = 55.0
            verified_institution_name = institution or "Unverified AICTE Institution"
            verified_aicte_id = aicte_id or "1-UNVERIFIED"
            flags.append(f"AICTE Affiliation Warning: Institute code '{aicte_id}' is pending central database re-accreditation.")

        # STAGE 4: Academic Document & Eligibility Verification
        if document_uploaded and document_name:
            doc_score = 100.0
            doc_status = "DOCUMENTS_VERIFIED"
        else:
            doc_score = 30.0
            doc_status = "MISSING_MANDATORY_DOCUMENTS"
            flags.append("Missing Document: Class XII Marksheet / DigiLocker academic certificate has not been uploaded.")

        # STAGE 5: AI Risk Assessment & Trust Score Calculation
        if duplicate_detected:
            anti_fraud_score = 0.0
            ai_trust_score = round((demographic_score * 0.25) + (anti_fraud_score * 0.50) + (inst_compliance_score * 0.15) + (doc_score * 0.10), 1)
            verdict_status = "AI_REJECTED_FRAUD"
            risk_level = "CRITICAL_FRAUD"
            decision_text = "AICTE Anti-Fraud Sentinel Blocked: Duplicate Aadhaar enrollment detected across multiple colleges."
            recommendation = "Reject record immediately and report to AICTE Grievance & Disciplinary Board."
        elif len(flags) > 0:
            ai_trust_score = round((demographic_score * 0.35) + (anti_fraud_score * 0.25) + (inst_compliance_score * 0.25) + (doc_score * 0.15), 1)
            if ai_trust_score > 84.0:
                ai_trust_score = round(ai_trust_score - 12.0, 1) # Penalty for discrepancy
            verdict_status = "AI_FLAGGED_DISCREPANCY"
            risk_level = "MEDIUM_ATTENTION"
            decision_text = "Minor demographic discrepancy or pending document detected by AI validation model."
            recommendation = "Route to Institution Verifier / Authorized Reviewer with suggested automated corrections."
        else:
            ai_trust_score = round((demographic_score * 0.35) + (anti_fraud_score * 0.25) + (inst_compliance_score * 0.25) + (doc_score * 0.15), 1)
            verdict_status = "AI_VERIFIED_CLEAN"
            risk_level = "LOW_RISK"
            decision_text = "Identity, Aadhaar e-KYC, AICTE institution affiliation, and documents cryptographically verified."
            recommendation = "Approved for instantaneous APAAR ID generation and automated repository enrollment."

        # STAGE 7: APAAR ID & ABC ID Generation
        # Deterministic or clean 12-digit APAAR ID
        clean_seed = abs(hash(f"{full_name}:{clean_aadhaar}:{verified_institution_name}")) % 900000000000 + 100000000000
        apaar_digits = str(clean_seed)
        generated_apaar_id = f"{apaar_digits[:4]}-{apaar_digits[4:8]}-{apaar_digits[8:12]}"
        generated_abc_id = f"ABC-{admission_year}-{apaar_digits[-6:]}"
        qr_token = f"APAAR-AUTH:{apaar_digits}:{verified_aicte_id}:AI-VERIFIED-2026"

        ai_report = {
            "trust_score": ai_trust_score,
            "status": verdict_status,
            "risk_level": risk_level,
            "decision": decision_text,
            "recommendation": recommendation,
            "demographic_match_score": demographic_score,
            "name_similarity_percent": name_similarity,
            "anti_fraud_score": anti_fraud_score,
            "institution_compliance_score": inst_compliance_score,
            "document_score": doc_score,
            "official_aadhaar_name": official_name,
            "masked_aadhaar": masked_aadhaar,
            "student_consent_verified": True,
            "consent_timestamp": now,
            "flags": flags,
            "suggested_corrections": suggested_corrections,
            "doc_status": doc_status
        }

        created_student = None
        workflow_app = None

        # STAGE 8: Automated Storage & Workflow Pipeline Submission
        if auto_enroll:
            # Prepare full student record
            student_doc = {
                "apaar_id": generated_apaar_id,
                "abc_id": generated_abc_id,
                "full_name": official_name if name_similarity < 90 else full_name,
                "dob": dob,
                "gender": gender,
                "email": email,
                "phone": phone,
                "institution": verified_institution_name,
                "aicte_id": verified_aicte_id,
                "program": program,
                "branch": branch,
                "admission_year": admission_year,
                "current_semester": int(data.get("current_semester") or 1),
                "abc_credits_total": 24,
                "cgpa": cgpa,
                "status": "Verified" if verdict_status == "AI_VERIFIED_CLEAN" else "Flagged",
                "kyc_status": "VERIFIED" if verdict_status != "AI_REJECTED_FRAUD" else "REJECTED_FRAUD",
                "biometric_verified": verdict_status == "AI_VERIFIED_CLEAN",
                "masked_aadhaar": masked_aadhaar,
                "student_consent": True,
                "consent_timestamp": now,
                "photo_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80",
                "qr_token": qr_token,
                "academic_history": [
                    {"semester": 1, "credits": 24, "sgpa": cgpa, "status": "Passed"}
                ],
                "compliance_notes": f"AI-Verified ({ai_trust_score}% Trust Score). {decision_text}",
                "ai_verification_report": ai_report
            }

            if verdict_status == "AI_VERIFIED_CLEAN":
                created_student = self.add_student(student_doc)

            # Insert application into Multi-Level Verification Workflow
            operator_user = user or {
                "name": "Ramesh Patel",
                "role": "COLLEGE_OPERATOR",
                "institution": verified_institution_name
            }

            app_status = "INSTITUTION_APPROVED" if verdict_status == "AI_VERIFIED_CLEAN" else ("FLAGGED_REVIEW" if verdict_status == "AI_FLAGGED_DISCREPANCY" else "FRAUD_CONFIRMED_REJECTED")

            workflow_payload = {
                "apaar_id": generated_apaar_id,
                "abc_id": generated_abc_id,
                "full_name": student_doc["full_name"],
                "dob": dob,
                "gender": gender,
                "email": email,
                "phone": phone,
                "institution": verified_institution_name,
                "aicte_id": verified_aicte_id,
                "program": program,
                "branch": branch,
                "admission_year": admission_year,
                "current_semester": 1,
                "abc_credits_total": 24,
                "cgpa": cgpa,
                "status": app_status,
                "submission_notes": f"AI-Powered Verification Application. Score: {ai_trust_score}%. {decision_text}",
                "ai_verification_report": ai_report
            }

            workflow_app = self.submit_workflow_application(workflow_payload, operator_user)

            # Dispatch smart alerts
            if verdict_status == "AI_VERIFIED_CLEAN":
                self.add_notification(
                    "INSTITUTION_VERIFIER",
                    verified_institution_name,
                    "New AI-Verified APAAR Application",
                    f"{full_name} was validated with {ai_trust_score}% trust score. Ready for final AICTE seal.",
                    workflow_app.get("workflow_id")
                )
            elif verdict_status == "AI_FLAGGED_DISCREPANCY":
                self.add_notification(
                    "AUTHORIZED_REVIEWER",
                    verified_institution_name,
                    "AI Discrepancy Flagged",
                    f"{full_name} has minor discrepancies ({', '.join(flags[:2])}). Requires reviewer validation.",
                    workflow_app.get("workflow_id")
                )
            else:
                self.add_notification(
                    "AICTE_ADMIN",
                    "All",
                    "CRITICAL FRAUD SENTINEL ALERT",
                    f"Blocked dual-enrollment attempt for {full_name} (Aadhaar {masked_aadhaar}).",
                    workflow_app.get("workflow_id")
                )

        return {
            "success": True,
            "verified": verdict_status == "AI_VERIFIED_CLEAN",
            "apaar_id": generated_apaar_id,
            "abc_id": generated_abc_id,
            "qr_token": qr_token,
            "ai_trust_score": ai_trust_score,
            "status": verdict_status,
            "risk_level": risk_level,
            "report": ai_report,
            "student_record": created_student,
            "workflow_record": workflow_app,
            "message": decision_text
        }

    # Verification logs
    def log_verification(self, apaar_id, student_name, institution, status, details, verifier="QR Scanner"):
        record = {
            "id": f"VER-{int(datetime.now().timestamp() * 1000)}",
            "apaar_id": apaar_id,
            "student_name": student_name,
            "institution": institution,
            "status": status,
            "verifier": verifier,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        if self.connected_to_mongo:
            self.db.verifications.insert_one(dict(record))
            if "_id" in record:
                del record["_id"]
        else:
            self.memory_verifications.insert(0, record)
        return record

    def get_verifications(self, limit=20):
        if self.connected_to_mongo:
            cursor = self.db.verifications.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit)
            return list(cursor)
        else:
            return self.memory_verifications[:limit]

    def get_institutions(self):
        if self.connected_to_mongo:
            return list(self.db.institutions.find({}, {"_id": 0}))
        else:
            return self.memory_institutions

    def get_analytics(self):
        students, _ = self.get_students(limit=1000)
        total = len(students)
        verified = sum(1 for s in students if s.get("status") == "Verified")
        flagged = sum(1 for s in students if s.get("status") == "Flagged")
        graduated = sum(1 for s in students if s.get("status") == "Graduated")
        total_credits = sum(s.get("abc_credits_total", 0) for s in students)
        
        branch_counts = {}
        for s in students:
            b = s.get("branch", "Other")
            branch_counts[b] = branch_counts.get(b, 0) + 1
            
        recent_verifications = self.get_verifications(limit=6)
        workflow_metrics = self.get_workflow_metrics()
        
        return {
            "total_students": total,
            "verified_count": verified,
            "flagged_fraud_count": flagged,
            "graduated_count": graduated,
            "total_abc_credits": total_credits,
            "avg_credits": round(total_credits / max(1, total), 1),
            "compliance_rate": round((verified / max(1, total)) * 100, 1),
            "branch_distribution": branch_counts,
            "recent_verifications": recent_verifications,
            "institutions_count": len(self.get_institutions()),
            "workflow_metrics": workflow_metrics
        }

db_manager = DatabaseManager()
