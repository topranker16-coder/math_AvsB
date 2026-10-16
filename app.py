from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import streamlit as st

def create_text_pdf(title, content, filename="document.pdf"):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    margin = 50
    y = height - margin
    
    # 제목 작성
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y, title)
    y -= 40
    
    # 본문 작성
    c.setFont("Helvetica", 11)
    lines = content.split('\n')
    for line in lines:
        while len(line) > 0:
            if y < margin:
                c.showPage()
                c.setFont("Helvetica", 11)
                y = height - margin
            
            chunk = line[:80]
            c.drawString(margin, y, chunk)
            line = line[80:]
            y -= 20
            
    c.save()
    return filename

st.set_page_config(page_title="텍스트 PDF 변환기", page_icon="✍️", layout="centered")

st.title("✍️ 복사한 텍스트로 PDF 만들기")
st.write("대화 내용이나 공부한 텍스트를 붙여넣어 깔끔한 PDF 노트로 만들어보세요!")

doc_title = st.text_input("문서 제목을 입력하세요", "소방 공부 노트")
doc_content = st.text_area("내용을 붙여넣으세요", height=350, placeholder="여기에 텍스트를 붙여넣으세요...")

if st.button("텍스트 PDF 생성하기", key="text_pdf_btn"):
    if doc_content.strip() == "":
        st.warning("내용을 입력해주세요!")
    else:
        pdf_file = create_text_pdf(doc_title, doc_content, "study_note.pdf")
        with open(pdf_file, "rb") as f:
            st.success("텍스트 PDF 문서 생성 완료!")
            st.download_button(
                label="📥 생성된 텍스트 PDF 다운로드", 
                data=f, 
                file_name="study_note.pdf", 
                mime="application/pdf"
            )
