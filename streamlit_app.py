# 1. 필요한 라이브러리를 불러옵니다.
import streamlit as st
import wikipediaapi
import wikipedia
import re
import time # API 요청 사이에 약간의 지연을 주기 위해 추가

# --- 초기 설정 ---
wiki_wiki = wikipediaapi.Wikipedia(
    language='ko',
    user_agent='MyCelebrityApp/1.0 (youremail@example.com)'
)
wikipedia.set_lang('ko')

# --- 도우미 함수 (업그레이드 및 추가) ---

# 이미지 URL을 가져오는 함수 (재사용)
def get_image_url(page):
    for image_url in page.images:
        if image_url.lower().endswith(('.jpg', '.jpeg', '.png')):
            return image_url
    return None

# 프로필 정보 추출 함수 (재사용)
def extract_profile(summary):
    profile = {
        "생년월일": "정보 없음",
        "출생": "정보 없음",
        "직업": "정보 없음",
        "소속 그룹": "정보 없음"
    }
    sentences = summary.split('.')
    if not sentences: return profile
    first_sentence = sentences[0]

    birth_match = re.search(r'(\d{4}년 \d{1,2}월 \d{1,2}일)', summary)
    if birth_match: profile["생년월일"] = birth_match.group(1)

    birthplace_match = re.search(r'의\s*(\S+)\s*출신', first_sentence)
    if not birthplace_match: birthplace_match = re.search(r'(\S+)(특별|광역|도|시|군|구)에서 태어난', first_sentence)
    if birthplace_match: profile["출생"] = birthplace_match.group(1).strip()

    if "가수" in first_sentence: profile["직업"] = "가수"
    if "배우" in first_sentence: profile["직업"] = "배우"
    if "가수 겸 배우" in first_sentence: profile["직업"] = "가수 겸 배우"

    exo_match = re.search(r'EXO|엑소', first_sentence)
    if exo_match: profile["소속 그룹"] = "EXO"
    
    return profile

# --- !!! 새로 추가된 핵심 함수 !!! ---
# 1. 섹션 텍스트에서 작품 목록을 추출하는 함수
def parse_works_from_section(text):
    # 《작품명》 또는 '작품명' 형태의 제목을 추출합니다.
    # 한국 위키피디아는 주로 《》 괄호를 사용합니다.
    works = re.findall(r'《([^》]+)》', text)
    return works

# 2. 작품명으로 위키피디아를 다시 검색해 이미지를 가져오는 함수
def get_image_for_work(work_title):
    try:
        # 작품명으로 페이지 검색
        work_page = wikipedia.page(work_title, auto_suggest=False)
        # 위키피디아 API에 과부하를 주지 않기 위해 잠시 대기
        time.sleep(0.1) 
        # 해당 페이지의 이미지 URL 반환
        return get_image_url(work_page)
    except Exception:
        # 페이지가 없거나 오류 발생 시 None 반환
        return None

# --- 앱 UI 구성 ---

st.title("🌟 전세계 연예인 사전")

if 'search_history' not in st.session_state:
    st.session_state.search_history = []

celebrity_name = st.text_input("연예인 이름을 입력하고 Enter를 누르거나 검색 버튼을 클릭하세요.")
search_button = st.button("검색")

if search_button or celebrity_name:
    if celebrity_name:
        try:
            page = wikipedia.page(celebrity_name, auto_suggest=False)
            
            if celebrity_name not in st.session_state.search_history:
                st.session_state.search_history.insert(0, celebrity_name)
                if len(st.session_state.search_history) > 10:
                    st.session_state.search_history.pop()

            st.header(page.title)

            col1, col2 = st.columns([1, 2])
            with col1:
                image_url = get_image_url(page)
                if image_url:
                    st.image(image_url, caption=page.title)
                else:
                    st.info("이미지를 찾을 수 없습니다.")
            with col2:
                st.subheader("👤 프로필")
                profile_data = extract_profile(page.summary)
                for key, value in profile_data.items():
                    st.write(f"**{key}:** {value}")

            st.subheader("📝 요약 설명")
            st.write(page.summary)

            # --- !!! 작품 목록 UI 업그레이드 !!! ---
            st.subheader("🎬 대표 작품 및 활동")
            
            wiki_page = wiki_wiki.page(celebrity_name)
            keywords = ['필모그래피', '음반', '참여 작품', '영화', '드라마', '뮤지컬', '공연']
            
            if wiki_page.exists():
                for section in wiki_page.sections:
                    for keyword in keywords:
                        if keyword in section.title:
                            # 1. 섹션 제목으로 확장 가능한 영역(expander)을 만듭니다.
                            with st.expander(f"**{section.title}** 목록 보기"):
                                # 2. 섹션 본문에서 작품명 리스트를 추출합니다.
                                works_list = parse_works_from_section(section.text)
                                
                                if not works_list:
                                    st.write("이 섹션에서 작품명을 자동으로 추출하지 못했습니다.")
                                    st.text(section.text[:500] + "...") # 대신 원본 텍스트 일부 표시
                                    continue

                                # 3. 추출된 작품명 하나하나에 대해 이미지 검색을 시도합니다.
                                for work in works_list:
                                    work_col1, work_col2 = st.columns([1, 3])
                                    with work_col1:
                                        # 작품 이미지를 가져옵니다. (시간이 조금 걸릴 수 있음)
                                        work_image_url = get_image_for_work(work)
                                        if work_image_url:
                                            st.image(work_image_url)
                                        else:
                                            st.image("https://via.placeholder.com/150x200.png?text=No+Image", use_column_width=True) # 대체 이미지
                                    with work_col2:
                                        st.markdown(f"**{work}**")
                                    st.divider() # 작품별 구분선
                            break # 키워드를 찾으면 다음 섹션으로 이동

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