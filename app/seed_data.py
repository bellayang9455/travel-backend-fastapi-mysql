from sqlalchemy.orm import Session
from . import models
from .utils import gen_uuid

def seed(db: Session):
    # check if already seeded
    if db.query(models.User).first():
        return

    u1 = models.User(
        id=gen_uuid(),
        email="lin@example.com",
        password_hash="demo",
        name="小林",
    )
    u2 = models.User(
        id=gen_uuid(),
        email="mei@example.com",
        password_hash="demo",
        name="小美",
    )
    db.add_all([u1, u2])
    db.flush()

    s1 = models.Spot(
        id=gen_uuid(),
        name="九份老街",
        category="文化",
        features={"features": ["老街", "小吃"]},
        location="新北",
        hours="10:00-20:00",
        activities={"activities": ["茶館", "拍照"]},
    )
    s2 = models.Spot(
        id=gen_uuid(),
        name="太魯閣國家公園",
        category="自然",
        features={"features": ["峽谷", "步道"]},
        location="花蓮",
        hours="全天",
        activities={"activities": ["健行"]},
    )
    db.add_all([s1, s2])
    db.flush()

    it1 = models.Itinerary(
        id=gen_uuid(),
        code="TRIP-2025-0001",
        title="東部三日遊",
        budget=12000,
        travel_time="3天2夜",
        lodging="青年旅館",
        transport="火車+租車",
        owner_user_id=u1.id,
    )
    db.add(it1)
    db.flush()

    is_rel = models.ItinerarySpot(
        itinerary_id=it1.id,
        spot_id=s2.id,
        day_order=1,
    )
    db.add(is_rel)

    review = models.Review(
        id=gen_uuid(),
        user_id=u2.id,
        spot_id=s2.id,
        stars=5,
        content="太魯閣超壯觀！注意安全。",
    )
    db.add(review)

    tr = models.TravelRecord(
        id=gen_uuid(),
        user_id=u1.id,
        itinerary_id=it1.id,
        experience="第一次到花蓮自駕。",
        cost_ticket=1200,
        cost_lodging=1600,
        cost_food=900,
        cost_transport=1800,
    )
    db.add(tr)

    db.commit()
