from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from controller.authController import cookie_checker
from database.db import get_db
from sqlalchemy.orm import Session
from model.feed import Feed
from model.node import Node
from settings import get_settings

settings = get_settings()
templates = Jinja2Templates(directory="./templates")

router = APIRouter(
    prefix="/feed",
    tags=['feed']
)
    
@router.get('/')
async def get_all_Node(request: Request, db: Session = Depends(get_db)):
    kue = request.cookies.get('user')
    akun = await cookie_checker(kue, db)
    if akun:
        return templates.TemplateResponse("feed.html", {"request": request})
    else:
        return templates.TemplateResponse("auth.html", {"request": request})
    
@router.post('/add')
async def create(request: Request, value: str = Form(),  id_node: str = Form(), db: Session = Depends(get_db)):
    kue = request.cookies.get('user')
    akun = await cookie_checker(kue, db)
    value = [int(_) for _ in value.split(',')]
    len_node_object = await Feed.get_len(id_node)
    len_node = len(len_node_object[0].get('field_sensor'))
    if akun:
        if len_node == len(value):
            if await Feed.create(id_node, value):
                return RedirectResponse("/feed", status_code=status.HTTP_303_SEE_OTHER)
            else:
                raise HTTPException(
                    status_code = status.HTTP_400_BAD_REQUEST,
                    detail="error when create feed",
                )
        else:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail="len musth be same",
            )
    else:
        return templates.TemplateResponse("auth.html", {"request": request})
    
@router.get('/detail/{id}')
async def get_stats(request: Request, id: int, db: Session = Depends(get_db)):
    kue = request.cookies.get('user')
    akun = await cookie_checker(kue, db)
    if akun:
        feed_object = await Feed.get_feed_data(id)
        field_object = await Node.get_field_data(id)
        field = field_object[0]["field_sensor"]
        feed_dict = {x: [] for x in field}
        date_list = []
        year_month_day_format = '%Y-%m-%d'
        for i in reversed(range(0, len(feed_object))):
            date_list.append(feed_object[i]["time_created"].strftime(year_month_day_format))
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

        return templates.TemplateResponse("graph.html", {"request" : request, "querys": querys, "fields": field, "number": number, "max": len(field) - 1})
    else:
        return templates.TemplateResponse("auth.html", {"request": request})