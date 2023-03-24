# 왁스코드 노드
> 왁스코드 메세지 정보를 전달하는 웹훅 노드

## 빌드

조건:
- docker
- docker hub desktop (선택)

## 노드 실행하기

도커 허브 이미지를 받기 위해 아래와 같이 실행합니다.

```sh
docker pull minibox24/wakscord-node:latest
```

도커 이미지를 항상 최신 버전으로 유지하세요.

그리고 다음과 같이 컨테이너를 실행합니다.
```sh
docker run -d -p 8777:3000 \
    -e "KEY=my_password" \
    -e "HOST=0.0.0.0" \
    -e "PORT=3000" \
    -e "ID=1" \
    -e "OWNER=yejun#3332" \
    -e "MAX_CONCURRENT=500" \
    -e "WAIT_CONCURRENT=0" \
    --name node --restart always \
    minibox24/wakscord-node
```

각 환경변수의 설명은 다음과 같습니다
- KEY : 노드에 요청을 보내기 위한 API 키
- HOST : aiohttp.web 서버를 열기 위한 호스트
- PORT : aiohttp.web 서버를 열기 위한 지정 포트
- ID : 고유 노드 ID 값
- OWNER : 노드 소유자의 정보
- MAX_CONCURRENT : 동시에 전송가능한 웹훅 수
- WAIT_CONCURRENT : 웹훅 전송 작업이 끝날때까지 기다리는 시간


## 기여하기

기여 및 개발 지침은 [`CONTRIBUTING.md`](CONTRIBUTING.md)를 참고하세요.
