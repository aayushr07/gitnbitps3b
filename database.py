"""
Database Manager for AICTE APAAR ID Platform
Handles MongoDB connections, in-memory fallbacks, automated validation engine,
admission intake checking, and verifiable academic credential generation.
"""

import os
import re
from datetime import datetime
from dotenv import load_dotenv

from seed_data import (
    INSTITUTIONS,
    INITIAL_STUDENTS,
    SAMPLE_ADMISSION_BATCH,
    AUTHORITY_USERS,
    INITIAL_AUDIT_LOGS
)

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/apaar_aicte")


class DatabaseManager:
    def __init__(self):
        self.connected_to_mongo = False
        self.client = None
        self.db = None
        self.mode = "In-Memory / Local Mode"
        
        # In-memory stores
        self.memory_students = [dict(s) for s in INITIAL_STUDENTS]
        self.memory_institutions = [dict(i) for i in INSTITUTIONS]
        self.memory_audit_logs = [dict(a) for a in INITIAL_AUDIT_LOGS]
        self.memory_sample_batch = [dict(b) for b in SAMPLE_ADMISSION_BATCH]
        self.memory_verifications = [
            {
                "id": "VER-1001",
                "apaar_id": "9283-4710-8521",
                "student_name": "Aarav Sharma",
                "institution": "Delhi Technological University",
                "status": "SUCCESS_VERIFIED",
                "verifier": "Tata Consultancy Services (HR Campus Onboarding)",
                "timestamp": datetime.now().isoformat(),
                "details": "Academic Bank of Credits (126), DigiLocker e-KYC, and AICTE Approval authenticated."
            },
            {
                "id": "VER-1002",
                "apaar_id": "9999-0000-1111",
                "student_name": "Vikramaditya Rao",
                "institution": "Apex Institute of Advanced Technology",
                "status": "ALERT_FLAGGED",
                "verifier": "AICTE Admissions Verification Gateway",
                "timestamp": datetime.now().isoformat(),
                "details": "ALERT: Concurrent dual enrollment detected across 2 institutions. Excess intake violation flagged."
            }
        ]
        
        self._init_mongo()

    def _init_mongo(self):
        try:
            from pymongo import MongoClient
            self.client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=4000)
            self.client.admin.command('ping')
            try:
                self.db = self.client.get_default_database()
            except Exception:
                self.db = None
            if self.db is None or self.db.name in ["admin", "test"]:
                self.db = self.client["apaar_aicte"]
            
            self.connected_to_mongo = True
            self.mode = "MongoDB Connected"
            print("Connected to MongoDB successfully.")
            self._sync_seed_if_empty()
        except Exception as e:
            self.connected_to_mongo = False
            self.mode = "In-Memory Standalone"
            print(f"MongoDB not available ({e}). Running in resilient In-Memory Mode.")

    def _sync_seed_if_empty(self):
        if not self.connected_to_mongo:
            return
        try:
            if self.db.students.count_documents({}) == 0:
                self.db.students.insert_many([dict(s) for s in INITIAL_STUDENTS])
            if self.db.institutions.count_documents({}) == 0:
                self.db.institutions.insert_many([dict(i) for i in INSTITUTIONS])
            if self.db.audit_logs.count_documents({}) == 0:
                self.db.audit_logs.insert_many([dict(a) for a in INITIAL_AUDIT_LOGS])
        except Exception as e:
            print("MongoDB sync error:", e)

    def get_status(self):
        return {
            "mode": self.mode,
            "connected_to_mongo": self.connected_to_mongo,
            "total_students": len(self.memory_students) if not self.connected_to_mongo else self.db.students.count_documents({}),
            "total_institutions": len(self.memory_institutions) if not self.connected_to_mongo else self.db.institutions.count_documents({})
        }

    @staticmethod
    def clean_id(apaar_id):
        if not apaar_id:
            return ""
        return re.sub(r'[^0-9A-Za-z]', '', str(apaar_id)).upper()

    # -------------------------------------------------------------
    # STUDENT RETRIEVAL & CRUD
    # -------------------------------------------------------------
    def get_students(self, query=None, branch=None, status=None, institution=None, quota=None, page=1, limit=50):
        if self.connected_to_mongo:
            filter_doc = {}
            if query:
                regex = {"$regex": query, "$options": "i"}
                filter_doc["$or"] = [
                    {"full_name": regex},
                    {"apaar_id": regex},
                    {"student_id": regex},
                    {"institution": regex},
                    {"email": regex},
                    {"branch": regex}
                ]
            if branch and branch != "All":
                filter_doc["branch"] = branch
            if status and status != "All":
                filter_doc["status"] = status
            if institution and institution != "All":
                filter_doc["institution"] = institution
            if quota and quota != "All":
                if quota == "Supernumerary":
                    filter_doc["supernumerary_seat"] = True
                elif quota == "TFWS":
                    filter_doc["$or"] = [
                        {"supernumerary_type": "TFWS"},
                        {"admission_category": "TFWS"},
                        {"tfws_eligible": True}
                    ]
                elif quota == "EWS":
                    filter_doc["$or"] = [
                        {"supernumerary_type": "EWS"},
                        {"admission_category": "EWS"},
                        {"ews_eligible": True}
                    ]
                elif quota == "NRI":
                    filter_doc["nri_category"] = {"$in": ["NRI", "NRI-Sponsored"]}
                elif quota == "OCI":
                    filter_doc["oci_status"] = True
                elif quota == "FN":
                    filter_doc["foreign_national_status"] = True
                elif quota == "Regular":
                    filter_doc["supernumerary_seat"] = False
                    filter_doc["nri_category"] = "Not Applicable"
                    filter_doc["foreign_national_status"] = False
            
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
                    or q in s.get("student_id", "").lower()
                    or q in s.get("institution", "").lower()
                    or q in s.get("email", "").lower()
                    or q in s.get("branch", "").lower()
                ]
            if branch and branch != "All":
                filtered = [s for s in filtered if s.get("branch") == branch]
            if status and status != "All":
                filtered = [s for s in filtered if s.get("status") == status]
            if institution and institution != "All":
                filtered = [s for s in filtered if s.get("institution") == institution or s.get("aicte_id") == institution]
            if quota and quota != "All":
                if quota == "Supernumerary":
                    filtered = [s for s in filtered if s.get("supernumerary_seat") is True]
                elif quota == "TFWS":
                    filtered = [s for s in filtered if s.get("supernumerary_type") == "TFWS" or s.get("admission_category") == "TFWS" or s.get("tfws_eligible") is True]
                elif quota == "EWS":
                    filtered = [s for s in filtered if s.get("supernumerary_type") == "EWS" or s.get("admission_category") == "EWS" or s.get("ews_eligible") is True]
                elif quota == "NRI":
                    filtered = [s for s in filtered if s.get("nri_category") in ["NRI", "NRI-Sponsored"]]
                elif quota == "OCI":
                    filtered = [s for s in filtered if s.get("oci_status") is True]
                elif quota == "FN":
                    filtered = [s for s in filtered if s.get("foreign_national_status") is True]
                elif quota == "Regular":
                    filtered = [s for s in filtered if not s.get("supernumerary_seat") and s.get("nri_category") == "Not Applicable" and not s.get("foreign_national_status")]

            total = len(filtered)
            start = (page - 1) * limit
            return filtered[start:start + limit], total

    def get_all_students_flat(self):
        if self.connected_to_mongo:
            return list(self.db.students.find({}, {"_id": 0}))
        return self.memory_students

    def get_student_by_apaar(self, identifier):
        clean_target = self.clean_id(identifier)
        if self.connected_to_mongo:
            # Match apaar_id or student_id
            found = self.db.students.find_one({
                "$or": [
                    {"apaar_id": identifier},
                    {"student_id": identifier}
                ]
            }, {"_id": 0})
            if not found:
                for s in self.db.students.find({}, {"_id": 0}):
                    if self.clean_id(s.get("apaar_id")) == clean_target or self.clean_id(s.get("student_id")) == clean_target:
                        return s
            return found
        else:
            for s in self.memory_students:
                if (s.get("apaar_id") == identifier or 
                    s.get("student_id") == identifier or 
                    self.clean_id(s.get("apaar_id")) == clean_target or 
                    self.clean_id(s.get("student_id")) == clean_target):
                    return s
            return None

    def add_student(self, student_data):
        clean = self.clean_id(student_data.get("apaar_id", ""))
        if len(clean) == 12 and "-" not in student_data.get("apaar_id", ""):
            student_data["apaar_id"] = f"{clean[:4]}-{clean[4:8]}-{clean[8:]}"

        if not student_data.get("qr_token"):
            student_data["qr_token"] = f"APAAR-AUTH:{clean}:{student_data.get('aicte_id', '1-GEN')}:SEC{clean[-4:]}"
        
        # Ensure standard fields
        student_data.setdefault("abc_credits_total", 24)
        student_data.setdefault("cgpa", 8.5)
        student_data.setdefault("academic_history", [])
        student_data.setdefault("swayam_nptel_credits", [])
        student_data.setdefault("status", "Verified")
        student_data.setdefault("kyc_status", "VERIFIED")
        student_data.setdefault("biometric_verified", True)
        student_data.setdefault("student_consent", True)
        student_data.setdefault("consent_timestamp", datetime.now().isoformat())

        if not student_data.get("degree_certificate"):
            student_data["degree_certificate"] = {
                "certificate_id": f"DEG-{student_data.get('branch', 'ENG')}-{clean[-4:]}",
                "degree_name": student_data.get("program", "Bachelor of Technology"),
                "degree_body": f"{student_data.get('institution', 'AICTE Approved Institute')} & AICTE",
                "class_awarded": "First Class with Distinction",
                "issue_date": datetime.now().strftime("%Y-%m-%d"),
                "chancellor_sign": True,
                "registrar_sign": True
            }

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

        # Update institution enrolment count if found
        self._increment_institution_enrolment(student_data)
        return student_data

    def _increment_institution_enrolment(self, student_data):
        inst_name = student_data.get("institution")
        aicte_id = student_data.get("aicte_id")
        branch = student_data.get("branch")
        is_tfws = (student_data.get("supernumerary_type") == "TFWS" or 
                   student_data.get("admission_category") == "TFWS" or 
                   student_data.get("tfws_eligible") is True)
        is_ews = (student_data.get("supernumerary_type") == "EWS" or 
                  student_data.get("admission_category") == "EWS" or 
                  student_data.get("ews_eligible") is True)
        is_sup = student_data.get("supernumerary_seat") or is_tfws or is_ews
        is_nri = student_data.get("nri_category") in ["NRI", "NRI-Sponsored"]
        is_fn = bool(student_data.get("foreign_national_status") or (student_data.get("passport_country") and student_data.get("passport_country") not in ["None", "India", ""]))

        institutions = self.get_institutions()
        for inst in institutions:
            if inst.get("name") == inst_name or inst.get("aicte_id") == aicte_id:
                inst["actual_enrolment"] = inst.get("actual_enrolment", 0) + 1
                if is_sup:
                    inst["actual_supernumerary"] = inst.get("actual_supernumerary", 0) + 1
                if is_tfws:
                    inst["actual_tfws"] = inst.get("actual_tfws", 0) + 1
                if is_ews:
                    inst["actual_ews"] = inst.get("actual_ews", 0) + 1
                if is_nri:
                    inst["actual_nri"] = inst.get("actual_nri", 0) + 1
                if is_fn:
                    inst["actual_fn"] = inst.get("actual_fn", 0) + 1

                for prog in inst.get("programs", []):
                    if prog.get("branch") == branch or prog.get("program") == student_data.get("program"):
                        prog["actual_enrolment"] = prog.get("actual_enrolment", 0) + 1
                        if is_sup:
                            prog["supernumerary_enrolled"] = prog.get("supernumerary_enrolled", 0) + 1
                        if is_tfws:
                            prog["tfws_enrolled"] = prog.get("tfws_enrolled", 0) + 1
                        if is_ews:
                            prog["ews_enrolled"] = prog.get("ews_enrolled", 0) + 1
                        if is_nri:
                            prog["nri_enrolled"] = prog.get("nri_enrolled", 0) + 1
                        if is_fn:
                            prog["fn_enrolled"] = prog.get("fn_enrolled", 0) + 1

                if self.connected_to_mongo:
                    self.db.institutions.update_one({"aicte_id": inst.get("aicte_id")}, {"$set": inst})
                break

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
    # INSTITUTIONS & INTAKE MANAGEMENT
    # -------------------------------------------------------------
    def get_institutions(self):
        if self.connected_to_mongo:
            return list(self.db.institutions.find({}, {"_id": 0}))
        return self.memory_institutions

    def get_institution_by_id(self, aicte_id):
        institutions = self.get_institutions()
        for inst in institutions:
            if inst.get("aicte_id") == aicte_id or inst.get("name").lower() == str(aicte_id).lower():
                return inst
        return None

    def update_institution_intake(self, aicte_id, updates):
        if self.connected_to_mongo:
            self.db.institutions.update_one({"aicte_id": aicte_id}, {"$set": updates})
        else:
            for inst in self.memory_institutions:
                if inst.get("aicte_id") == aicte_id:
                    inst.update(updates)
                    break
        return True

    # -------------------------------------------------------------
    # AUTOMATED APAAR & INTAKE VALIDATION ENGINE (KEY REQUIREMENT 3)
    # -------------------------------------------------------------
    def validate_student_record(self, record, target_institution=None):
        """
        Validates individual student record for:
        1. Duplicate student records
        2. Invalid/missing APAAR IDs
        3. Admissions exceeding approved intake
        4. Inconsistencies in student data
        5. Potential duplicate enrolment across institutions.
        """
        errors = []
        warnings = []
        apaar_raw = str(record.get("apaar_id", "")).strip()
        clean_apaar = self.clean_id(apaar_raw)

        # 1. Invalid or missing APAAR ID check
        if not apaar_raw:
            errors.append({
                "code": "MISSING_APAAR_ID",
                "field": "apaar_id",
                "message": "APAAR ID is mandatory for AICTE student-level registration."
            })
        elif len(clean_apaar) != 12 or not clean_apaar.isdigit():
            errors.append({
                "code": "INVALID_APAAR_FORMAT",
                "field": "apaar_id",
                "message": f"Invalid APAAR ID '{apaar_raw}'. Must be exactly 12 numeric digits (format: XXXX-XXXX-XXXX)."
            })

        # Find target institution
        inst_name = record.get("institution") or (target_institution.get("name") if target_institution else "")
        all_students = self.get_all_students_flat()

        # 2. Duplicate Student Record check within same institution
        same_inst_dups = [
            s for s in all_students
            if self.clean_id(s.get("apaar_id")) == clean_apaar and clean_apaar and
            (s.get("institution", "").lower() == inst_name.lower() or s.get("aicte_id") == record.get("aicte_id"))
        ]
        if same_inst_dups:
            errors.append({
                "code": "DUPLICATE_STUDENT_RECORD",
                "field": "apaar_id",
                "message": f"Duplicate student record: APAAR ID '{apaar_raw}' is already registered in {inst_name} (Student ID: {same_inst_dups[0].get('student_id')})."
            })

        # 3. Potential Duplicate Enrolment Across Institutions
        cross_inst_dups = [
            s for s in all_students
            if self.clean_id(s.get("apaar_id")) == clean_apaar and clean_apaar and
            s.get("institution", "").lower() != inst_name.lower()
        ]
        if cross_inst_dups:
            errors.append({
                "code": "CROSS_INSTITUTION_DUPLICATE_ENROLMENT",
                "field": "apaar_id",
                "message": f"CRITICAL FRAUD ALERT: Student with APAAR ID '{apaar_raw}' is actively enrolled simultaneously at '{cross_inst_dups[0].get('institution')}' in program '{cross_inst_dups[0].get('program')}'. Dual full-time enrollment is prohibited under AICTE norms."
            })

        # 4. Admissions Exceeding Approved Intake Check
        inst_obj = target_institution
        if not inst_obj and inst_name:
            inst_obj = next((i for i in self.get_institutions() if i.get("name", "").lower() == inst_name.lower() or i.get("aicte_id") == record.get("aicte_id")), None)

        if inst_obj:
            branch_name = record.get("branch", "")
            prog_name = record.get("program", "")
            prog = next((p for p in inst_obj.get("programs", []) if p.get("branch", "").lower() == branch_name.lower() or p.get("program", "").lower() == prog_name.lower()), None)
            
            is_tfws = (record.get("supernumerary_type") == "TFWS" or 
                       record.get("admission_category") == "TFWS" or 
                       record.get("tfws_eligible") is True)
            is_ews = (record.get("supernumerary_type") == "EWS" or 
                      record.get("admission_category") == "EWS" or 
                      record.get("ews_eligible") is True)
            is_supernumerary = bool(record.get("supernumerary_seat") or (record.get("supernumerary_type") and record.get("supernumerary_type") not in ["None", "Regular", ""])) or is_tfws or is_ews
            is_nri = record.get("nri_category") in ["NRI", "NRI-Sponsored"]
            is_fn = bool(record.get("foreign_national_status") or (record.get("passport_country") and record.get("passport_country") not in ["None", "India", ""]))

            if prog:
                appr_intake = prog.get("approved_intake", 60)
                act_enr = prog.get("actual_enrolment", 0)

                # Regular seat check (Standard AICTE 60 seats cutoff per division)
                if not is_supernumerary and not is_nri and not is_fn:
                    if act_enr >= appr_intake:
                        errors.append({
                            "code": "ADMISSION_EXCEEDING_APPROVED_INTAKE",
                            "field": "approved_intake",
                            "message": f"REGULAR INTAKE CUTOFF EXCEEDED: Department '{prog.get('branch', branch_name)}' has reached its AICTE Approved Intake cap of {appr_intake} seats ({act_enr}/{appr_intake} seats filled). Admissions beyond approved cutoff are strictly prohibited."
                        })
                    elif act_enr >= appr_intake - 2:
                        warnings.append({
                            "code": "NEAR_APPROVED_INTAKE_CAP",
                            "field": "approved_intake",
                            "message": f"Department '{prog.get('branch', branch_name)}' is approaching approved intake cutoff ({act_enr}/{appr_intake} seats filled)."
                        })

                # TFWS Quota check (Strictly 5% supernumerary quota = 3 seats for a 60-seat department)
                if is_tfws:
                    tfws_appr = prog.get("tfws_approved", 3)
                    tfws_enr = prog.get("tfws_enrolled", 0)
                    if tfws_enr >= tfws_appr:
                        errors.append({
                            "code": "EXCEEDING_TFWS_QUOTA",
                            "field": "tfws_quota",
                            "message": f"TFWS QUOTA VIOLATION: Exceeds sanctioned 5% Tuition Fee Waiver Scheme capacity ({tfws_enr}/{tfws_appr} seats filled in {prog.get('branch', branch_name)}). Under AICTE norms, TFWS is strictly capped at 5% of approved intake (3 seats per division of 60)."
                        })
                    elif tfws_enr >= tfws_appr - 1:
                        warnings.append({
                            "code": "NEAR_TFWS_QUOTA_CAP",
                            "field": "tfws_quota",
                            "message": f"TFWS quota in {prog.get('branch', branch_name)} is near capacity ({tfws_enr}/{tfws_appr} seats filled)."
                        })

                # EWS Quota check (Strictly 10% supernumerary quota = 6 seats for a 60-seat department)
                if is_ews:
                    ews_appr = prog.get("ews_approved", 6)
                    ews_enr = prog.get("ews_enrolled", 0)
                    if ews_enr >= ews_appr:
                        errors.append({
                            "code": "EXCEEDING_EWS_QUOTA",
                            "field": "ews_quota",
                            "message": f"EWS QUOTA VIOLATION: Exceeds sanctioned 10% Economically Weaker Section supernumerary capacity ({ews_enr}/{ews_appr} seats filled in {prog.get('branch', branch_name)}). Under AICTE norms, EWS is strictly capped at 10% of approved intake (6 seats per division of 60)."
                        })
                    elif ews_enr >= ews_appr - 1:
                        warnings.append({
                            "code": "NEAR_EWS_QUOTA_CAP",
                            "field": "ews_quota",
                            "message": f"EWS quota in {prog.get('branch', branch_name)} is near capacity ({ews_enr}/{ews_appr} seats filled)."
                        })

                # General Supernumerary quota check (Max sanctioned supernumerary ceiling)
                if is_supernumerary and not is_tfws and not is_ews:
                    sup_appr = prog.get("supernumerary_approved", 11)
                    sup_enr = prog.get("supernumerary_enrolled", 0)
                    if sup_enr >= sup_appr:
                        errors.append({
                            "code": "EXCEEDING_SUPERNUMERARY_QUOTA",
                            "field": "supernumerary_seats",
                            "message": f"SUPERNUMERARY QUOTA VIOLATION: Exceeds approved supernumerary capacity ({sup_enr}/{sup_appr} seats filled in {prog.get('branch', branch_name)})."
                        })

                # NRI quota check
                if is_nri:
                    nri_appr = prog.get("nri_approved", 0)
                    nri_enr = prog.get("nri_enrolled", 0)
                    if nri_enr >= nri_appr:
                        errors.append({
                            "code": "EXCEEDING_NRI_QUOTA",
                            "field": "nri_category",
                            "message": f"NRI QUOTA VIOLATION: Exceeds sanctioned 5% NRI seats ({nri_enr}/{nri_appr} filled)."
                        })

                # Foreign National quota check
                if is_fn:
                    fn_appr = prog.get("fn_approved", 0)
                    fn_enr = prog.get("fn_enrolled", 0)
                    if fn_enr >= fn_appr:
                        errors.append({
                            "code": "EXCEEDING_FN_QUOTA",
                            "field": "foreign_national_status",
                            "message": f"FOREIGN NATIONAL QUOTA VIOLATION: Exceeds sanctioned FN seats ({fn_enr}/{fn_appr} filled)."
                        })

        # 5. Inconsistencies in Student Data
        if not record.get("student_id") or not str(record.get("student_id")).strip():
            errors.append({
                "code": "MISSING_STUDENT_ID",
                "field": "student_id",
                "message": "Student Institutional ID (Roll/Registration Number) is required."
            })

        if not record.get("full_name") or len(str(record.get("full_name")).strip()) < 2:
            errors.append({
                "code": "INVALID_STUDENT_NAME",
                "field": "full_name",
                "message": "Valid student full name is required."
            })

        if record.get("foreign_national_status") and (not record.get("passport_country") or record.get("passport_country") in ["None", "India", ""]):
            errors.append({
                "code": "INCONSISTENT_FN_DATA",
                "field": "passport_country",
                "message": "Foreign National status is marked True, but valid passport country is missing."
            })

        if record.get("oci_status") and not record.get("oci_number"):
            warnings.append({
                "code": "INCOMPLETE_OCI_DATA",
                "field": "oci_number",
                "message": "OCI status marked True without OCI card serial number."
            })

        if record.get("supernumerary_seat") and (not record.get("supernumerary_type") or record.get("supernumerary_type") == "None"):
            errors.append({
                "code": "INCONSISTENT_SUPERNUMERARY_DATA",
                "field": "supernumerary_type",
                "message": "Supernumerary seat is marked True, but quota category (TFWS, EWS, PMSSS, Sports) is not specified."
            })

        if is_tfws and not record.get("family_annual_income"):
            warnings.append({
                "code": "TFWS_INCOME_PROOF_PENDING",
                "field": "family_annual_income",
                "message": "Tuition Fee Waiver Scheme (TFWS) requires parental income verification (< ₹8,00,000 p.a.)."
            })

        if is_ews and not record.get("ews_certificate_no"):
            warnings.append({
                "code": "EWS_CERTIFICATE_PENDING",
                "field": "ews_certificate_no",
                "message": "Economically Weaker Section (EWS) reservation requires Tehsildar/Revenue Authority Certificate No."
            })

        if record.get("student_consent") is False:
            errors.append({
                "code": "CONSENT_NOT_GRANTED",
                "field": "student_consent",
                "message": "Mandatory student consent under Digital Personal Data Protection Act is not granted."
            })

        is_valid = len(errors) == 0
        return {
            "is_valid": is_valid,
            "status": "VALID" if is_valid else "INVALID",
            "errors": errors,
            "warnings": warnings,
            "record": record
        }

    def validate_batch(self, batch_records, target_institution=None):
        results = []
        valid_count = 0
        flagged_count = 0

        for r in batch_records:
            val = self.validate_student_record(r, target_institution)
            if val["is_valid"]:
                valid_count += 1
            else:
                flagged_count += 1
            results.append(val)

        return {
            "total_submitted": len(batch_records),
            "valid_count": valid_count,
            "flagged_count": flagged_count,
            "results": results
        }

    def submit_institution_admissions(self, records, target_institution=None, user=None):
        validation = self.validate_batch(records, target_institution)
        saved_records = []
        flagged_records = []

        actor_name = user.get("name", "Institution Operator") if user else "Institution Registrar"
        inst_name = target_institution.get("name", "AICTE Approved Institution") if target_institution else "AICTE Approved Institution"

        for item in validation["results"]:
            if item["is_valid"]:
                created = self.add_student(item["record"])
                saved_records.append(created)
            else:
                flagged_records.append(item)

        # Log audit trail
        self.log_audit(
            action="BATCH_ADMISSION_INGESTION",
            actor_name=actor_name,
            actor_role=user.get("role", "INSTITUTION_VERIFIER") if user else "INSTITUTION_VERIFIER",
            institution=inst_name,
            details=f"Processed {len(records)} post-admission records: {len(saved_records)} admitted to Central Repository, {len(flagged_records)} flagged for validation errors.",
            status="SUCCESS" if len(flagged_records) == 0 else "PARTIAL_WARNING"
        )

        return {
            "success": True,
            "total_submitted": len(records),
            "saved_count": len(saved_records),
            "flagged_count": len(flagged_records),
            "saved_records": saved_records,
            "flagged_records": flagged_records
        }

    # -------------------------------------------------------------
    # AUDIT TRAILS & VERIFICATION LOGS (KEY REQUIREMENTS 5 & 8)
    # -------------------------------------------------------------
    def log_audit(self, action, actor_name, actor_role, institution, details, status="SUCCESS"):
        entry = {
            "id": f"AUD-{int(datetime.now().timestamp() * 1000) % 100000}",
            "action": action,
            "actor_name": actor_name,
            "actor_role": actor_role,
            "institution": institution,
            "details": details,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        if self.connected_to_mongo:
            self.db.audit_logs.insert_one(dict(entry))
        else:
            self.memory_audit_logs.insert(0, entry)
        return entry

    def get_audit_logs(self, limit=30):
        if self.connected_to_mongo:
            return list(self.db.audit_logs.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit))
        return self.memory_audit_logs[:limit]

    def log_verification(self, apaar_id, student_name, institution, status, details, verifier="Authorized Scanner"):
        entry = {
            "id": f"VER-{int(datetime.now().timestamp() * 1000) % 100000}",
            "apaar_id": apaar_id,
            "student_name": student_name,
            "institution": institution,
            "status": status,
            "verifier": verifier,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        if self.connected_to_mongo:
            self.db.verifications.insert_one(dict(entry))
        else:
            self.memory_verifications.insert(0, entry)

        # Mirror in audit log
        self.log_audit(
            action="STAKEHOLDER_VERIFICATION",
            actor_name=verifier,
            actor_role="AUTHORIZED_VERIFIER",
            institution=institution,
            details=f"Verification query for APAAR ID {apaar_id} ({student_name}). Status: {status}",
            status="SUCCESS" if "SUCCESS" in status else "ALERT"
        )
        return entry

    def get_verifications(self, limit=30):
        if self.connected_to_mongo:
            return list(self.db.verifications.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit))
        return self.memory_verifications[:limit]

    # -------------------------------------------------------------
    # ADMISSION ANALYTICS & MONITORING (KEY REQUIREMENTS 4 & 9)
    # -------------------------------------------------------------
    def get_analytics(self):
        students = self.get_all_students_flat()
        institutions = self.get_institutions()

        total_students = len(students)
        verified_count = sum(1 for s in students if s.get("status") == "Verified")
        flagged_count = sum(1 for s in students if s.get("status") == "Flagged")

        # Quota breakdowns
        tfws_count = sum(1 for s in students if s.get("supernumerary_type") == "TFWS" or s.get("admission_category") == "TFWS" or s.get("tfws_eligible") is True)
        ews_count = sum(1 for s in students if s.get("supernumerary_type") == "EWS" or s.get("admission_category") == "EWS" or s.get("ews_eligible") is True)
        supernumerary_count = sum(1 for s in students if s.get("supernumerary_seat") is True or s.get("supernumerary_type") in ["TFWS", "EWS", "PMSSS", "Sports", "KM"])
        nri_count = sum(1 for s in students if s.get("nri_category") in ["NRI", "NRI-Sponsored"])
        oci_count = sum(1 for s in students if s.get("oci_status") is True)
        fn_count = sum(1 for s in students if s.get("foreign_national_status") is True)

        # Capacity & Intake calculations
        total_approved_intake = sum(i.get("approved_intake", 0) for i in institutions)
        total_actual_enrolment = sum(i.get("actual_enrolment", 0) for i in institutions)
        total_supernumerary_quota = sum(i.get("supernumerary_quota", 0) for i in institutions)
        total_tfws_quota = sum(sum(p.get("tfws_approved", 3) for p in i.get("programs", [])) for i in institutions)
        total_tfws_enrolled = sum(sum(p.get("tfws_enrolled", 0) for p in i.get("programs", [])) for i in institutions)
        total_ews_quota = sum(sum(p.get("ews_approved", 6) for p in i.get("programs", [])) for i in institutions)
        total_ews_enrolled = sum(sum(p.get("ews_enrolled", 0) for p in i.get("programs", [])) for i in institutions)

        # Excess Admissions Detection
        excess_intake_institutions = [
            i for i in institutions 
            if i.get("actual_enrolment", 0) > i.get("approved_intake", 0) or i.get("intake_status") == "VIOLATION_EXCESS_INTAKE"
        ]

        total_credits = sum(s.get("abc_credits_total", 0) for s in students)

        branch_dist = {}
        for s in students:
            b = s.get("branch", "Other")
            branch_dist[b] = branch_dist.get(b, 0) + 1

        recent_verifications = self.get_verifications(limit=6)
        audit_logs = self.get_audit_logs(limit=8)

        return {
            "total_students": total_students,
            "verified_count": verified_count,
            "flagged_fraud_count": flagged_count,
            "total_approved_intake": total_approved_intake,
            "total_actual_enrolment": total_actual_enrolment,
            "intake_utilization_rate": round((total_actual_enrolment / max(1, total_approved_intake)) * 100, 1),
            "supernumerary_count": supernumerary_count,
            "supernumerary_quota_total": total_supernumerary_quota,
            "tfws_count": tfws_count,
            "tfws_quota_total": total_tfws_quota,
            "tfws_enrolled_total": total_tfws_enrolled,
            "ews_count": ews_count,
            "ews_quota_total": total_ews_quota,
            "ews_enrolled_total": total_ews_enrolled,
            "nri_count": nri_count,
            "oci_count": oci_count,
            "fn_count": fn_count,
            "excess_intake_violations": len(excess_intake_institutions),
            "excess_institutions": excess_intake_institutions,
            "compliance_rate": round((verified_count / max(1, total_students)) * 100, 1),
            "total_abc_credits": total_credits,
            "branch_distribution": branch_dist,
            "recent_verifications": recent_verifications,
            "audit_logs": audit_logs,
            "institutions_count": len(institutions)
        }

    # -------------------------------------------------------------
    # REGULATORY & POLICY REPORTS GENERATION (KEY REQUIREMENT 9)
    # -------------------------------------------------------------
    def generate_admissions_report(self, report_type="COMPREHENSIVE"):
        institutions = self.get_institutions()
        students = self.get_all_students_flat()

        rows = []
        for inst in institutions:
            appr = inst.get("approved_intake", 0)
            enr = inst.get("actual_enrolment", 0)
            diff = enr - appr
            status = "COMPLIANT" if diff <= 0 else f"VIOLATION (+{diff} EXCESS SEATS)"
            
            # Aggregate TFWS and EWS for this institution
            inst_tfws_appr = sum(p.get("tfws_approved", 3) for p in inst.get("programs", []))
            inst_tfws_enr = sum(p.get("tfws_enrolled", 0) for p in inst.get("programs", []))
            inst_ews_appr = sum(p.get("ews_approved", 6) for p in inst.get("programs", []))
            inst_ews_enr = sum(p.get("ews_enrolled", 0) for p in inst.get("programs", []))

            rows.append({
                "aicte_id": inst.get("aicte_id"),
                "institution_name": inst.get("name"),
                "state": inst.get("state"),
                "category": inst.get("category"),
                "approved_intake": appr,
                "actual_enrolment": enr,
                "vacancy_or_excess": diff,
                "tfws_approved": inst_tfws_appr,
                "tfws_enrolled": inst_tfws_enr,
                "ews_approved": inst_ews_appr,
                "ews_enrolled": inst_ews_enr,
                "supernumerary_enrolled": inst.get("actual_supernumerary", 0),
                "supernumerary_quota": inst.get("supernumerary_quota", 0),
                "nri_enrolled": inst.get("actual_nri", 0),
                "fn_enrolled": inst.get("actual_fn", 0),
                "compliance_status": status,
                "compliance_score": inst.get("compliance_score", 95.0)
            })

        return {
            "report_id": f"REP-AICTE-{datetime.now().strftime('%Y%m%d')}",
            "generated_at": datetime.now().isoformat(),
            "report_type": report_type,
            "total_institutions_audited": len(institutions),
            "total_students_enrolled": len(students),
            "data": rows
        }


db_manager = DatabaseManager()
