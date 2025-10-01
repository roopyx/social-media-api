import logging

from fastapi import APIRouter, HTTPException

from api.database import post_table, comment_table, database
from api.models.post import (
    UserPost,
    UserPostIn,
    Comment,
    CommentIn,
    UserPostWithComments
)


router = APIRouter()

logger = logging.getLogger(__name__)


async def find_post(post_id:int):
    query = post_table.select().where(post_table.c.id == post_id)

    logger.debug("Finding post using query: %s", query)

    return await database.fetch_one(query)


@router.post("/post", response_model=UserPost, status_code=201)
async def create_post(post:UserPostIn):
    data = post.model_dump()
    query = post_table.insert().values(data)
    
    logger.debug("Creating post using query: %s", query)
    
    last_record_id = await database.execute(query)
    return { **data, "id": last_record_id }


@router.get("/post", response_model=list[UserPost])
async def get_all_posts():
    query = post_table.select()
    
    logger.debug("Fetching all posts with query: %s", query)

    return await database.fetch_all(query)


@router.post("/comment", response_model=Comment, status_code=201)
async def create_comment(comment:CommentIn):
    post = await find_post(comment.post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    data = comment.model_dump()
    query = comment_table.insert().values(data)

    logger.debug("Creating comment using query: %s", query)

    last_record_id = await database.execute(query)
    return { **data, "id": last_record_id }


@router.get("/post/{post_id}/comment", response_model=list[Comment])
async def get_comments_on_posts(post_id: int):
    query = comment_table.select().where(comment_table.c.post_id == post_id)
    
    logger.debug("Fetching comments for post with query: %s", query)
    
    return await database.fetch_all(query)


@router.get("/post/{post_id}/comments", response_model=UserPostWithComments)
async def get_post_with_comments(post_id: int):
    logger.debug("Fetching post and its comments")

    post = await find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return { "post": post, "comments": await get_comments_on_posts(post_id) }