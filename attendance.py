import json
import csv
import os
from datetime import datetime, date
from pathlib import Path

# ============================================
# Attendance System CLI
# Day 41 — 120 Days of Code | NIT Rourkela
# ============================================

DATA_FILE = "attendance.json"
MIN_ATTENDANCE = 75.0

def load_data():
    if Path(DATA_FILE).exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"subjects": {}, "records": []}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_percentage(present, total):
    return (present / total * 100) if total > 0 else 0

def get_status(pct):
    if pct >= 85: return "✅ Good"
    if pct >= 75: return "⚠️  Safe"
    return "❌ Low"

def header(title):
    print("\n" + "=" * 55)
    print(f"  {title}")
    print("=" * 55)

def add_subject(data):
    header("Add Subject")
    name = input("  Subject name: ").strip()
    if not name:
        print("  ❌ Name cannot be empty!")
        return
    if name in data["subjects"]:
        print(f"  ❌ {name} already exists!")
        return
    code = input("  Subject code (e.g. ME301): ").strip()
    credits = input("  Credits: ").strip()
    data["subjects"][name] = {
        "code": code,
        "credits": credits,
        "total": 0,
        "present": 0
    }
    save_data(data)
    print(f"  ✅ Subject '{name}' added!")

def mark_attendance(data):
    if not data["subjects"]:
        print("\n  ❌ No subjects added yet!")
        return

    header("Mark Attendance")
    today = date.today().strftime("%Y-%m-%d")
    print(f"  Date: {today}\n")

    already_marked = [
        r["subject"] for r in data["records"]
        if r["date"] == today
    ]

    subjects = list(data["subjects"].keys())
    for i, sub in enumerate(subjects, 1):
        status = "(already marked today)" if sub in already_marked else ""
        print(f"  {i}. {sub} {status}")

    print("\n  Enter subject number (or 'all' to mark all):")
    choice = input("  Choice: ").strip().lower()

    to_mark = []
    if choice == 'all':
        to_mark = [s for s in subjects if s not in already_marked]
    else:
        try:
            idx = int(choice) - 1
            sub = subjects[idx]
            if sub in already_marked:
                print(f"  ⚠️  {sub} already marked today!")
                return
            to_mark = [sub]
        except (ValueError, IndexError):
            print("  ❌ Invalid choice!")
            return

    for sub in to_mark:
        att = input(f"  {sub} — Present? (p/a): ").strip().lower()
        is_present = att == 'p'
        data["subjects"][sub]["total"] += 1
        if is_present:
            data["subjects"][sub]["present"] += 1

        data["records"].append({
            "date": today,
            "subject": sub,
            "status": "present" if is_present else "absent"
        })
        print(f"  {'✅ Present' if is_present else '❌ Absent'} marked for {sub}")

    save_data(data)
    print("\n  ✅ Attendance saved!")

def view_attendance(data):
    if not data["subjects"]:
        print("\n  ❌ No subjects added yet!")
        return

    header("Attendance Summary")
    print(f"  {'Subject':<25} {'Code':<8} {'P/T':<10} {'%':<8} {'Status'}")
    print("  " + "-" * 53)

    warnings = []
    for name, sub in data["subjects"].items():
        total = sub["total"]
        present = sub["present"]
        pct = get_percentage(present, total)
        status = get_status(pct)

        print(f"  {name:<25} {sub['code']:<8} {present}/{total:<8} {pct:.1f}%{'':<3} {status}")

        if pct < MIN_ATTENDANCE and total > 0:
            classes_needed = 0
            while get_percentage(present + classes_needed, total + classes_needed) < MIN_ATTENDANCE:
                classes_needed += 1
            warnings.append((name, pct, classes_needed))

    if warnings:
        print("\n  ⚠️  LOW ATTENDANCE WARNINGS:")
        for name, pct, needed in warnings:
            print(f"  {name}: {pct:.1f}% — Attend {needed} more class(es) to reach 75%")

