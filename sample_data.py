import json

# Creates sample attendance data for testing
sample = {
  "subjects": {
    "Engineering Mathematics": {
      "code": "MA301", "credits": "4",
      "total": 30, "present": 26
    },
    "Fluid Mechanics": {
      "code": "ME302", "credits": "3",
      "total": 28, "present": 24
    },
    "Thermodynamics": {
      "code": "ME303", "credits": "4",
      "total": 32, "present": 20
    },
    "Manufacturing Processes": {
      "code": "ME304", "credits": "3",
      "total": 25, "present": 23
    },
    "Engineering Drawing Lab": {
      "code": "ME305L", "credits": "2",
      "total": 15, "present": 15
    }
  },
  "records": []
}

with open("attendance.json", "w") as f:
    json.dump(sample, f, indent=2)

print("✅ Sample data created!")
print("Run python3 attendance.py to see it in action.")