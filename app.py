import os
import streamlit as st
import google.generativeai as genai

# 페이지 설정
st.set_page_config(page_title="math_avsb - 수학 문항 검수 AI 대항군", layout="wide", page_icon="📐")

# 1. 사이드바 API Key
st.sidebar.header("🔑 설정")
api_key = st.sidebar.text_input("Gemini API Key 입력", type="password")

st.title("📐 math_avsb: 수학 변형 문제 및 해설 대항군(Critic) 검수기")
st.markdown("원본 기출문제들과 AI가 창작한 변형 문제를 대조하여 **조건 누락, 계산 오류, 범위 미스매치, 복수정답 가능성**을 칼같이 검증합니다.")

# 2. 파일 업로드 구역
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 1. 원본 기출문제 및 해설 (다중 선택 가능)")
    # accept_multiple_files=True 옵션으로 30여 개 파일 한 번에 선택 가능
    original_files = st.file_uploader(
        "연도별/회차별 원본 기출 파일들을 모두 선택하세요 (.md, .txt)", 
        type=["md", "txt"], 
        accept_multiple_files=True, 
        key="origin"
    )

with col2:
    st.subheader("📝 2. 변형 문제 (5문항 등)")
    generated_file = st.file_uploader(
        "검증할 변형 문제 및 해설 파일 선택 (.md, .txt)", 
        type=["md", "txt"], 
        key="gen"
    )

exam_info = st.text_input("문항 정보 / 식별자 (예: 2026학년도 수능 수학 22번 변형)", value="수학 변형문항 검수")

# 3. 검증 실행
if st.button("🚀 수학 대항군 문항 감사 시작"):
    if not api_key:
        st.error("좌측 사이드바에 Gemini API Key를 먼저 입력해주세요!")
    elif not original_files or not generated_file:
        st.warning("원본 기출 파일(최소 1개 이상)과 변형 문제 파일을 모두 업로드해주세요.")
    else:
        genai.configure(api_key=api_key.strip())
        
        try:
            # 여러 개의 원본 파일 텍스트를 하나로 자동 병합
            origin_text = ""
            for file in original_files:
                content = file.read().decode("utf-8")
                origin_text += f"\n\n=========================================\n"
                origin_text += f"📄 [참조 원본 파일명: {file.name}]\n"
                origin_text += f"=========================================\n\n"
                origin_text += content
            
            gen_text = generated_file.read().decode("utf-8")
            
            with st.spinner(f"총 {len(original_files)}개의 원본 기출을 병합하여 대항군이 조건, 계산, 정의역 범위, 복수정답 가능성을 정밀 검증 중입니다..."):
                
                gen_model = genai.GenerativeModel("gemini-3.8-flash")
                
                # 대항군(Critic) 프롬프트
                prompt_critic = f"""
                너는 대한민국 최고 권위의 수능 수학 출제 위원이자 냉철한 문항 감수 전문가(대항군)다.
                제공된 [통합 원본 기출 및 해설] 데이터베이스의 출제 코드와 AI가 만든 [변형 문제 및 해설]을 대조하여 아래의 5대 수학적 정합성 기준으로 엄격하게 감사하라.

                [수학 문항 5대 검증 기준]:
                1. 조건 및 정의역·범위 정합성: 원본이 가진 제한 조건(예: 최고차항 계수, 최고차수, 정의역 범위, 부등호 방향, 실수/정수/자연수 조건 등)이 변형 과정에서 누락되거나 왜곡되어 해가 무수히 나오거나 성립하지 않는 오류가 없는가?
                2. 계산 및 풀이 과정의 무결성: 변형된 식의 전개, 미적분, 확률·통계, 수열 등의 계산 과정에서 산술적 오타나 논리적 비약이 전혀 없는지 처음부터 끝까지 직접 계산하여 검증하라.
                3. 선지(보기)의 타당성 및 오답 유도력: 객관식/단답형 정답이 명확하게 도출되는지, 그리고 오답 선지들이 수험생이 흔히 하는 실수(착각, 계산 실수 등)를 저격할 수 있도록 설계되었는지 확인하라.
                4. 교육과정 및 출제 의도 유지 여부: 원본 기출이 요구하는 핵심 개념(수학적 본질)을 변형 문항이 정확히 승계하고 있는지 평가하라.
                5. 발문의 명확성: 문장의 표현이나 수학적 기호가 모호하여 학생이 문항의 의도를 오해할 여지가 없는지 점검하라.

                [검증 지침]:
                - 5개 변형 문항 각각에 대해 (1번~5번) 번호별로 검증 결과를 명확히 구분하여 작성하라.
                - 치명적인 오류(계산 오류, 조건 누락, 해가 없는 문제 등)가 하나라도 발견되면 최상단에 [승인 불가 및 정정 요구]를 명시하고 해당 오류와 수정된 완벽한 문항/해설을 제시하라.
                - 오류가 전혀 없고 완벽하다면 최상단에 [승인]을 적어라.

                [통합 원본 기출 및 해설 DB (총 {len(original_files)}개 파일 병합본)]:
                {origin_text}

                [검증 대상 변형 문제 및 해설]:
                {gen_text}
                """
                
                audit_res = gen_model.generate_content(prompt_critic)
                audit_result = audit_res.text
                
            st.success(f"총 {len(original_files)}개 기출 파일 병합 완료 및 대항군 감사가 끝났습니다!")
            
            st.markdown("---")
            st.subheader("🛡️ math_avsb 대항군(Critic) 문항 감사 리포트")
            st.markdown(audit_result)
            
            # 다운로드 버튼
            st.download_button(
                label="📥 문항 감사 리포트(.md) 다운로드",
                data=audit_result,
                file_name=f"math_audit_{exam_info}.md",
                mime="text/markdown"
            )

        except Exception as e:
            st.error(f"❌ 실행 중 오류가 발생했습니다: {str(e)}")
            st.info("💡 팁: 파일 개수가 너무 많거나 용량이 크면 나누어 업로드하거나 네트워크 상태를 확인하세요.")
