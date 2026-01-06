import streamlit as st
from datetime import datetime

st.title("우리회사 근태관리")

name = st.text_input("직원 성함을 입력하세요")
status = st.radio("상태 선택", ["출근", "퇴근", "외근"])

if st.button("기록하기"):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.success(f"{name}님, {now}에 {status} 처리가 완료되었습니다!")
    # 여기에 나중에 구글 시트 저장 코드를 추가하면 됩니다.