#input_type_name: MatchProInput
#output_type_name: MatchProResult
#function_name: match_pro

"""Find the best replacement professional for an at-risk booking.

Deterministic ranking: skill match (hard filter) + availability + daily load
(hard filters), then a score over proximity, rating, and spare capacity. Pure
read — it recommends a candidate; the workflow performs the reassignment.
"""

from math import asin, cos, radians, sin, sqrt

from lemma_sdk import FunctionContext, Pod
from pydantic import BaseModel

# Scoring weights (higher score = better candidate).
_W_PROXIMITY = 1.0
_W_RATING = 0.6
_W_CAPACITY = 0.3
# ETA model: base dispatch time plus travel time per km.
_ETA_BASE_MIN = 15.0
_ETA_MIN_PER_KM = 3.0


class MatchProInput(BaseModel):
    booking_id: str


class Candidate(BaseModel):
    pro_id: str
    pro_name: str
    area: str | None = None
    rating: float | None = None
    distance_km: float | None = None
    eta_minutes: int | None = None
    score: float


class MatchProResult(BaseModel):
    matched: bool
    booking_id: str
    skill_required: str | None = None
    candidates_considered: int = 0
    best: Candidate | None = None
    runner_up: Candidate | None = None
    reason: str = ""


def _haversine_km(lat1, lng1, lat2, lng2) -> float | None:
    if None in (lat1, lng1, lat2, lng2):
        return None
    r = 6371.0
    d_lat = radians(lat2 - lat1)
    d_lng = radians(lng2 - lng1)
    a = sin(d_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lng / 2) ** 2
    return round(2 * r * asin(sqrt(a)), 2)


def _score(distance_km, rating, jobs_today, max_jobs, same_area) -> float:
    # Proximity: 1.0 when on top of the customer, decaying with distance.
    prox = 1.0 / (1.0 + (distance_km if distance_km is not None else 8.0))
    rate = (rating or 0.0) / 5.0
    spare = max(0.0, (max_jobs - jobs_today)) / max_jobs if max_jobs else 0.0
    bonus = 0.15 if same_area else 0.0
    return round(_W_PROXIMITY * prox + _W_RATING * rate + _W_CAPACITY * spare + bonus, 4)


def _eta(distance_km) -> int:
    km = distance_km if distance_km is not None else 5.0
    return int(round(_ETA_BASE_MIN + _ETA_MIN_PER_KM * km))


async def match_pro(ctx: FunctionContext, data: MatchProInput) -> MatchProResult:
    pod = Pod.from_env()

    booking = pod.table("bookings").get(data.booking_id)
    if not booking:
        return MatchProResult(
            matched=False, booking_id=data.booking_id, reason="Booking not found."
        )

    skill = booking.get("skill_required")
    b_lat, b_lng = booking.get("lat"), booking.get("lng")
    b_area = booking.get("area")
    original_pro = booking.get("original_pro_id")

    rows = pod.query(
        "SELECT * FROM beauticians WHERE status = 'active' AND is_available = true"
    ).to_dict()["items"]

    ranked: list[Candidate] = []
    for pro in rows:
        if pro.get("id") == original_pro:
            continue
        skills = pro.get("skills") or []
        if skill and skill not in skills:
            continue
        jobs_today = pro.get("jobs_today") or 0
        max_jobs = pro.get("max_jobs_per_day") or 0
        if max_jobs and jobs_today >= max_jobs:
            continue

        distance = _haversine_km(b_lat, b_lng, pro.get("lat"), pro.get("lng"))
        same_area = bool(b_area) and pro.get("area") == b_area
        score = _score(distance, pro.get("rating"), jobs_today, max_jobs, same_area)
        ranked.append(
            Candidate(
                pro_id=pro["id"],
                pro_name=pro.get("name", "Unknown"),
                area=pro.get("area"),
                rating=pro.get("rating"),
                distance_km=distance,
                eta_minutes=_eta(distance),
                score=score,
            )
        )

    ranked.sort(key=lambda c: c.score, reverse=True)

    if not ranked:
        return MatchProResult(
            matched=False,
            booking_id=data.booking_id,
            skill_required=skill,
            candidates_considered=0,
            reason=f"No available '{skill}' professional could be found.",
        )

    best = ranked[0]
    return MatchProResult(
        matched=True,
        booking_id=data.booking_id,
        skill_required=skill,
        candidates_considered=len(ranked),
        best=best,
        runner_up=ranked[1] if len(ranked) > 1 else None,
        reason=(
            f"{best.pro_name} in {best.area} (rating {best.rating}, "
            f"~{best.distance_km} km, ETA ~{best.eta_minutes} min) is the best of "
            f"{len(ranked)} available match(es)."
        ),
    )
