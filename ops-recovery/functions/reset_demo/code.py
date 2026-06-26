#input_type_name: ResetDemoInput
#output_type_name: ResetDemoResult
#function_name: reset_demo

"""Reset the demo to a clean, repeatable starting state.

Truncates bookings, recovery_log, comp_ledger, and beauticians, then re-seeds
the Bangalore dataset so every demo run starts identically (recovery scenario
+ escalation scenario both intact).
"""

from lemma_sdk import FunctionContext, Pod
from pydantic import BaseModel

BEAUTICIANS = [
    {"name": "Aarti Sharma", "phone": "+919800000001", "skills": ["Facial", "Manicure", "Waxing"], "city": "Bangalore", "area": "Koramangala", "lat": 12.9352, "lng": 77.6245, "rating": 4.8, "is_available": True, "jobs_today": 2, "max_jobs_per_day": 6, "status": "active"},
    {"name": "Priya Nair", "phone": "+919800000002", "skills": ["Haircut", "Facial"], "city": "Bangalore", "area": "HSR Layout", "lat": 12.9116, "lng": 77.6389, "rating": 4.6, "is_available": True, "jobs_today": 1, "max_jobs_per_day": 6, "status": "active"},
    {"name": "Sneha Reddy", "phone": "+919800000003", "skills": ["Facial", "Bridal Makeup"], "city": "Bangalore", "area": "BTM Layout", "lat": 12.9166, "lng": 77.6101, "rating": 4.9, "is_available": False, "jobs_today": 5, "max_jobs_per_day": 5, "status": "off"},
    {"name": "Kavya Iyer", "phone": "+919800000004", "skills": ["Massage"], "city": "Bangalore", "area": "Koramangala", "lat": 12.9340, "lng": 77.6270, "rating": 4.5, "is_available": True, "jobs_today": 0, "max_jobs_per_day": 5, "status": "active"},
    {"name": "Deepa Menon", "phone": "+919800000005", "skills": ["Haircut", "Waxing"], "city": "Bangalore", "area": "Indiranagar", "lat": 12.9719, "lng": 77.6412, "rating": 4.4, "is_available": True, "jobs_today": 3, "max_jobs_per_day": 6, "status": "active"},
    {"name": "Ritu Singh", "phone": "+919800000006", "skills": ["Manicure", "Waxing", "Facial"], "city": "Bangalore", "area": "HSR Layout", "lat": 12.9100, "lng": 77.6400, "rating": 4.7, "is_available": True, "jobs_today": 2, "max_jobs_per_day": 6, "status": "active"},
    {"name": "Meena Kumari", "phone": "+919800000007", "skills": ["Bridal Makeup", "Facial"], "city": "Bangalore", "area": "Jayanagar", "lat": 12.9250, "lng": 77.5938, "rating": 4.9, "is_available": False, "jobs_today": 4, "max_jobs_per_day": 4, "status": "off"},
    {"name": "Lakshmi Rao", "phone": "+919800000008", "skills": ["Massage", "Facial"], "city": "Bangalore", "area": "BTM Layout", "lat": 12.9170, "lng": 77.6110, "rating": 4.3, "is_available": False, "jobs_today": 5, "max_jobs_per_day": 5, "status": "busy"},
    {"name": "Anjali Gupta", "phone": "+919800000009", "skills": ["Haircut", "Facial", "Manicure"], "city": "Bangalore", "area": "Whitefield", "lat": 12.9698, "lng": 77.7500, "rating": 4.6, "is_available": True, "jobs_today": 1, "max_jobs_per_day": 6, "status": "active"},
    {"name": "Pooja Desai", "phone": "+919800000010", "skills": ["Waxing", "Manicure"], "city": "Bangalore", "area": "Marathahalli", "lat": 12.9569, "lng": 77.7011, "rating": 4.2, "is_available": True, "jobs_today": 0, "max_jobs_per_day": 6, "status": "active"},
]

