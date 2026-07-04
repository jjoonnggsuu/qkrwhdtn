import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(page_title="설문조사 및 결과 대시보드", layout="wide")
st.title("📋 설문조사 참여 및 실시간 결과")

# 2. Google Sheets 연결 설정
# 제공해주신 구글 시트 URL 링크
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1Pna_I6ML52sU6p_RhQCzmKJlmJ25Kjjtn-6tj22oPxw/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

# 기존 데이터 불러오기 함수 (캐시를 지우고 실시간 반영하기 위해 ttl=0 설정)
def load_data():
    try:
        return conn.read(spreadsheet=SPREADSHEET_URL, ttl=0)
    except Exception as e:
        # 시트가 완전히 비어있을 경우 예외 처리용 빈 데이터프레임 생성
        return pd.DataFrame(columns=["타임스탬프", "이름", "만족도", "건의사항"])

df = load_data()

# 화면을 좌우 2부 분할 (왼쪽: 설문조사 입력, 오른쪽: 결과 시각화)
col1, col2 = st.columns([1, 1.2])

# =========================================================
# 왼쪽 Column: 설문조사 참여 양식
# =========================================================
with col1:
    st.header("📝 설문 참여하기")
    
    with st.form(key="survey_form", clear_on_submit=True):
        # 예시 문항들입니다. 설문지 컬럼에 맞춰 수정 가능합니다.
        name = st.text_input("1. 이름을 입력해주세요:")
        satisfaction = st.selectbox("2. 서비스 만족도는 어떠신가요?", ["매우 만족", "만족", "보통", "불만족"])
        comments = st.text_area("3. 추가 건의사항이 있다면 적어주세요:")
        
        submit_button = st.form_submit_button(label="설문 제출하기")
        
        if submit_button:
            if name.strip() == "":
                st.error("이름을 입력해주세요!")
            else:
                # 새 응답 데이터 생성
                new_data = pd.DataFrame([{
                    "타임스탬프": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "이름": name,
                    "만족도": satisfaction,
                    "건의사항": comments
                }])
                
                # 기존 데이터와 병합
                updated_df = pd.concat([df, new_data], ignore_index=True)
                
                # 구글 시트에 업데이트 기록
                conn.update(spreadsheet=SPREADSHEET_URL, data=updated_df)
                st.success("설문이 성공적으로 제출되었습니다! 🎉")
                
                # 데이터 새로고침
                st.rerun()

# =========================================================
# 오른쪽 Column: 설문조사 결과 통계 및 차트
# =========================================================
with col2:
    st.header("📊 실시간 설문 결과")
    
    # 최신 데이터 다시 로드
    df = load_data()
    
    if df.empty or len(df) == 0:
        st.info("아직 제출된 설문 응답이 없습니다. 첫 번째 설문을 제출해보세요!")
    else:
        # 총 참여자 수 표시
        st.metric(label="👥 총 참여자 수", value=f"{len(df)}명")
        
        st.subheader("💡 만족도 분포")
        # 만족도 항목별 비율 계산 및 시각화 (Pie 차트)
        satisfaction_counts = df["만족도"].value_counts().reset_index()
        satisfaction_counts.columns = ["만족도", "응답 수"]
        
        fig = px.pie(
            satisfaction_counts, 
            values="응답 수", 
            names="만족도", 
            hole=0.3,
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 전체 응답 데이터 테이블 표출
        st.subheader("📋 전체 응답 데이터 데이터 현황")
        st.dataframe(df, use_container_width=True)