def view_by_subject(data):
    if not data["subjects"]:
        print("\n  ❌ No subjects added yet!")
        return

    header("View by Subject")
    subjects = list(data["subjects"].keys())
    for i, s in enumerate(subjects, 1):
        print(f"  {i}. {s}")

    try:
        idx = int(input("\n  Select subject: ").strip()) - 1
        sub_name = subjects[idx]
    except (ValueError, IndexError):
        print("  ❌ Invalid choice!")
        return

    sub = data["subjects"][sub_name]
    records = [r for r in data["records"] if r["subject"] == sub_name]

    header(f"Records — {sub_name}")
    print(f"  Code    : {sub['code']}")
    print(f"  Credits : {sub['credits']}")
    print(f"  Present : {sub['present']}/{sub['total']}")
    pct = get_percentage(sub["present"], sub["total"])
    print(f"  %       : {pct:.1f}% {get_status(pct)}")

    if records:
        print(f"\n  Recent Records (last 10):")
        print(f"  {'Date':<14} {'Status'}")
        print("  " + "-" * 25)
        for r in records[-10:]:
            icon = "✅" if r["status"] == "present" else "❌"
            print(f"  {r['date']:<14} {icon} {r['status']}")

def export_report(data):
    if not data["subjects"]:
        print("\n  ❌ No data to export!")
        return

    filename = f"attendance_report_{date.today().strftime('%Y%m%d')}.csv"
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Subject", "Code", "Credits",
                         "Total Classes", "Present", "Absent", "Percentage", "Status"])
        for name, sub in data["subjects"].items():
            total = sub["total"]
            present = sub["present"]
            absent = total - present
            pct = get_percentage(present, total)
            writer.writerow([
                name, sub["code"], sub["credits"],
                total, present, absent,
                f"{pct:.1f}%", get_status(pct).replace("✅","").replace("⚠️","").replace("❌","").strip()
            ])

    print(f"\n  ✅ Report exported to {filename}")

def delete_subject(data):
    if not data["subjects"]:
        print("\n  ❌ No subjects to delete!")
        return

    header("Delete Subject")
    subjects = list(data["subjects"].keys())
    for i, s in enumerate(subjects, 1):
        print(f"  {i}. {s}")

    try:
        idx = int(input("\n  Select subject to delete: ").strip()) - 1
        sub_name = subjects[idx]
    except (ValueError, IndexError):
        print("  ❌ Invalid choice!")
        return

    confirm = input(f"  Delete '{sub_name}'? (yes/no): ").strip().lower()
    if confirm == 'yes':
        del data["subjects"][sub_name]
        data["records"] = [r for r in data["records"]
                          if r["subject"] != sub_name]
        save_data(data)
        print(f"  ✅ '{sub_name}' deleted!")

def view_today(data):
    today = date.today().strftime("%Y-%m-%d")
    records = [r for r in data["records"] if r["date"] == today]

    header(f"Today's Attendance — {today}")
    if not records:
        print("  No attendance marked today yet.")
        return

    for r in records:
        icon = "✅" if r["status"] == "present" else "❌"
        print(f"  {icon} {r['subject']} — {r['status']}")

def main():
    data = load_data()

    while True:
        header("Attendance System — Day 41 of 120")
        print("  1. Add subject")
        print("  2. Mark attendance")
        print("  3. View summary")
        print("  4. View by subject")
        print("  5. Today's attendance")
        print("  6. Export CSV report")
        print("  7. Delete subject")
        print("  8. Exit")

        choice = input("\n  Choose (1-8): ").strip()

        if choice == '1': add_subject(data)
        elif choice == '2': mark_attendance(data)
        elif choice == '3': view_attendance(data)
        elif choice == '4': view_by_subject(data)
        elif choice == '5': view_today(data)
        elif choice == '6': export_report(data)
        elif choice == '7': delete_subject(data)
        elif choice == '8':
            print("\n  Goodbye! Keep attending classes! 📚")
            break
        else:
            print("  ❌ Invalid choice!")

main()