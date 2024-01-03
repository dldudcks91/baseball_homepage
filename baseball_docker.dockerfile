FROM python:3.7.7
# python 3.7.7 버전의 컨테이너 이미지를 base이미지

MAINTAINER LYC <dldudcks91o@gmail.com>
# Docker의 컨테이너를 생성 및 관리 하는 사람의 정보를 기입해줍니다.



WORKDIR ./
# WORKDIR은 cd와 같은 명령으로, 작업 경로를 /usr/src/app으로 이동합니다.
# CMD에서 설정한 실행 파일이 실행될 디렉터리를 지정해주어야 한다.

COPY . .

RUN pip3 install --upgrade pip3
RUN pip3 install -r requirements.txt
# python:3.9.18 이미지 상에 django를 pip를 통해 설치합니다.

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
# 이동한 디렉토리에서 django를 가동시켜주는 코드를 작성합니다. 여기서 port는 8000로 실행시키겠습니다.

EXPOSE 8000
# django 서버의 포트를 8000로 지정하였으므로 Docker의 컨테이너 또한 8000 포트를 열어줍니다.