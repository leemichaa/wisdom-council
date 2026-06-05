import streamlit as st
from lunarcalendar import Converter, Solar, Lunar
import anthropic
import os

# 페이지 설정
st.set_page_config(
    page_title="가족 지혜 위원회",
    page_icon="🌙",
    layout="centered"
)

# 제목
st.markdown("# 🌙 가족 지혜 위원회")
st.markdown("당신의 사주로 보는 인생의 방향")
st.divider()

# 입력 폼
st.subheader("📝 당신의 정보를 입력하세요")

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("이름", placeholder="예: 홍길동")
with col2:
    gender = st.selectbox("성별", ["남성", "여성"])

col1, col2 = st.columns(2)
with col1:
    birth_date = st.text_input("생년월일", placeholder="1985-03-15")
with col2:
    birth_time = st.text_input("출생시간", placeholder="14:30")

question = st.text_area("질문 (선택)", placeholder="올해 운세는? 결혼은?", height=80)

# 분석 버튼
if st.button("🔮 사주 분석하기", use_container_width=True, type="primary"):
    
    if not name:
        st.error("이름을 입력해주세요.")
        st.stop()
    
    if not birth_date or not birth_time:
        st.error("생년월일과 출생시간을 입력해주세요.")
        st.stop()
    
    try:
        year, month, day = map(int, birth_date.split('-'))
        hour, minute = map(int, birth_time.split(':'))
    except:
        st.error("날짜 형식: YYYY-MM-DD, 시간 형식: HH:MM")
        st.stop()
    
    with st.spinner("분석 중..."):
        try:
            # 사주 계산
            solar = Solar(year, month, day, hour, minute, 0)
            lunar = Lunar.fromSolar(solar)
            bazi = lunar.getBaZi()
            
            four_pillars = {
                'year': bazi[0],
                'month': bazi[1],
                'day': bazi[2],
                'hour': bazi[3]
            }
            
            lunar_date = {
                'year': lunar.getYear(),
                'month': lunar.getMonth(),
                'day': lunar.getDay()
            }
            
            # Claude API 호출
            api_key = os.environ.get('ANTHROPIC_API_KEY')
            if not api_key:
                st.error("API 키 미설정")
                st.info("터미널: export ANTHROPIC_API_KEY='sk-ant-...'")
                st.stop()
            
            client = anthropic.Anthropic(api_key=api_key)
            
            prompt = f"""
사주 명리 전문가 답변:
이름: {name} | 성별: {gender}
생년월일: {birth_date} {birth_time}
사주: {four_pillars['year']} {four_pillars['month']} {four_pillars['day']} {four_pillars['hour']}
음력: {lunar_date['year']}년 {lunar_date['month']}월 {lunar_date['day']}일

분석:
1. 성격과 기질
2. 오행 분석
3. 운세
4. 조언

{f"질문: {question}" if question else ""}
"""
            
            response = client.messages.create(
                model="claude-opus-4-1-20250805",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            interpretation = response.content[0].text
            
            # 결과 표시
            st.success("✨ 완료!")
            st.divider()
            
            st.subheader("📊 당신의 사주")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("년주", four_pillars['year'])
            with col2:
                st.metric("월주", four_pillars['month'])
            with col3:
                st.metric("일주", four_pillars['day'])
            with col4:
                st.metric("시주", four_pillars['hour'])
            
            st.info(f"🌙 음력: {lunar_date['year']}년 {lunar_date['month']}월 {lunar_date['day']}일")
            
            st.subheader("✨ 해석")
            st.write(interpretation)
            
        except Exception as e:
            st.error(f"오류: {str(e)}")

st.divider()
st.markdown("""
### 🚀 빠른 시작

**1단계: 설치 (터미널)**
```bash
pip install streamlit lunar_python anthropic --break-system-packages
```

**2단계: API 키 설정**
```bash
export ANTHROPIC_API_KEY='sk-ant-...'
```

**3단계: 실행**
```bash
streamlit run wisdom_council_streamlit.py
```

완료! 자동으로 브라우저가 열립니다.
""")
