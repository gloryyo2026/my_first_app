import streamlit as st
import pandas as pd
from datetime import datetime

# --- 페이지 설정 ---
st.set_page_config(page_title="HyperMesh Process Manager", layout="wide")

# --- 세션 상태 초기화 (데이터 유지용) ---
if 'step_completed' not in st.session_state:
    st.session_state.step_completed = {f"Step {i}": False for i in range(1, 6)}
if 'logs' not in st.session_state:
    st.session_state.logs = []

def add_log(message, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{timestamp}] [{level}] {message}")

# --- 사이드바: 진행 상태 및 로그 ---
with st.sidebar:
    st.title("작업 관리자")
    
    # 전체 진행률
    completed_count = sum(1 for v in st.session_state.step_completed.values() if v)
    progress_percent = completed_count / 5
    st.write(f"전체 진행률: {int(progress_percent*100)}%")
    st.progress(progress_percent)
    
    st.divider()
    st.subheader("작업 로그")
    # 최신 로그가 위로 오게 출력
    log_content = "\n".join(st.session_state.logs[::-1])
    st.text_area("Log View", value=log_content, height=400, disabled=True)

# --- 메인 화면: 단계별 탭 ---
st.title("🛠️ HyperMesh Standard Workflow")

# tkinter의 Notebook 기능을 streamlit의 tabs로 변경
tabs = st.tabs(["Step 1: Setup", "Step 2: Cleanup", "Step 3: Meshing", "Step 4: Property", "Step 5: Boundary"])

# --- Step 1: Setup ---
with tabs[0]:
    st.header("Step 1: 모델 준비")
    
    uploaded_file = st.file_uploader("CAD/HM 파일 업로드", type=['hm', 'stp', 'igs', 'catpart'])
    if uploaded_file:
        st.success(f"파일 업로드 완료: {uploaded_file.name}")
        
    col1, col2 = st.columns(2)
    with col1:
        solver = st.selectbox("Solver 설정", ["OptiStruct", "Abaqus", "Nastran", "LS-DYNA"])
    with col2:
        unit = st.selectbox("단위계 설정", ["mm-ton-s", "m-kg-s", "inch-lb-s"])
        
    if st.button("Step 1 완료"):
        if uploaded_file:
            st.session_state.step_completed["Step 1"] = True
            add_log(f"Step 1 완료 - Solver: {solver}, 단위계: {unit}", "SUCCESS")
            st.rerun()
        else:
            st.error("파일을 먼저 업로드해주세요.")

# --- Step 2: Cleanup (Step 1이 완료되어야 활성화 로직 처리) ---
with tabs[1]:
    if not st.session_state.step_completed["Step 1"]:
        st.warning("Step 1을 먼저 완료해주세요.")
    else:
        st.header("Step 2: 기하 정리")
        if st.button("Free Edge 및 중복 서피스 검사"):
            add_log("기하 검사 시작...", "INFO")
            st.info("검사 중...")
            add_log("Free Edge 3개 발견 / 중복 서피스 1개 발견", "WARNING")
            
        tolerance = st.number_input("자동 봉합 톨러런스", value=0.1)
        if st.button("자동 봉합 실행"):
            add_log(f"자동 봉합 완료 (Tolerance: {tolerance})", "SUCCESS")
            
        if st.button("Step 2 완료"):
            st.session_state.step_completed["Step 2"] = True
            add_log("Step 2 완료 - 기하 정리 완료", "SUCCESS")
            st.rerun()

# --- Step 3: Meshing ---
with tabs[2]:
    if not st.session_state.step_completed["Step 2"]:
        st.warning("Step 2를 먼저 완료해주세요.")
    else:
        st.header("Step 3: 격자 생성")
        mesh_size = st.text_input("Target Element Size", value="5.0")
        elem_type = st.radio("요소 타입", ["Quad", "Tria", "Mixed"], horizontal=True)
        
        if st.button("메싱 실행"):
            add_log(f"메싱 완료: 15,234 요소 생성 (Size: {mesh_size})", "SUCCESS")
            
        if st.button("Step 3 완료"):
            st.session_state.step_completed["Step 3"] = True
            add_log("Step 3 완료 - 메싱 완료", "SUCCESS")
            st.rerun()

# --- Step 4 & 5 도 동일한 방식으로 구성 가능 (생략) ---
with tabs[3]:
    st.write("Step 4 속성 정의 화면입니다.")
    if st.button("Step 4 완료"):
        st.session_state.step_completed["Step 4"] = True
        st.rerun()

with tabs[4]:
    st.write("Step 5 경계 조건 화면입니다.")
    if st.button("전체 작업 완료 및 내보내기"):
        st.balloons()
        add_log("전체 공정 완료 및 Solver Deck 내보내기 준비 완료", "SUCCESS")
