# 1. 필요한 라이브러리를 불러옵니다.
import streamlit as st
import wikipediaapi # 'wikipedia' 라이브러리보다 안정적인 'wikipedia-api'를 사용합니다.

# 2. 위키피디아 API 객체를 생성하고, 언어를 한국어로 설정합니다.
# User-Agent는 위키피디아 정책상 간단한 설명과 연락처를 포함하는 것이 좋습니다.
wiki_wiki = wikipediaapi.Wikipedia(
    language='ko',
    user_agent='MyCelebrityApp/1.0 (youremail@example.com)'
)

# --- 앱 UI 구성 ---

# 3. 앱 제목을 설정합니다.
st.title("🌟 전세계 연예인 사전")

# 4. 'session_state'를 사용하여 최근 검색 기록을 저장할 공간을 초기화합니다.
# 이 공간은 앱이 재실행되어도 유지됩니다.
if 'search_history' not in st.session_state:
    st.session_state.search_history = []

# 5. 연예인 이름을 입력받을 검색창을 만듭니다.
celebrity_name = st.text_input("연예인 이름을 입력하고 Enter를 누르거나 검색 버튼을 클릭하세요.")
search_button = st.button("검색")

# 6. 검색 버튼이 클릭되었거나, 검색창에 텍스트 입력 후 Enter를 눌렀을 때 실행될 로직
if search_button or celebrity_name:
    if celebrity_name: # 입력값이 있는 경우에만 실행
        # 6-1. 위키피디아에서 해당 연예인 페이지를 가져옵니다.
        page = wiki_wiki.page(celebrity_name)

        if page.exists():
            # 6-2. 검색 성공 시, 최근 검색 기록에 추가합니다. (중복 제외)
            if celebrity_name not in st.session_state.search_history:
                st.session_state.search_history.insert(0, celebrity_name)
                # 검색 기록은 최대 10개까지만 유지합니다.
                if len(st.session_state.search_history) > 10:
                    st.session_state.search_history.pop()

            # --- 검색 결과 출력 ---
            
            # 이름
            st.header(page.title)

            # 사진 (Wikimedia Commons 이미지)
            # page.images는 이미지 URL 목록을 반환하며, 첫 번째 이미지를 사용합니다.
            # 하지만 이 라이브러리는 직접적인 이미지 URL을 제공하지 않으므로, 요약 정보에 집중합니다.
            # 좀 더 안정적인 이미지 출력을 위해서는 별도의 라이브러리나 복잡한 과정이 필요합니다.
            # 여기서는 초보자 가이드에 맞게 텍스트 정보에 집중합니다.
            st.info("현재 버전에서는 텍스트 정보를 중심으로 제공합니다.")

            # 간단 프로필 및 요약 설명 (위키피디아 요약)
            # 요약본의 첫 5문장을 가져와 프로필로 사용합니다.
            st.subheader("👤 프로필 요약")
            summary_sentences = page.summary.split('.')
            st.write(". ".join(summary_sentences[:5]) + ".")

            # 대표 작품/활동 프로그램
            # 위키피디아 '섹션'을 순회하며 '필모그래피', '작품', '음반' 등의 정보를 찾습니다.
            st.subheader("🎬 대표 작품 및 활동")
            
            sections_found = []
            keywords = ['필모그래피', '출연 작품', '영화', '드라마', '음반', '방송']
            
            for section in page.sections:
                for keyword in keywords:
                    if keyword in section.title:
                        sections_found.append(f"**[{section.title}]**\n{section.text[:500]}...") # 섹션별로 500자까지 표시
                        break # 키워드를 찾으면 다음 섹션으로 이동

            if sections_found:
                for found in sections_found:
                    st.write(found)
            else:
                st.write("요약 정보 외에 별도로 분류된 작품 정보가 없습니다.")
        
        else:
            # 6-3. 위키피디아에 해당 인물 정보가 없을 경우 에러 메시지를 표시합니다.
            st.error(f"'{celebrity_name}'에 대한 정보를 찾을 수 없습니다. 철자를 확인하거나 다른 이름으로 검색해 보세요.")

# --- 사이드바 UI ---

# 7. 사이드바에 최근 검색 기록을 표시합니다.
st.sidebar.title("최근 검색 기록")
if not st.session_state.search_history:
    st.sidebar.info("아직 검색 기록이 없습니다.")
else:
    # 검색 기록을 순서대로 버튼으로 만들어 클릭 시 재검색이 가능하도록 할 수 있습니다. (심화)
    # 여기서는 간단히 목록만 표시합니다.
    for item in st.session_state.search_history:
        st.sidebar.write(item)