BOOKINGS = [
    {"customer_name": "Riya Kapoor", "customer_phone": "+919900000001", "service": "Facial at Home", "skill_required": "Facial", "city": "Bangalore", "area": "Koramangala", "lat": 12.9352, "lng": 77.6245, "scheduled_at": "2026-06-26T15:00:00Z", "duration_min": 60, "price": 1200, "status": "scheduled", "notes": "Regular customer, prefers same-day."},
    {"customer_name": "Sara Ali", "customer_phone": "+919900000002", "service": "Bridal Makeup", "skill_required": "Bridal Makeup", "city": "Bangalore", "area": "Whitefield", "lat": 12.9698, "lng": 77.7500, "scheduled_at": "2026-06-26T17:00:00Z", "duration_min": 120, "price": 5000, "status": "scheduled", "notes": "Wedding event - high priority."},
    {"customer_name": "Neha Joshi", "customer_phone": "+919900000003", "service": "Haircut at Home", "skill_required": "Haircut", "city": "Bangalore", "area": "Indiranagar", "lat": 12.9719, "lng": 77.6412, "scheduled_at": "2026-06-26T16:00:00Z", "duration_min": 45, "price": 800, "status": "scheduled", "notes": ""},
    {"customer_name": "Divya Rao", "customer_phone": "+919900000004", "service": "Massage Therapy", "skill_required": "Massage", "city": "Bangalore", "area": "Koramangala", "lat": 12.9340, "lng": 77.6270, "scheduled_at": "2026-06-26T18:00:00Z", "duration_min": 90, "price": 1800, "status": "scheduled", "notes": ""},
    {"customer_name": "Tanvi Shah", "customer_phone": "+919900000005", "service": "Manicure & Pedicure", "skill_required": "Manicure", "city": "Bangalore", "area": "HSR Layout", "lat": 12.9116, "lng": 77.6389, "scheduled_at": "2026-06-26T14:00:00Z", "duration_min": 60, "price": 900, "status": "scheduled", "notes": ""},
    {"customer_name": "Isha Verma", "customer_phone": "+919900000006", "service": "Waxing", "skill_required": "Waxing", "city": "Bangalore", "area": "BTM Layout", "lat": 12.9166, "lng": 77.6101, "scheduled_at": "2026-06-26T19:00:00Z", "duration_min": 45, "price": 700, "status": "scheduled", "notes": ""},
    {"customer_name": "Pooja Hegde", "customer_phone": "+919900000007", "service": "Facial at Home", "skill_required": "Facial", "city": "Bangalore", "area": "Jayanagar", "lat": 12.9250, "lng": 77.5938, "scheduled_at": "2026-06-26T15:30:00Z", "duration_min": 60, "price": 1200, "status": "scheduled", "notes": ""},
    {"customer_name": "Megha Pillai", "customer_phone": "+919900000008", "service": "Haircut at Home", "skill_required": "Haircut", "city": "Bangalore", "area": "Whitefield", "lat": 12.9698, "lng": 77.7500, "scheduled_at": "2026-06-26T17:30:00Z", "duration_min": 45, "price": 800, "status": "scheduled", "notes": ""},
]


class ResetDemoInput(BaseModel):
    confirm: bool = True


class ResetDemoResult(BaseModel):
    ok: bool
    beauticians: int
    bookings: int
    cleared: list[str]


def _truncate(pod: Pod, table: str) -> None:
    while True:
        rows = pod.records.list(table, limit=200).to_dict().get("items", [])
        if not rows:
            break
        pod.records.bulk_delete(table, [r["id"] for r in rows])


async def reset_demo(ctx: FunctionContext, data: ResetDemoInput) -> ResetDemoResult:
    pod = Pod.from_env()
    cleared = ["recovery_log", "comp_ledger", "bookings", "beauticians"]
    for table in cleared:
        _truncate(pod, table)

    n_pros = pod.records.bulk_create("beauticians", BEAUTICIANS)
    n_bookings = pod.records.bulk_create("bookings", BOOKINGS)
    return ResetDemoResult(
        ok=True, beauticians=n_pros, bookings=n_bookings, cleared=cleared
    )
