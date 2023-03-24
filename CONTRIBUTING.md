# 왁스코드 노드에 기여하기

이 문서는 개발을 위해 왁스코드 노드를 실행하는데 도움이 되는 것을 목표로 합니다.

[왁스코드는 Github에 오픈 소스 프로젝트](https://https://github.com/wakscord)에 대한 기여를 환영합니다.

패치 및 추가 사항 제출에 대해 각 프로젝트에 스타일 및 기여 지침을 확인하세요.  
일반적으로 왁스코드는 "fork-and-pull" Git 작업 흐름을 따릅니다.

 1. 깃헙에서 리포지토리를 **포크하기** 
 2. 자신의 컴퓨터에 프로젝트 **복제하기** 
 3. 자신의 브랜치에 대한 변경 사항 **커밋하기** 
 4. 작업 내용을 포크된 리포지토리로 **푸쉬하기**
 5. 변경 사항을 검토하고 리뷰할 수 있도록 **Pull Request 요청하기**

주의: Pull Request를 요청하기 전에 "업스트림"에서 최신 변경 사항을 병합해야 합니다

## 문제
문제 및 개선 요청을 자유롭게 제출하십시오.

특정 버그 및 오류를 보고하려면 [이메일로 연락하세요](mailto:minibox724@gmail.com).

## 개발

### 초기 세팅 & 노드 실행하기

먼저 왁스코드 노트 프로젝트를 복제하고 python 가상환경을 생성해 모든 종속성를 설치하세요.

```sh
git clone https://github.com/wakscord/wakscord-node.git
cd wakscord-node
python3 -m pip install --user -U virtualenv
virtualenv [가상 환경을 만들고자 하는 경로]
```
아래와 같이 가상 환경을 운영체제를 확인하고 활성화하세요.

Linux/Max OS: source ``[가상 환경을 만들고자 하는 경로]/bin/activate``  
Windows: ``.\[가상 환경을 만들고자 하는 경로]\Scripts\activate``

그런 다음 모든 종속성을 설치하세요.
```sh
pip install -r requirements.txt
```

### 디버깅 시작하기
프로젝트를 디버깅하려면 다음과 같이 ``node/__main__.py``코드를 수정합니다.
```
11 | def main():
12 |   logging.basicConfig(
13 |       format="[%(name)s] (%(asctime)s) %(levelname)s: %(message)s",
14 |       datefmt="%y/%m/%d %p %I:%M:%S",
15 |       level=logging.DEBUG,
16 |   )
```

이제 개선할 코드를 수정하세요!

