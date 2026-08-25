from fastapi import APIRouter, HTTPException

from app.schemas.topic import TopicCreate, TopicOut
from app.services import topic_service

router = APIRouter(prefix="/topics", tags=["Topics"])


@router.get("/", response_model=list[TopicOut])
async def list_topics():
    return await topic_service.list_topics()


@router.get("/{topic_id}", response_model=TopicOut)
async def get_topic(topic_id: int):
    topic = await topic_service.get_topic(topic_id)
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic


@router.get("/subject/{subject_id}", response_model=list[TopicOut])
async def get_subject_topics(subject_id: int):
    return await topic_service.list_topics_for_subject(subject_id)


@router.post("/", response_model=TopicOut, status_code=201)
async def create_topic(payload: TopicCreate):
    return await topic_service.register_topic(
        payload.subject_id, payload.name, payload.difficulty, payload.estimated_hours
    )
