import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="Supabase 설문 대시보드", layout="wide")
st.title("📋 Supabase 기반 설문조사 및 실시간 결과")

# Streamlit Secrets에서 보안 환경변수 로드
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# 데이터 불러오기 함수
def load_data():
    try:
        response = supabase.table("survey_responses").select("*").execute()
        if response.data:
            return pd.DataFrame(response.data)
        else:
            return pd.DataFrame(columns=["id", "created_at", "name", "satisfaction", "comments"])
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류 발생: {e}")
        return pd.DataFrame()

df = load_data()

# 화면 좌우 분할
col1, col2 = st.columns([1, 1.2])

# 왼쪽: 설문조사 참여 양식
with col1:
    st.header("📝 설문 참여하기")
    
    with st.form(key="survey_form", clear_on_submit=True):
        name = st.text_input("1. 이름을 입력해주세요:")
        satisfaction = st.selectbox("2. 서비스 만족도는 어떠신가요?", ["매우 만족", "만족", "보통", "불만족"])
        comments = st.text_area("3. 추가 건의사항이 있다면 적어주세요:")
        
        submit_button = st.form_submit_button(label="설문 제출하기")
        
        if submit_button:
            if name.strip() == "":
                st.error("이름을 입력해주세요!")
            else:
                insert_data = {
                    "name": name,
                    "satisfaction": satisfaction,
                    "comments": comments
                }
                try:
                    supabase.table("survey_responses").insert(insert_data).execute()
                    st.success("설문이 Supabase에 안전하게 저장되었습니다! 🎉")
                    st.rerun()
                except Exception as e:
                    st.error(f"제출 실패: {e}")

# 오른쪽: 실시간 통계 및 차트
with col2:
    st.header("📊 실시간 설문 결과")
    
    df = load_data()
    
    if df.empty or len(df) == 0:
        st.info("아직 제출된 설문 응답이 없습니다. 첫 번째 설문을 제출해보세요!")
    else:
        st.metric(label="👥 총 참여자 수", value=f"{len(df)}명")
        
        st.subheader("💡 만족도 분포")
        satisfaction_counts = df["satisfaction"].value_counts().reset_index()
        satisfaction_counts.columns = ["만족도", "응답 수"]
        
        fig = px.pie(
            satisfaction_counts, 
            values="응답 수", 
            names="만족도", 
            hole=0.3,
            color_discrete_sequence=px.colors.sequential.Plotly3
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("📋 전체 응답 데이터 현황")
        display_df = df.rename(columns={
            "created_at": "제출 시간",
            "name": "이름",
            "satisfaction": "만족도",
            "comments": "건의사항"
        })
        st.dataframe(display_df[["제출 시간", "이름", "만족도", "건의사항"]], use_container_width=True)
