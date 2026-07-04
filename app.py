import streamlit as st
from supabase import create_client, Client
import datetime

# 1. Streamlit Secrets에서 Supabase 연결 정보 가져오기
import os

try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except KeyError:
    st.error("Streamlit Secrets에 SUPABASE_URL과 SUPABASE_KEY를 설정해주세요.")
    st.stop()

# 2. Supabase 클라이언트 초기화
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 3. 설문조사 앱 UI 구성
st.title("🏫 학교 생활 설문조사")
st.write("아래 설문에 답하고 제출 버튼을 눌러주세요.")

with st.form("survey_form", clear_on_submit=True):
    # 질문 1: 어느 학교를 다니나요? (텍스트 입력)
    school_name = st.text_input("어느 학교를 다니나요?", placeholder="예: 한국고등학교")
    
    # 질문 2: 학교 가는 것을 좋아하나요? (라디오 버튼)
    like_school = st.radio(
        "학교 가는 것을 좋아하나요?",
        ["매우 좋다", "좋다", "보통이다", "싫다", "매우 싫다"],
        index=2
    )
    
    # 질문 3: 학교에서 가장 좋아하는 과목은 무엇인가요? (텍스트 입력)
    favorite_subject = st.text_input("학교에서 가장 좋아하는 과목은 무엇인가요?", placeholder="예: 수학, 물리")
    
    # 질문 4: 그 과목을 얼마나 좋아하나요? (슬라이더 1~5점)
    love_level = st.slider("그 과목을 얼마나 좋아하나요? (1: 조금, 5: 매우 많이)", 1, 5, 3)
    
    # 질문 5: 그 과목은 일주일에 몇번 들어있나요? (숫자 입력)
    class_frequency = st.number_input("그 과목은 일주일에 몇번 들어있나요?", min_value=0, max_value=20, value=3, step=1)
    
    # 제출 버튼
    submitted = st.form_submit_button("설문 제출하기")

# 4. 데이터 제출 로직
if submitted:
    if not school_name.strip() or not favorite_subject.strip():
        st.warning("모든 주관식 문항에 답변을 입력해주세요.")
    else:
        # 데이터베이스에 저장할 데이터 객체 생성
        # 타임스탬프는 현재 시간(ISO 형식)으로 자동 생성하여 저장합니다.
        survey_data = {
            "타임스탬프": datetime.datetime.now().isoformat(),
            "어느 학교를 다니나요": school_name,
            "학교 가는 것을 좋아하나요?": like_school,
            "학교에서 가장 좋아하는 과목은 무엇인가요?": favorite_subject,
            "그 과목을 얼마나 좋아하나요?": love_level,
            "그 과목은 일주일에 몇번 들어있나요?": class_frequency
        }
        
        try:
            # Supabase 테이블에 데이터 삽입
            # 테이블 이름에 특수문자가 있으므로 문자열 그대로 정확히 입력해야 합니다.
            response = supabase.table("qkrwhdtn123@").insert(survey_data).execute()
            
            # 성공 메시지
            st.success("🎉 설문이 성공적으로 제출되었습니다! 참여해주셔서 감사합니다.")
        except Exception as e:
            st.error(f"데이터 저장 중 오류가 발생했습니다: {e}")
