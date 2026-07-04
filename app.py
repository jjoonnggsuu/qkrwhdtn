import re
import pandas as pd
import streamlit as st
from supabase import create_client

# =========================
# 페이지 및 디자인 설정
# =========================
st.set_page_config(page_title="배터리 충전 습관 설문 시스템", page_icon="🔋", layout="centered")

st.markdown("""
<style>
.block-container { max-width: 900px; padding-top: 2rem; }
h1 { text-align: center; color: #1f2937; font-weight: 800; }
.stForm { background-color: white; padding: 30px; border-radius: 20px; border: 1px solid #e5e7eb; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
.stButton button { width: 100%; border-radius: 12px; font-size: 18px; font-weight: bold; padding: 12px; }
</style>
""", unsafe_allow_html=True)

# =========================
# Supabase 연결
# =========================
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    # 새로운 테이블명을 secrets에 넣거나 없으면 기본값 사용
    TABLE_NAME = st.secrets.get("BATTERY_TABLE_NAME", "battery_survey")
except Exception:
    st.error("Streamlit Secrets 설정을 확인해주세요.")
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# 기능 함수들
# =========================
def load_data():
    response = supabase.table(TABLE_NAME).select("*").execute()
    return pd.DataFrame(response.data)

# 데이터베이스 영문 컬럼명을 설문지용 한글 질문으로 매칭하는 딕셔너리
COLUMN_MAPPING = {
    "timestamp": "타임스탬프",
    "charge_count": "1. 하루 충전 횟수",
    "charge_level": "2. 충전 시작 배터리 양",
    "use_while_charging": "3. 충전 중 사용 여부",
    "place_location": "4. 충전 시 기기 위치",
    "overnight_charging": "5. 밤새 충전 여부",
    "fast_charging": "6. 고속충전 빈도",
    "unplug_at_100": "7. 완충 후 즉시 분리 여부",
    "has_battery_issue": "8. 배터리 이상 경험",
    "issue_symptoms": "8-1. 경험한 이상 증상",
    "bad_habits": "9. 수명 단축 습관 생각",
    "chemical_awareness": "10. 화학반응 인지 여부",
    "willing_to_change": "11. 습관 변경 의향"
}

# =========================
# 메인 제어부 (화면 전환용 세션)
# =========================
st.title("🔋 스마트폰 충전 습관")

if "menu" not in st.session_state:
    st.session_state.menu = "📝 설문지 입력"

menu = st.radio(
    "메뉴 선택", 
    ["📝 설문지 입력", "📊 설문 결과 및 DB"], 
    index=0 if st.session_state.menu == "📝 설문지 입력" else 1,
    horizontal=True
)
st.divider()

# 데이터 미리 로드
try:
    current_df = load_data()
except Exception as e:
    st.error("Supabase 데이터를 불러오지 못했습니다. 테이블명이나 컬럼 설정을 확인해주세요.")
    st.stop()

# =========================
# 화면 1: 설문지 입력
# =========================
if menu == "📝 설문지 입력":
    st.subheader("📱 나의 충전 습관 기록하기")

    with st.form("battery_form"):
        charge_count = st.selectbox(
            "1. 하루에 스마트폰·태블릿을 몇 번 충전하나요?",
            ["① 1회 이하", "② 2회", "③ 3회", "④ 4회 이상"]
        )
        charge_level = st.selectbox(
            "2. 보통 배터리가 어느 정도 남았을 때 충전하나요?",
            ["① 10% 이하일 때", "② 11~30% 정도일 때", "③ 31~50% 정도일 때", "④ 50% 이상 남았을 때도 자주 충전한다"]
        )
        use_while_charging = st.selectbox(
            "3. 충전 중 스마트폰·태블릿을 사용하나요?",
            ["① 항상 사용한다", "② 자주 사용한다", "③ 가끔 사용한다", "④ 거의 사용하지 않는다"]
        )
        place_location = st.multiselect(
            "4. 충전할 때 주로 어디에 올려두나요? (복수 선택 가능)",
            ["① 책상·테이블·바닥 위", "② 침대·이불·베개 위", "③ 주머니나 가방 안", "④ 신경쓰지 않는다"]
        )
        overnight_charging = st.selectbox(
            "5. 밤새 충전기를 꽂아두는 편인가요?",
            ["① 예", "② 아니오"]
        )
        fast_charging = st.selectbox(
            "6. 고속충전을 얼마나 자주 사용하나요?",
            ["① 항상 사용한다", "② 자주 사용한다", "③ 가끔 사용한다", "④ 거의 사용하지 않는다"]
        )
        unplug_at_100 = st.selectbox(
            "7. 기기가 완충(100%) 되면 바로 충전 케이블을 분리하나요?",
            ["① 항상 분리한다", "② 자주 분리한다", "③ 가끔 분리한다", "④ 거의 분리하지 않는다"]
        )
        has_battery_issue = st.selectbox(
            "8. 스마트폰·태블릿의 배터리 이상 증상을 경험한 적이 있나요?",
            ["① 예", "② 아니오"]
        )
        issue_symptoms = st.multiselect(
            "8-1. 8번 질문에서 '예'라고 답한 경우, 어떤 증상을 경험하였나요? (복수 선택 가능)",
            ["① 충전 중 기기가 심하게 뜨거워진 적이 있다", "② 완충 후 배터리가 빨리 닳는다", "③ 배터리가 갑자기 꺼진 적이 있다", "④ 배터리가 부풀어 오른 적이 있다"]
        )
        bad_habits = st.multiselect(
            "9. 배터리 수명을 단축시킬 수 있다고 생각하는 충전 습관은 무엇인가요? (복수 선택 가능)",
            ["① 충전 중 기기 사용", "② 과열되기 쉬운 환경에서 충전 (예: 이불·베개 위)", "③ 고속 충전을 반복적으로 사용", "④ 밤새 충전", "⑤ 완충 (100%) 후에도 충전을 계속할 때", "⑥ 방전 (0%) 후 충전하기", "⑦ 잘 모르겠다"]
        )
        chemical_awareness = st.selectbox(
            "10. 배터리 발열과 수명 단축이 내부 화학 반응과 관련 있다는 사실을 알고 있나요?",
            ["① 잘 알고 있다", "② 어느 정도 안다", "③ 들어본 적은 있다", "④ 전혀 모른다"]
        )
        willing_to_change = st.selectbox(
            "11. 잘못된 충전 습관이 화재 위험으로 이어질 수 있다면, 충전 습관을 바꿀 의향이 있나요?",
            ["① 예", "② 아니오"]
        )

        submitted = st.form_submit_button("💾 설문 결과 제출하기")

    if submitted:
        # 멀티셀렉트(리스트) 데이터는 문자열로 합쳐서 저장
        place_location_str = ", ".join(place_location) if place_location else ""
        issue_symptoms_str = ", ".join(issue_symptoms) if issue_symptoms else ""
        bad_habits_str = ", ".join(bad_habits) if bad_habits else ""

        data = {
            "charge_count": charge_count,
            "charge_level": charge_level,
            "use_while_charging": use_while_charging,
            "place_location": place_location_str,
            "overnight_charging": overnight_charging,
            "fast_charging": fast_charging,
            "unplug_at_100": unplug_at_100,
            "has_battery_issue": has_battery_issue,
            "issue_symptoms": issue_symptoms_str,
            "bad_habits": bad_habits_str,
            "chemical_awareness": chemical_awareness,
            "willing_to_change": willing_to_change
        }

        try:
            supabase.table(TABLE_NAME).insert(data).execute()
            st.success("🎉 설문 데이터가 안전하게 수집되었습니다!")
            st.balloons()
            
            st.session_state.menu = "📊 설문 결과 및 DB"
            st.rerun()
        except Exception as e:
            st.error(f"저장 실패: {e}")

