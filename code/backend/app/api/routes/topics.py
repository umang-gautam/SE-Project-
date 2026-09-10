from fastapi import APIRouter, HTTPException, status
from app.services import topic_service
from app.schemas.topic import TopicCreate, TopicUpdate, TopicResponse

router = APIRouter()

@router.post("/", response_model=TopicResponse, status_code=status.HTTP_201_CREATED)
async def create_topic(topic_in: TopicCreate):
    return await topic_service.create_topic(topic_in.model_dump(exclude_unset=True))

@router.get("/", response_model=list[TopicResponse])
async def list_topics():
    return await topic_service.get_topics()

@router.get("/by-subject/{subject_id}", response_model=list[TopicResponse])
async def get_topics_by_subject(subject_id: str):
    return await topic_service.get_topics_by_subject(subject_id)

@router.get("/{topic_id}", response_model=TopicResponse)
async def get_topic(topic_id: str):
    topic = await topic_service.get_topic(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

@router.patch("/{topic_id}", response_model=TopicResponse)
async def update_topic(topic_id: str, topic_in: TopicUpdate):
    updated = await topic_service.update_topic(topic_id, topic_in.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Topic not found")
    return updated

@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(topic_id: str):
    success = await topic_service.delete_topic(topic_id)
    if not success:
        raise HTTPException(status_code=404, detail="Topic not found")
