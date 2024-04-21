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
from selenium import webdriver
from selenium.webdriver.common.by import By
import datetime
import copy

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

# 카페 제목이 긴 경우 max_length에 맞추어 자르고 뒤에 ".." 붙이기
def truncate_cafe_title(s, max_length=10):
    if len(s) <= max_length:
        return s
    else:
        return s[:max_length] + ".."

def get_latest_cafe_link(url, member_name):
    options = webdriver.ChromeOptions()
    # headless 옵션 설정
    options.add_argument('--headless=new')

    driver = webdriver.Chrome(options=options)

    # 크롤링 방지 우회
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
                """
    })

    driver.get(url)
    driver.implicitly_wait(20)

    # iframe 식별
    # 스텔라이브 카페 게시글 관계없이 iframe 공통으로 보임
    iframe = driver.find_element(By.XPATH,'//*[@id="cafe_main"]')

    # iframe으로 전환
    driver.switch_to.frame(iframe)

    # 특정 url의 첫 게시글 element 얻기
    # 모든 게시판 공통인 점 확인
    post = driver.find_element(By.XPATH,'//*[@id="main-area"]/div[4]/table/tbody/tr[1]/td[1]/div[2]/div/a[1]')

    # 해당 게시글 링크
    cafe_link = post.get_attribute('href')

    # 해당 게시글 제목
    cafe_title = post.text
    # 제목을 최대 글자 길이에 맞추어 자르기
    cafe_title = truncate_cafe_title(cafe_title)

    # 해당 게시글 업로드 날짜
    cafe_time = driver.find_element(By.XPATH, '//*[@id="main-area"]/div[4]/table/tbody/tr[1]/td[3]').text
    if ":" in cafe_time:
        # 현재 날짜와 시간을 가져옵니다.
        now = datetime.datetime.now()

        # 날짜를 yyyy.mm.dd 형식으로 포맷팅합니다.
        #cafe_time = now.strftime("%Y.%m.%d") + ' ' + cafe_time
        cafe_time = now.strftime("%Y.%m.%d")
    else:
        cafe_time = cafe_time[:-1]
    


    if not cafe_link or not cafe_title or not cafe_time:
        print("[에러] 빈 정보의 cafe_link 또는 cafe_title, cafe_time이 크롤링 되었습니다.")

    # 카페 링크, 카페 제목, 업로드 날짜 순서대로 캐시 data list 삽입
    # 캐싱된 데이터가 없는경우 데이터 최초 삽입
    if not cafe_cache_dict[member_name]['data']:
        cafe_cache_dict[member_name]['data'].append(cafe_link)
        cafe_cache_dict[member_name]['data'].append(cafe_title)
        cafe_cache_dict[member_name]['data'].append(cafe_time)
    # 이미 캐싱된 데이터가 있지만 cache_time을 오버하여 값을 덮어쓰는 경우
    else:
        cafe_cache_dict[member_name]['data'][0] = cafe_link
        cafe_cache_dict[member_name]['data'][1] = cafe_title
        cafe_cache_dict[member_name]['data'][2] = cafe_time
    
    # 데이터를 새로 저장한 시간을 저장
    cafe_cache_dict[member_name]['time'] = datetime.datetime.now()

    return cafe_link, cafe_title, cafe_time



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
@app.route("/get_cafe_data", methods=["POST"])
def get_cafe_data():
    # js 파일에서 전달한 member 변수 얻어오기 (멤버별 dictionary key값 ex.GangGi)
    member = request.form.get('member')
    member_name = member.split('-')[-1]

    # 이전에 호출하여 cache_dict에 데이터가 있는 경우, cache_time을 초과하지 않은 경우 기존 caching 데이터 반환
    if is_caching_time(cafe_cache_dict, member_name) == True:
        print(member_name + ' 캐싱 데이터 반환 ! \n크롤링 진행하지 않음')
        return jsonify({
            'cafe_link': cafe_cache_dict[member_name]['data'][0],
            'cafe_title' : cafe_cache_dict[member_name]['data'][1],
            'cafe_time' : cafe_cache_dict[member_name]['data'][2]
        })
    
    # 네이버 카페는 게시글이 iframe안에 있어서 크롤링시 iframe url로 접근 필요
    # 멤버별로 menuid만 다르기 때문에 해당 부분만 dictionary에서 값을 얻어와 삽입
    url = 'https://cafe.naver.com/tteokbokk1?iframe_url=/ArticleList.nhn%3Fsearch.clubid=29424353%26search.menuid=' + cafe_menuid_dict[member_name] + '%26search.boardtype=L'

    # 크롤링으로 링크, 제목, 올린날짜 얻어오기
    cafe_link, cafe_title, cafe_time = get_latest_cafe_link(url, member_name)

    return jsonify({
        'cafe_link': cafe_link,
        'cafe_title' : cafe_title,
        'cafe_time' : cafe_time
    })

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

#  menuid (게시판 우클릭 링크 복사로 알 수 있음)
cafe_menuid_dict = {
    'GangGi' :'7',
    'Kanna' : '131',
    'Yuni' : '134',
    'Hina' : '149',
    'Masiro' : '150',
    'Tabi' : '152',
    'Rize' : '151'
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
cafe_cache_dict = copy.deepcopy(member_dict)



# YouTube API 키와 채널 ID를 입력하세요.
api_key = 'AIzaSyACvxE1jRByHukPXrNJZ86Wy9Bx9c7ehzU'
#api_key = 'AIzaSyAcBl1hDIozS7imfQnT8GvkSZzUO1XdjLE'

# 캐시 데이터 저장 시간 (초단위)
# 해당 시간 이후 api 새로 호출하여 정보 갱신
# 현재 6시간으로 설정
cache_time = 6 * 3600

#로컬에서 구동할 때만 아래 코드 주석 해제
# if __name__ == '__main__':
#     #app.run(debug=True, use_reloader=False)
#     app.run(host='0.0.0.0')