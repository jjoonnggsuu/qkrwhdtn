import streamlit as st
from supabase import create_client, Client
import datetime
import pandas as pd
import altair as alt

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
            # 저장할 데이터 딕셔너리 생성
            survey_data = {
                "타임스탬프": datetime.datetime.now().isoformat(),
                "어느 학교를 다니나요": school_type,
                "학교 가는 것을 좋아하나요?": like_school,
                "학교에서 가장 좋아하는 과목은 무엇인가요?": favorite_subject,
                "그 과목을 얼마나 좋아하나요?": love_level,
                "그 과목은 일주일에 몇번 들어있나요?": class_frequency
            }
            
            try:
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
        # Supabase에서 전체 데이터 가져오기 (시간 순서대로 정렬)
        response = supabase.table("qkrwhdtn123@").select("*").order("타임스탬프", desc=False).execute()
        data = response.data
        
        if not data:
            st.info("아직 제출된 설문 데이터가 없습니다. 첫 번째 설문을 제출해 보세요!")
        else:
            # 판다스 데이터프레임으로 변환
            df = pd.DataFrame(data)
            
            # 오래된 순서(시간 순서)대로 1번부터 번호 매기기
            df["번호"] = range(1, len(df) + 1)
            
            # 표에 보여줄 컬럼 지정
            display_cols = ["번호", "어느 학교를 다니나요", "학교 가는 것을 좋아하나요?", "학교에서 가장 좋아하는 과목은 무엇인가요?", "그 과목을 얼마나 좋아하나요?", "그 과목은 일주일에 몇번 들어있나요?"]
            
            # 실제 데이터프레임에 있는 컬럼만 필터링하여 순서대로 가져오기
            df_display = df[[col for col in display_cols if col in df.columns]]
            
            # 총 참여자 수 시각화
            st.metric(label="총 참여 학생 수", value=f"{len(df)}명")
            
            # 전체 응답 데이터 표 출력
            st.subheader("📝 전체 응답 데이터")
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            # 그래프 출력
            st.markdown("---")
            st.subheader("📈 간단 통계 그래프")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if "어느 학교를 다니나요" in df.columns:
                    st.write("**[학교급별 참여 비율]**")
                    school_counts = df["어느 학교를 다니나요"].value_counts().reset_index()
                    school_counts.columns = ["학교 종류", "학생 수"]
                    
                    chart1 = alt.Chart(school_counts).mark_bar(color="#1f77b4").encode(
                        x=alt.X("학교 종류:N", axis=alt.Axis(labelAngle=0)),
                        y="학생 수:Q"
                    ).properties(width="container")
                    st.altair_chart(chart1, use_container_width=True)
                    
            with col2:
                if "학교 가는 것을 좋아하나요?" in df.columns:
                    st.write("**[학교가 좋은지 여부]**")
                    like_counts = df["학교 가는 것을 좋아하나요?"].value_counts().reset_index()
                    like_counts.columns = ["답변", "학생 수"]
                    
                    chart2 = alt.Chart(like_counts).mark_bar(color="#1f77b4").encode(
                        x=alt.X("답변:N", axis=alt.Axis(labelAngle=0)),
                        y="학생 수:Q"
                    ).properties(width="container")
                    st.altair_chart(chart2, use_container_width=True)
            
            # --- 학교별 가장 좋아하는 과목 분석 표 ---
            st.markdown("---")
            st.subheader("🔍 학교 종류별 가장 좋아하는 과목 현황")
            
            check_cols = ["어느 학교를 다니나요", "학교에서 가장 좋아하는 과목은 무엇인가요?"]
            if all(col in df.columns for col in check_cols):
