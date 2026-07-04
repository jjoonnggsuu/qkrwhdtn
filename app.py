import streamlit as st
from supabase import create_client, Client
import datetime
import pandas as pd

# 1. Streamlit Secrets에서 Supabase 연결 정보 가져오기
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except KeyError:
    st.error("Streamlit Secrets에 SUPABASE_URL과 SUPABASE_KEY를 설정해주세요.")
    st.stop()

# 2. Supabase 클라이언트 초기화
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 사이드바 메뉴 구성 ---
st.sidebar.title("📋 메뉴 선택")
menu = st.sidebar.radio(
    "이동할 페이지를 선택하세요:",
    ["설문조사 참여하기", "설문 결과 확인하기"]
)
st.sidebar.markdown("---")
st.sidebar.info("학생들의 학교 생활을 알아보는 설문 앱입니다.")

# =========================================================================
# 페이지 1: 설문조사 참여하기
# =========================================================================
if menu == "설문조사 참여하기":
    st.title("🏫 학교 생활 설문조사")
    st.write("아래 설문에 답하고 제출 버튼을 눌러주세요.")

    with st.form("survey_form", clear_on_submit=True):
        school_type = st.radio(
            "어느 학교를 다니나요?",
            ["초등학교", "중학교", "고등학교", "대학교/기타"],
            index=2
        )
        
        like_school = st.radio(
            "학교 가는 것을 좋아하나요?",
            ["매우 좋다", "좋다", "보통이다", "싫다", "매우 싫다"],
            index=2
        )
        
        favorite_subject = st.text_input("학교에서 가장 좋아하는 과목은 무엇인가요?", placeholder="예: 수학, 물리")
        
        love_level = st.slider("그 과목을 얼마나 좋아하나요? (1: 조금, 5: 매우 많이)", 1, 5, 3)
        
        class_frequency = st.number_input("그 과목은 일주일에 몇번 들어있나요?", min_value=0, max_value=20, value=3, step=1)
        
        submitted = st.form_submit_button("설문 제출하기")

    if submitted:
        if not favorite_subject.strip():
            st.warning("가장 좋아하는 과목을 입력해주세요.")
        else:
            # 저장할 데이터 딕셔너리 생성 (오류 없이 확실하게 중괄호 처리)
            survey_data = {
                "타임스탬프": datetime.datetime.now().isoformat(),
                "어느 학교를 다니나요": school_type,
                "학교 가는 것을 좋아하나요?": like_school,
                "학교에서 가장 좋아하는 과목은 무엇인가요?": favorite_subject,
                "그 과목을 얼마나 좋아하나요?": love_level,
                "그 과목은 일주일에 몇번 들어있나요?": class_frequency
            }
            
            try:
                # Supabase 테이블에 데이터 삽입 (문자열 잘림 없이 한 줄로 처리)
                response = supabase.table("qkrwhdtn123@").insert(survey_data).execute()
                st.success("🎉 설문이 성공적으로 제출되었습니다! 결과 확인 페이지에서 실시간 데이터를 확인해보세요.")
            except Exception as e:
                st.error(f"데이터 저장 중 오류가 발생했습니다: {e}")

# =========================================================================
# 페이지 2: 설문 결과 확인하기
# =========================================================================
elif menu == "설문 결과 확인하기":
    st.title("📊 설문조사 결과 통계")
    st.write("Supabase 데이터베이스에 저장된 실시간 설문 결과입니다.")
    
    try:
        # Sup
