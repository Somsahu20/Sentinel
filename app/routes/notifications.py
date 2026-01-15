from fastapi import Response, HTTPException, Depends, APIRouter
from ..db.notifications import NotificationSend, NotificationResponse
from ..db.sessions import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_422_UNPROCESSABLE_CONTENT
from ..models.notifications import Notification
from sqlalchemy import select
from typing import List
from pydantic import ValidationError
from ..redis.notificationredis import push_to_queue, logger

router = APIRouter()

@router.get('/db')
async def start_func(db: AsyncSession = Depends(get_db)):
    return {"message": "Successfully connected"}

@router.get('/notifications', response_model=List[NotificationResponse])
async def get_all_notifications(db: AsyncSession = Depends(get_db)):

    try:
        stmt = select(Notification)
        result = (await db.execute(stmt)).scalars().all()

        return result


    except Exception as err:
        print(f"Error is {err}")
        raise HTTPException(status_code=500, detail=f'Error at get_all_funcctions.')
    
@router.post('/notifications', response_model=NotificationResponse)
async def send_notification(res: Response, notif: NotificationSend, db: AsyncSession = Depends(get_db)):
    try:
        noti_dict = notif.model_dump()
        noti_send = Notification(**noti_dict)
        db.add(noti_send)
        await db.commit()
        await db.refresh(noti_send)

        try:
            pydantic_obj = NotificationResponse.model_validate(noti_send)
            push_to_queue(pydantic_obj)
        except Exception as err:
            logger.error(f"there is an error {err}")

        res.status_code = HTTP_201_CREATED
        
        return noti_send
    
    except ValidationError:
        await db.rollback()
        raise HTTPException(status_code=HTTP_422_UNPROCESSABLE_CONTENT, detail='Please fill all the details carefully')
    
    except Exception as err:
        await db.rollback()
        print(f"Error at send_notification\n, error is {err}")
        raise HTTPException(status_code=500, detail="Sorry couldn\'t send the notitication")