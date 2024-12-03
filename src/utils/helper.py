import os
from uuid import uuid4
from datetime import datetime, UTC
from pymongo import MongoClient

client = MongoClient(host=os.environ.get("DB_URI"))
db_name: str = os.environ.get("DB_NAME")
ipd_dept_collection: str = os.environ.get("IPD_DEPT_COLLECTION")
ipd_wards_collection: str = os.environ.get("IPD_WARDS_COLLECTION")
pmgmt_collection: str = os.environ.get("PMGMT_COLLECTION")
doctors_collection: str = os.environ.get("DOCTORS_COLLECTION")

# Create new admission into IPD ward
def create_new_ipd_admission(patient_id: str):
  """Create new admission into IPD ward"""
  try:
    # check patient info from the patient mgmt database
    # if record exists, then proceed
    # otherwise notify the reason in the response

    lookup_result = lookup_patient(patient_id)
    # print(lookup_result)
    if lookup_result is None:
      return {"error": True, "reason": f"No patient found with patient id {patient_id}"}
    
    medical_data = lookup_result["medical_info"]
    patient_basic_data = lookup_result["basic_info"]

    # determine the target ward
    target_ward: map = assign_ward(medical_data["illness_primary"])
    target_ward_name: str = target_ward["ward"]
    assigned_doctor: map = assign_doctor(target_ward_name)

    # create the admisison id
    admission_id: str = str(uuid4())

    # create emergency admission
    # prepare the payload
    payload = {
      "admission_id": admission_id,
      "admitted_on": datetime.now(UTC),
      "patient_id": patient_id,
      "assigned_doctor": {
        "doctor_id": assigned_doctor["doctor_id"],
        "doctor_name": assigned_doctor["doctor_name"]
      },
      "patient_name": patient_basic_data["name"],
      "department": medical_data["department"],
      "history": medical_data["history"],
      "illness_primary": medical_data["illness_primary"]
    }

    insert_ok = client[db_name][ipd_dept_collection].insert_one(payload).acknowledged
    if not insert_ok:
      return {"error": True, "reason": "db insertion failure"}
    return {"error": False, "status": "ok", "data": {"admission_id": admission_id}}
  except Exception as err:
    raise err
  

# Lookup patient info
def lookup_patient(patient_id: str):
  """Lookup patient info"""
  try:
    patient_mgmt_collection = client[db_name][pmgmt_collection]
    result = patient_mgmt_collection.find_one({"medical_info.patientId": patient_id}, {"_id": 0})
    return result
  except Exception as err:
    raise err


# Get current date for today in the format YYYY-MM-DD
def get_today(datetime: datetime) -> str:
  """Get current date for today in the format YYYY-MM-DD"""
  return f"{datetime.year}-{datetime.month}-{datetime.day}"


# Assign ward to the new IPD patient
def assign_ward(patient_illness: str) -> dict[str, any]:
  """Assign ward to the new IPD patient"""
  try:
    wards_cursor = client[db_name][ipd_wards_collection].find({}, {"_id": 0})
    available_ward_list_map = [ward for ward in wards_cursor]
    ward_result = [{"ward": ward_map["ward"]} for ward_map in available_ward_list_map if any([condition for condition in ward_map["patient_condition_keywords"] if condition in patient_illness])]
    return ward_result[0]
  except Exception as err:
    raise err


# Assign available doctors from the doctors pool
def assign_doctor(ward: str) -> dict[str, any]:
  """Assign available doctors from the doctors pool"""
  try:
    doctors_cursor = client[db_name][doctors_collection].find({}, {"_id": 0})
    available_doctors_list_map = [doctor for doctor in doctors_cursor]
    return [doctor for doctor in available_doctors_list_map if doctor["department"] == ward and get_today(datetime.now()) not in doctor["unavailable_dates"]][0]
  except Exception as err:
    raise err
