# 1. 필요한 라이브러리를 불러옵니다.
import streamlit as st
import wikipediaapi
import wikipedia # 이미지 및 쉬운 검색을 위해 추가
import re # 생년월일 같은 특정 패턴을 찾기 위해 추가

# --- 초기 설정 ---

# 2. 위키피디아 언어를 한국어로 설정합니다.
# User-Agent는 위키피디아 정책상 간단한 설명과 연락처를 포함하는 것이 좋습니다.
wiki_wiki = wikipediaapi.Wikipedia(
    language='ko',
    user_agent='MyCelebrityApp/1.0 (youremail@example.com)'
)
# 'wikipedia' 라이브러리도 한국어로 설정합니다.
wikipedia.set_lang('ko')

# --- 추가된 함수 ---

# 이미지 URL을 가져오는 함수
def get_image_url(page):
    # .jpg, .png 등 이미지 확장자로 끝나는 첫 번째 이미지 주소를 반환합니다.
    for image_url in page.images:
        if image_url.lower().endswith(('.jpg', '.jpeg', '.png')):
            return image_url
    return None

# 요약 텍스트에서 구조화된 프로필 정보를 추출하는 함수
def extract_profile(summary):
    profile = {
        "생년월일": "정보 없음",
        "출생": "정보 없음",
        "직업": "정보 없음",
        "소속 그룹": "정보 없음"
    }
    # 정규표현식을 사용하여 생년월일 추출 (예: 1993년 1월 12일)
    birth_match = re.search(r'(\d{4}년 \d{1,2}월 \d{1,2}일)', summary)
    if birth_match:
        profile["생년월일"] = birth_match.group(1)

    # 간단한 키워드로 정보 추출
    sentences = summary.split('.')
    if sentences:
        first_sentence = sentences[0]
        if "가수" in first_sentence: profile["직업"] = "가수"
        if "배우" in first_sentence: profile["직업"] = "배우"
        if "가수 겸 배우" in first_sentence: profile["직업"] = "가수 겸 배우"

        # 소속 그룹 정보 (예시)
        exo_match = re.search(r'EXO|엑소', first_sentence)
        if exo_match:
            profile["소속 그룹"] = "EXO"

    return profile


# --- 앱 UI 구성 ---

st.title("🌟 전세계 연예인 사전")

if 'search_history' not in st.session_state:
    st.session_state.search_history = []

celebrity_name = st.text_input("연예인 이름을 입력하고 Enter를 누르거나 검색 버튼을 클릭하세요.")
search_button = st.button("검색")

if search_button or celebrity_name:
    if celebrity_name:
        try:
            # 7-1. 'wikipedia' 라이브러리로 먼저 페이지를 가져옵니다. (이미지, 요약에 유리)
            # auto_suggest=False는 관련 없는 다른 페이지로 자동 이동하는 것을 방지합니다.
            page = wikipedia.page(celebrity_name, auto_suggest=False)
            
            # 7-2. 검색 성공 시, 최근 검색 기록에 추가
            if celebrity_name not in st.session_state.search_history:
                st.session_state.search_history.insert(0, celebrity_name)
                if len(st.session_state.search_history) > 10:
                    st.session_state.search_history.pop()

            # --- 검색 결과 출력 (업그레이드된 부분) ---
            st.header(page.title)

            # 8. 화면을 두 개의 열로 분할합니다.
            col1, col2 = st.columns([1, 2]) # 비율 1:2

            with col1: # 첫 번째 열 (사진)
                # 8-1. 이미지 URL을 찾아서 화면에 표시
                image_url = get_image_url(page)
                if image_url:
                    st.image(image_url, caption=page.title)
                else:
                    st.info("이미지를 찾을 수 없습니다.")

            with col2: # 두 번째 열 (프로필)
                # 8-2. 요약 텍스트에서 프로필 정보를 추출하여 표시
                st.subheader("👤 프로필")
                profile_data = extract_profile(page.summary)
                for key, value in profile_data.items():
                    st.write(f"**{key}:** {value}")

            # 9. 전체 요약 설명
            st.subheader("📝 요약 설명")
            st.write(page.summary)

            # 10. 대표 작품/활동 (wikipedia-api 라이브러리 활용)
            # 이 부분은 섹션별 텍스트를 가져오는 'wikipedia-api'가 더 안정적입니다.
            st.subheader("🎬 대표 작품 및 활동")
            wiki_page = wiki_wiki.page(celebrity_name)
            sections_found = []
            keywords = ['필모그래피', '출연 작품', '영화', '드라마', '음반', '방송']
            if wiki_page.exists():
                for section in wiki_page.sections:
                    for keyword in keywords:
                        if keyword in section.title:
                            sections_found.append(f"**[{section.title}]**\n{section.text[:300]}...")
                            break
            
            if sections_found:
                for found in sections_found:
                    st.write(found)
            else:
                st.write("분류된 작품 정보가 없습니다.")


        except wikipedia.exceptions.PageError:
            st.error(f"'{celebrity_name}'에 대한 위키피디아 페이지를 찾을 수 없습니다.")
        except wikipedia.exceptions.DisambiguationError as e:
            st.warning(f"검색어가 여러 의미를 가집니다. 좀 더 자세하게 입력해주세요. (예: {e.options[0]}, {e.options[1]})")
        except Exception as e:
            st.error(f"알 수 없는 오류가 발생했습니다: {e}")


# --- 사이드바 UI ---
st.sidebar.title("최근 검색 기록")
if not st.session_state.search_history:
    st.sidebar.info("아직 검색 기록이 없습니다.")
else:
    for item in st.session_state.search_history:
        st.sidebar.write(item)