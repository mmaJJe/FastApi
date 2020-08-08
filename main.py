
# api 생성, Body, Query, Path 안의 값을 사용할 때 사용 
from fastapi import FastAPI, Body, Query, Path
# 모델 생성, 필드(속성) 생성
from pydantic import BaseModel, Field
# 열거형 클래스 생성
from enum import Enum
# 선택적 매개변수에 사용, 매개변수의 값을 리스트로 만들어 줌
from typing import Optional, List



# 서버 실행
# uvicorn main:app --reload --host=0.0.0.0 --port=8000
class ModelName(str, Enum):
    al = "alexnet"
    resent = "resnet"
    lenet = "lenet"


class Item(BaseModel):
    name:str
    description:Optional[str] = Field(
        None, title="The description", max_length=300
    )
    price: float = Field(
        ...,
        gt=0,
        description="The price must be bigger than zer0"
        )
    tax:Optional[float] = None

class User(BaseModel):
    username: str
    full_name: Optional[str] = None

app = FastAPI()

@app.get("/")
async def root():
    return {"massage": "hello world"}

@app.post("/create/item/{item_id}")
async def create_item(item: Item):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax":price_with_tax})
    return item_dict

# 경로 매개 변수 
# 경로에 담겨서 데이터가 넘어옴
@app.post("/item/{item_id}")
# 데이터를 반환 데이터의 유형을 지정 가능 
async def read_item(item_id: int):
    return {"item_id": item_id}
# /item/3 오류 X, /item/foo 숫자형 아니라고 오류 남

@app.get("/model/{ModelName}")
async def get_model(model_name: ModelName):
    if model_name == ModelName.al:
        return {"model_name":model_name, "message":"FTW"}

    if model_name.value == "lanet":
        return {"model_name":model_name, "message":"image"}

    return {"model_name":model_name, "message":"residuals"}



fake_items_db = [{"item_name":"foo1"},{"item_name":"foo2"},{"item_name":"foo3"},{"item_name":"foo4"},{"item_name":"foo5"}]
# 쿼리 매개 변수 skip: int = 0 // 쿼리명: 쿼리 데이터의 종류 = default 값
@app.get("/items")
async def get_items(skip: int = 0, limit: int = 10):
    return fake_items_db[skip: skip + limit]


# 선택적 매개 변수, Query 통한 검증 추가
@app.get("/user/{user_id}/items/{item_id}")
# 만약 q 가 있다면 q 를 받아오고 없으면 받아오지 않는 방식 Optional[자료형] 
# None min_length, max_length, regex =선택적으로 작성 가능 or default 값, 최소길이, 최대길이, 만족해야하는 정규표현식
async def read_user_items(user_id:int, item_id: str, q:Optional[str] = Query(None, min_length=3, max_length=50 ), short: bool = False):
    item = {"user_id":user_id, "item_id":item_id}

    if q:
        item.update({"q":q})

    if not short:
        item.update({"description":"long long long description"})

    return item


# ...(ellipsis) => 쿼리를 사용할 때 매개변수 q 가 필요하다는 것을 명시가능
@app.get("/ellipsis")
async def ellipsis(q:str = Query(...,max_length=3)):
    results = {"items": [{"user_id":"foo", "item_id":"foo"}]}
    if q:
        results.update({"q":q})
    return results

#list: Optional[List[str]] = Query(None) 
# list 라는 매개변수 안에 
# :List 자료형을 채워 넣을 수 있고 List 내부에는 str사용해야한다 
# = 필수로 값을 채워야하는 것은 아님 Query 안에 리스트 넣어서 default 값 넣을 수 있음

# Query 안의 alias 속성 파이썬 변수로 가질 수 없는 값을 query 의 변수로 가질 수 있게 해줌
# deprecated=True 사용 불가로 만듬
@app.get("/list")
async def list_items(
    q: Optional[List[str]] = Query(
    None,
    title="Query String", 
    alias="item-query", 
    description= "asdasd",
    # ??? docs 에 Query S
    # regex= "^fixedquery$",
    deprecated=True
  )
):
    result = {"items": [{"user_id":"foo", "item_id":"foo"}]}
    result.update({"q":q})
    return result

# Request URL: http://localhost:8000/list?item-query=aaa&item-query=bbb
# result :
# {
#   "q": [
#     "aaa",
#     "bbb"
#   ]
# }

# * 사용되는 경우 찾아보기
@app.get("/path/item/{item_id}")
async def path_item(
    *,
    # 경로상에서 데이터를 가져와야 제대로 작동함
    item_id: int = Path(..., title="The ID of the item to get"),
    q: Optional[str] = Query(
        None, alias="item_query"
    ),
    # gt = 초과, ge = 이상, lt = 미만, le = 이하
    size: float = Query(..., gt=0, lt=10.5)
):
    result = {"item_id":item_id, "size":size}
    if q:
        result.update({"q":q})
    return result

@app.put("/item/{item_id}")
async def update_item1(
    *,
    item_id: int = Path(..., title="the ID of the item", ge=0, le=1000),
    q: Optional[str]= None,
    item: Item = Body(...),
    user : User,
    importance: int = Body(...),
):
    results = {"item_id":item_id, "user":user, "importance":importance}
    if q:
        results.update({"q":q})
    if item:
        results.update({"item":item})
    return results

@app.put("/item2/{item_id}")
async def update_item2(
    item_id: int,
    item : Item = Body(...,embed=True)
):
    result = {"item_id":item_id, "item":item}
    return result