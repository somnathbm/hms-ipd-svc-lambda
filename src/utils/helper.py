import os
from uuid import uuid4
from datetime import datetime, UTC
from pymongo import MongoClient

client = MongoClient(host=os.environ.get("DB_URI"))

# Create new admission into emergency ward
def create_new_ipd_admission(patient_id: str):
  """Create new admission into emergency ward"""
  try:
    # check patient info from the patient mgmt database
    # if record exists, then proceed
    # otherwise notify the reason in the response
    db_name: str = os.environ.get("DB_NAME")
    emg_dept_collection: str = os.environ.get("EMG_DEPT_COLLECTION")
    pmgmt_collection: str = os.environ.get("PMGMT_COLLECTION")

    lookup_result = lookup_patient(patient_id, db_name, pmgmt_collection)
    # print(lookup_result)
    if lookup_result is None:
      return {"error": True, "reason": f"No patient found with patient id {patient_id}"}
    
    medical_data = lookup_result["medical_info"]
    patient_basic_data = lookup_result["basic_info"]

    # create emergency admission
    # prepare the payload
    payload = {
      "admission_id": str(uuid4()),
      "admitted_on": datetime.now(UTC),
      "patient_id": patient_id,
      "patient_name": patient_basic_data["name"],
      "department": medical_data["department"],
      "history": medical_data["history"],
      "illness_primary": medical_data["illness_primary"]
    }

    insert_ok = client[db_name][emg_dept_collection].insert_one(payload).acknowledged
    if not insert_ok:
      return {"error": True, "reason": "db insertion failure"}
    return {"error": False, "status": "ok", "data": lookup_result}
  except Exception as err:
    raise err
  

# Lookup patient info
def lookup_patient(patient_id: str, db_name: str, patient_mgmt_collection_name: str):
  """Lookup patient info"""
  try:
    patient_mgmt_collection = client[db_name][patient_mgmt_collection_name]
    result = patient_mgmt_collection.find_one({"medical_info.patientId": patient_id}, {"_id": 0})
    return result
  except Exception as err:
    raise err
