# 왁스코드 노드

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
