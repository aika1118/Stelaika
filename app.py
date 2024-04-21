# 해당 파일 실행 후 http://127.0.0.1:5000로 접속해야함
# 파일 구조는 아래와 같아야함
# - app.py
# - static/
#   - images/
#     - your_image.jpg
#   - css/
#     - your_style.css
#   - js/
#     - your_script.js
# - templates/
#   - your_template.html

# develop commit test


from flask import Flask, render_template, jsonify, request
from googleapiclient.discovery import build
import datetime
import copy
import urllib.request
import json
import re

app = Flask(__name__)

def init_youtube_api(api_key, channel_id):
    # YouTube API 클라이언트를 빌드합니다.
    youtube = build('youtube', 'v3', developerKey=api_key)

    # 동영상 목록을 가져오는 API 요청을 만듭니다.
    request = youtube.search().list(
        part='snippet',
        channelId=channel_id,
        order='date',
        maxResults=1  # 최근 동영상 1개만 가져오도록 설정
    )

    # API 요청을 실행하고 응답을 가져옵니다.
    try:
        response = request.execute()
        print("유튜브 API 요청 성공 !")
    except Exception as e:
        print("유튜브 API 요청 실패 !", e)
        exit(0)

    return response

def get_latest_video_data(response, member_name):
    url = f'https://www.youtube.com/embed/{response["items"][0]["id"]["videoId"]}'
    if not youtube_cache_dict[member_name]['data']:
        youtube_cache_dict[member_name]['data'].append(url)
    else:
        youtube_cache_dict[member_name]['data'][0] = url
    youtube_cache_dict[member_name]['time'] = datetime.datetime.now()
    print(youtube_cache_dict[member_name]['time'])
    return url

def get_search_data_by_naverAPI(member_name):
    keyword = ""

    if member_name == 'GangGi':
        keyword = "스텔라이브 강지"

    elif member_name == 'Kanna':
        keyword = "스텔라이브 칸나"

    elif member_name == 'Yuni':
        keyword = "스텔라이브 유니"

    elif member_name == 'Hina':
        keyword = "스텔라이브 히나"  

    elif member_name == 'Masiro':
        keyword = "스텔라이브 마시로"

    elif member_name == 'Tabi':
        keyword = "스텔라이브 타비"  

    elif member_name == 'Rize':
        keyword = "스텔라이브 리제"  

    # 네이버 api 활용하여 keyword를 통해 블로그 검색 후 결과 얻어오기
    encText = urllib.parse.quote(keyword)
    url = "https://openapi.naver.com/v1/search/blog?query=" + encText # JSON 결과
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id",naver_client_id)
    request.add_header("X-Naver-Client-Secret",naver_client_secret)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()

    items = []

    if(rescode==200):
        print("네이버 API 요청 성공 !")
        response_body = response.read()
        response_dict = json.loads(response_body.decode('utf-8'))
        
        for item in response_dict['items']:
            remove_tag = re.compile('<.*?>')
            title = re.sub(remove_tag, '', item['title'])
            link = item['link']

            title = truncate_title(title)
            items.append({"title": title, "link": link})
        
        if not search_cache_dict[member_name]['data']:
            search_cache_dict[member_name]['data'].append(items)
        else:
            search_cache_dict[member_name]['data'][0] = items
            
        search_cache_dict[member_name]['time'] = datetime.datetime.now()
    else:
        print("네이버 API 요청 실패 !:" + rescode)
            
    return items

# 제목이 긴 경우 max_length에 맞추어 자르고 뒤에 ".." 붙이기
def truncate_title(s, max_length=30):
    if len(s) <= max_length:
        return s
    else:
        return s[:max_length] + ".."



def is_caching_time(cache_dict, member_name):
    # cache된 데이터가 있는 경우
    if cache_dict[member_name]['data']:
        elapsed_time = (datetime.datetime.now() - cache_dict[member_name]['time']).total_seconds()
        # 캐싱 타임 범위 안에 있는 경우
        if elapsed_time < cache_time:
            return True
    
    return False


# http://127.0.0.1:5000로 최초 접속 시 어떤 html을 렌더링 해줄지 지정
@app.route('/')
def main():
    return render_template('main.html')

# info.html GET요청 시 info.html 연결
@app.route('/info.html')
def info_html():
    return render_template('info.html')

