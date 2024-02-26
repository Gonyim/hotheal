import requests
from bs4 import BeautifulSoup
import time
import json

# 액세스 토큰 로드 함수
def load_access_token():
    with open("access_token.txt", "r") as file:
        access_token = file.read().strip()
    return access_token

KAKAO_TOKEN = load_access_token()

# 중복방지 send_lists 리스트 생성
send_lists = []


#카카오톡 나에게보내기 설정
def send_to_kakao(text):
    header = {"Authorization": 'Bearer ' + KAKAO_TOKEN}
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    post = {
        "object_type": "text",
        "text": text,
        "link": {
            "web_url": "https://developers.kakao.com",
            "mobile_web_url": "https://developers.kakao.com"
        },
    }

    data = {"template_object": json.dumps(post)}
    try:
        response = requests.post(url, headers=header, data=data)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print("카카오톡 전송 중 오류 발생:", e)
        return None


def crawl_board_items(board_url, target_keywords):
    # HTTP GET 요청을 보냅니다.
    response = requests.get(board_url)

    # 요청이 성공했는지 확인합니다.
    if response.status_code == 200:
        # HTML을 파싱합니다.
        soup = BeautifulSoup(response.text, 'html.parser')

        # 게시글 제목과 작성자 정보를 찾습니다.
        titles = soup.find_all('a', class_='hotdeal_var8')
        posts = soup.find_all('span', class_='author')

        # 각 키워드를 순회하며 게시글을 검색합니다.
        for keyword in target_keywords:
            # 게시글 제목들을 순회하며 원하는 키워드가 있는지 확인합니다.
            for title, post in zip(titles, posts):
                # 제목의 양쪽 공백을 제거합니다.
                title_text = title.text.strip()
                # 작성자 정보를 가져옵니다.
                author = post.text.strip()

                if keyword in title_text:
                    send = True
                    for s in send_lists:
                        if s["title_text"] == title_text:
                            print("중복")
                            send = False
                            break  # 중복된 게시물이 발견되면 더 이상 검사하지 않고 중단

                    if send:
                        text = f'게시물 제목: {title_text}\n게시글 링크: https://www.fmkorea.com/{title["href"]}\n작성자: {author}\n'
                        # print("게시글 제목:", title_text)
                        # print("게시글 링크:", f'https://www.fmkorea.com/{title["href"]}')
                        # print("작성자:", author)
                        # print()  # 개행을 통해 각 게시글 정보를 구분합니다.
                        r = send_to_kakao(text)
                        if r is not None:
                            print(r)  # 카카오톡 전송 결과를 출력합니다.
                            send_lists.append({
                                "title_text": title_text,
                                "author": author
                            })
    else:
        print("HTTP 요청이 실패했습니다.")

# 크롤링할 게시판 URL과 찾고자 하는 키워드들을 지정합니다.
board_url = "https://www.fmkorea.com/hotdeal"
target_keywords = ["보먹돼", "연어"]

# 크롤링 함수를 호출하여 게시판에서 원하는 키워드가 포함된 게시글을 찾습니다.
while True:
    crawl_board_items(board_url, target_keywords)
    time.sleep(1800)
    # 현재 30분 간격으로 자동확인
