from fastapi import APIRouter, Depends, HTTPException, status, Form, Request, BackgroundTasks
from fastapi.responses import RedirectResponse, JSONResponse
from controller.authController import get_current_user
from database.db import get_db
from model.account import Account
from sqlalchemy.orm import Session
from model.feed import Feed
from model.node import Node
from settings import get_settings
from pydantic import BaseModel

settings = get_settings()

router = APIRouter(
    prefix="/channel",
    tags=['channel']
)

class form_add_feed(BaseModel):
    value: str
    id_node: str
    
async def add_to_db(form_data):
    value = [float(_) for _ in form_data.value.split(',')]
    # len_node_object = await Feed.get_len(form_data.id_node)
    # len_node = len(len_node_object[0].get('field_sensor'))
    # if len_node == len(value):
    if await Feed.create(form_data.id_node, form_data.value):
        print('Success')
    else:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail="error when create",
        )
    # else:
    #     raise HTTPException(
    #         status_code = status.HTTP_400_BAD_REQUEST,
    #         detail="len musth be same",
    #     )
    # except Exception as e:
    #     raise HTTPException(
    #         status_code = status.HTTP_400_BAD_REQUEST,
    #         detail=e,
    #     )

@router.post('/')
async def create(form_data: form_add_feed, akun : Account = Depends(get_current_user)):
    if akun:
        await add_to_db(form_data)
        return JSONResponse({"message":f"On process for node = {form_data.id_node}! if still not appear this mean node with id {form_data.id_node} doesnt exist or value given is not compatible with node (different length how much value given and item in field_sensor )"}, status_code=201)
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)
    
@router.get('/detail/{id}')
async def get_stats(id: int, akun : Account = Depends(get_current_user)):
    if akun:
        try:
            feed_object = await Feed.get_feed_data(id)
            print(len(feed_object))
            try:
                field_object = await Node.get_field_data(id)
                field = field_object[0]["field_sensor"]
            except:
                raise HTTPException(
                    status_code = status.HTTP_400_BAD_REQUEST,
                    detail="node not found",
                )
        except:
            return JSONResponse({'message':'this node doesnt have any feed'}, status_code=400)
        feed_dict = {x: [] for x in field}
        date_list = []
        year_month_day_format = '%Y-%m-%d'
        for i in reversed(range(0, len(feed_object))):
            date_list.append(feed_object[i]["time"].strftime(year_month_day_format))
            for j in range(0, len(feed_object[i]["value"])):
                feed_dict[field[j]].append(feed_object[i]["value"][j])
        print(feed_dict)
        print(date_list)

        # for feed in feed_object:
        #     feed_data = feed.get('value')
        #     feed_list.append(feed_data)
        # field_object = await Node.get_field_data(id)
        # field_list = []
        # for feed in field_object:
        #     feed_data = feed.get('field_sensor')
        #     field_list.append(feed_data)

        querys = []
        for j in feed_dict:
            query = ''
            for i in range(0, len(feed_dict[j])):
                if i == len(feed_dict[j]) - 1:
                    query += '{ label: "%s", y: %s }' % (date_list[i], str(feed_dict[j][i]))
                else:
                    query += '{ label: "%s", y: %s },' % (date_list[i], str(feed_dict[j][i]))
            querys.append(query)

        number = [x for x in range(0, len(field))]
        print(number)

        return JSONResponse({'fields':field, 'feed':feed_dict, 'date':date_list}, status_code=200)
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)