
# Wakscord Node

뭔가 더 빨라지고 좋아진 느낌이 드는 새로운 왁스코드 노드


## Installation / Setup


```bash
git clone https://github.com/deploybg/wakscord-node
cd wakscord-node
pip install -r requirements.txt 
# or poetry install

cp .config/.env.example .config/.env
cp .config/metadata.example.json .config/metadata.json
```

#### .config/.env 수정하기
```
ACCESS_KEY=왁스코드 리퀘스트할때 쓰는 키
HOST=노드 서버 호스트
PORT=노드 서버 포트
CACHE_CLEANUP_SECOND=이미 작업처리된 task를 보관해주는 시간(초)
```

#### .config/metadata.json 수정하기
```json
{
  "name": "노드 이름",
  "description": "노드 설명 (필수 아님)",
  "owner": "노드 소유자 (필수 아님)"
}
```

#### 실행하기
```bash
python main.py
```
![example-running](https://i.ibb.co/3RCQCFd/2022-12-18-090811.png)

    
## 대충 바뀐거

* sanic > aiohttp.web
* asyncio.Queue > collections.OrderedDict[asyncio.Queue]




## 개발

- [@deploybg](https://www.github.com/deploybg)
- [@minibox24](https://github.com/minibox24)


