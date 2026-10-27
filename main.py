import streamlit as st
st.title('나의 첫 웹 서비스 만들기!')
st.text_input('이름을 입력하세요')
st.selectbox('좋아하는 음식을 입력하세요',['타코야끼','김치찌개','파스타','떡볶이'])
st.button('인사말 생성')