# =========================
# 화면 2: 설문 결과 및 DB
# =========================
else:
    st.subheader("📊 충전 습관 실시간 누적 통계")
    
    if current_df.empty:
        st.info("아직 데이터베이스에 누적된 데이터가 없습니다.")
    else:
        # 컬럼 순서 정렬 및 한글 변환
        available_cols = [col for col in COLUMN_MAPPING.keys() if col in current_df.columns]
        df_display = current_df[available_cols].rename(columns=COLUMN_MAPPING)
        
        # 1. 데이터프레임 데이터 표 출력
        st.dataframe(df_display, use_container_width=True, height=300)
        st.success(f"🔥 현재 총 {len(current_df)}명의 스마트폰 충전 데이터가 실시간 분석 중입니다.")

        # 2. 실시간 대시보드 그래프 분석
        st.markdown("---")
        st.markdown("### 📈 핵심 충전 습관 통계 분석")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### 🔌 하루 평균 충전 횟수 분포")
            if "charge_count" in current_df.columns:
                st.bar_chart(current_df["charge_count"].value_counts())

        with col2:
            st.markdown("##### 🔄 충전 중 기기 사용 빈도")
            if "use_while_charging" in current_df.columns:
                st.bar_chart(current_df["use_while_charging"].value_counts())

        # 3. 상세 항목 요약 분석 (Metric 표시)
        st.markdown("---")
        st.markdown("### 🔍 위험 요인 및 인지 요약 요약")
        m_col1, m_col2, m_col3 = st.columns(3)
        
        with m_col1:
            if "overnight_charging" in current_df.columns:
                # 밤새 꽂아두는 '예'의 비율 계산
                overnight_counts = current_df["overnight_charging"].value_counts(normalize=True) * 100
                yes_ratio = overnight_counts.get("① 예", overnight_counts.get("예", 0))
                st.metric(label="🛌 밤새 충전기 꽂아둠", value=f"{yes_ratio:.1f} %")
                
        with m_col2:
            if "has_battery_issue" in current_df.columns:
                # 배터리 이상 경험 비율 계산
                issue_counts = current_df["has_battery_issue"].value_counts(normalize=True) * 100
                issue_ratio = issue_counts.get("① 예", issue_counts.get("예", 0))
                st.metric(label="⚠️ 배터리 이상 증상 경험률", value=f"{issue_ratio:.1f} %")
                
        with m_col3:
            if "willing_to_change" in current_df.columns:
                # 습관 변경 의향 비율 계산
                change_counts = current_df["willing_to_change"].value_counts(normalize=True) * 100
                change_ratio = change_counts.get("① 예", change_counts.get("예", 0))
                st.metric(label="💡 습관 개선 의향률", value=f"{change_ratio:.1f} %")

        # 인지 정보 요약 피드백
        if "chemical_awareness" in current_df.columns:
            aware_count = current_df["chemical_awareness"].str.contains("잘 알고 있다|어느 정도 안다").sum()
            aware_ratio = (aware_count / len(current_df)) * 100
            st.info(f"💡 응답자 중 배터리 발열과 내부 화학 반응의 연관성을 이해하고 있는 비율은 **{aware_ratio:.1f}%** 입니다.")