# main.html GET요청 시 main.html 연결 (info.html에서 배너 클릭으로 main.html 접근 시도시 등)
@app.route('/main.html')
def main_html():
    return render_template('main.html')

# info-script.js에서 post 형식으로 해당 ajax 요청올 시 아래와 같이 데이터를 얻은 후 json으로 전송함
@app.route("/get_video_data", methods=["POST"])
def get_video_data():
    # js 파일에서 전달한 member 변수 얻어오기 (멤버별 dictionary key값 ex.GangGi)
    member = request.form.get('member')
    member_name = member.split('-')[-1]

    # 이전에 호출하여 cache_dict에 데이터가 있는 경우, cache_time을 초과하지 않은 경우 기존 caching 데이터 반환
    if is_caching_time(youtube_cache_dict, member_name) == True:
        print(member_name + ' 캐싱 데이터 반환 ! \nAPI를 호출하지 않음')
        return jsonify({'video_link': youtube_cache_dict[member_name]['data'][0]})

    channel_id = channel_id_dict[member_name]
    response = init_youtube_api(api_key, channel_id)
    video_link = get_latest_video_data(response, member_name)
    return jsonify({'video_link': video_link})

# info-script.js에서 post 형식으로 해당 ajax 요청올 시 아래와 같이 데이터를 얻은 후 json으로 전송함
@app.route("/get_search_data", methods=["POST"])
def get_search_data():
    # js 파일에서 전달한 member 변수 얻어오기 (멤버별 dictionary key값 ex.GangGi)
    member = request.form.get('member')
    member_name = member.split('-')[-1]

    # 이전에 호출하여 cache_dict에 데이터가 있는 경우, cache_time을 초과하지 않은 경우 기존 caching 데이터 반환
    if is_caching_time(search_cache_dict, member_name) == True:
        print(member_name + ' 캐싱 데이터 반환 ! \nAPI를 호출하지 않음')
        return jsonify(search_cache_dict[member_name]['data'][0])

    items = get_search_data_by_naverAPI(member_name)
    
    return jsonify(items)


# channel_id 얻는법
# 유튜브 채널 자세히 알아보기 -> 채널 공유 -> 채널 ID 복사
channel_id_dict = {
    'GangGi' :'UCIVFv8AiQLqM9oLHTixrNYw',
    'Kanna' : 'UCKzfyYWHQ92z_2jUcSABM8Q',
    'Yuni' : 'UClbYIn9LDbbFZ9w2shX3K0g',
    'Hina' : 'UC1afpiIuBDcjYlmruAa0HiA',
    'Masiro' : 'UC_eeSpMBz8PG4ssdBPnP07g',
    'Tabi' : 'UCAHVQ44O81aehLWfy9O6Elw',
    'Rize' : 'UC7-m6jQLinZQWIbwm9W-1iw'
}

# ajax 요청에 따라 data에 데이터 저장, time에 데이터 저장한 시간 저장 (cache_time을 벗어났는지 비교 위함)
member_dict = {
    'GangGi' : {
        'data' : [],
        'time' : ''
    },
    'Kanna' : {
        'data' : [],
        'time' : ''
    },
    'Yuni' : {
        'data' : [],
        'time' : ''
    },
    'Hina' : {
        'data' : [],
        'time' : ''
    },
    'Masiro' : {
        'data' : [],
        'time' : ''
    },
    'Tabi' : {
        'data' : [],
        'time' : ''
    },
    'Rize' : {
        'data' : [],
        'time' : ''
    },
}

# ajax 요청 타입별로 데이터 저장소 깊은 복사 
youtube_cache_dict = copy.deepcopy(member_dict)
search_cache_dict = copy.deepcopy(member_dict)

# 네이버 API 정보
naver_client_id = "YlKCxFgQ3AlYi6yL0OBp"
naver_client_secret = "9BMD9HxhWX"



# YouTube API 키와 채널 ID를 입력하세요.
api_key = 'AIzaSyACvxE1jRByHukPXrNJZ86Wy9Bx9c7ehzU'

# 캐시 데이터 저장 시간 (초단위)
# 해당 시간 이후 api 새로 호출하여 정보 갱신
# 현재 2시간으로 설정
cache_time = 2 * 3600

#로컬에서 구동시 아래 코드 주석 해제
if __name__ == '__main__':
     #app.run(debug=True, use_reloader=False)
     app.run(host='0.0.0.0')