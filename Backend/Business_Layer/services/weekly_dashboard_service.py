from collections import defaultdict
from datetime import date, datetime
from Backend.DAL.dao.weekly_dashboard_dao import get_dashboard_data_from_db
from Backend.Business_Layer.utils.date_utils import get_date_range
from datetime import timedelta

async def get_dashboard_data(db,start_date: date, end_date: date ):

    # start_date, end_date = get_date_range(range_type)
    offers = await get_dashboard_data_from_db(db, start_date, end_date)

    today = date.today()
    
    # ================= FIXED SUMMARY =================
    summary = {
        "selected": 0,
        "offersMade": 0,
        "joined": 0,
        "dropOffs": 0,
        "pending": 0
    }

    weekly = defaultdict(lambda:{"completed": 0, "joining": 0})
    monthly = defaultdict(lambda:{"completed": 0, "joining": 0})

    candidates = []

    def resolve_department_name(emp, department_name):
        joined_department_name = (
            department_name.strip()
            if isinstance(department_name, str) and department_name.strip()
            else None
        )
        if joined_department_name:
            return joined_department_name

        employee_department = getattr(emp, "departments", None) if emp else None
        employee_department_name = getattr(employee_department, "department_name", None)
        if isinstance(employee_department_name, str) and employee_department_name.strip():
            return employee_department_name.strip()

        return "N/A"

    # ================= MAIN LOOP =================
    for o, emp, department_name in offers:

        if not o.joining_date:
            continue

        # ✅ RANGE FILTER
        if not (start_date <= o.joining_date <= end_date):
            continue

        #  DYNAMIC STATUS
        status = (o.status or "").strip().lower()

        if status == "completed":
            status = "Completed"
        else:
            status = "Joining"

        # ================= KPI =================
        if status == "Completed":
            summary["joined"] += 1
        else:
            summary["pending"] += 1

        # ================= WEEKLY =================
        day = o.joining_date.strftime("%a")

        # ================= MONTHLY =================
        month_start = o.joining_date.replace(day=1)
        week_index = (o.joining_date.day - 1) // 7

        week_start = month_start + timedelta(days=week_index * 7)
        week_end = week_start + timedelta(days=6)

        label = f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d')}"

        if status == "Completed":
            weekly[day]["completed"] += 1
            monthly[label]["completed"] += 1
        else:
            weekly[day]["joining"] += 1
            monthly[label]["joining"] += 1
        # ================= TABLE =================
        candidates.append({
            "name": f"{o.first_name} {o.last_name}",
            "role": o.designation,
            "department": resolve_department_name(emp, department_name),
            "joiningDate": str(o.joining_date),
            "status": status
        })

    # ================= OUTPUT =================
    day_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for day in day_order:
        if day not in weekly:
            weekly[day] = {"completed": 0, "joining": 0}
    weekly_output = [
        {
            "day": day,
            "completed": weekly[day]["completed"],
            "joining": weekly[day]["joining"]
        }
        for day in day_order
    ]
    month_start = today.replace(day=1)

    for i in range(5):
        week_start = month_start + timedelta(days=i * 7)
        week_end = week_start + timedelta(days=6)

        label = f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d')}"

        if label not in monthly:
            monthly[label] = {"completed": 0, "joining": 0}
    monthly_output = sorted(
    [
        {
            "week": k,
            "completed": v["completed"],
            "joining": v["joining"]
        }
        for k, v in monthly.items()
    ],
    key=lambda x: datetime.strptime(x["week"].split(" - ")[0], "%b %d")
    )
    # ================= ACTIVITIES =================
    activities_sorted = sorted(
        candidates,
        key=lambda x: x["joiningDate"],
        reverse=True
    )[:6]

    activities_output = [
        {
            "message": (
                f"{c['name']} completed joining for {c['role']}."
                if c["status"] == "Completed"
                else f"{c['name']} is scheduled for joining as {c['role']}."
            ),
            "type": c["status"],   
            "time": c["joiningDate"] 
        }
        for c in activities_sorted
    ]

    # ================= FINAL RESPONSE =================
    return {
        "summary": summary,
        "monthlyJoinings": monthly_output,
        "weeklyJoinings": weekly_output,
        "joinedCandidates": candidates,
        "activities": activities_output
    }
