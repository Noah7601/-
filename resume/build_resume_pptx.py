import copy, re
from pptx import Presentation
from pptx.util import Emu
p=Presentation('ppt_src.pptx')
S=list(p.slides)

def set_text(shape, lines):
    """Replace text keeping first run formatting. lines: list of str (paragraphs)."""
    tf=shape.text_frame
    paras=list(tf.paragraphs)
    p0=paras[0]
    r0=p0.runs[0] if p0.runs else None
    tmpl_r=copy.deepcopy(r0._r) if r0 is not None else None
    tmpl_p=copy.deepcopy(p0._p)
    # clear all paragraphs
    txBody=tf._txBody
    for para in paras: txBody.remove(para._p)
    for i,line in enumerate(lines):
        np_=copy.deepcopy(tmpl_p)
        for r in np_.findall('{http://schemas.openxmlformats.org/drawingml/2006/main}r'): np_.remove(r)
        for br in np_.findall('{http://schemas.openxmlformats.org/drawingml/2006/main}br'): np_.remove(br)
        nr=copy.deepcopy(tmpl_r)
        nr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}t').text=line
        # insert run before endParaRPr if present
        end=np_.find('{http://schemas.openxmlformats.org/drawingml/2006/main}endParaRPr')
        if end is not None: end.addprevious(nr)
        else: np_.append(nr)
        txBody.append(np_)

def by_id(slide, sid, nth=0):
    hits=[s for s in slide.shapes if s.shape_id==sid]
    return hits[nth]

# ---------- Slide 1 ----------
s1=S[0]
by_id(s1,39).width=Emu(1800000)              # email no wrap
for sid in (49,50): sp=by_id(s1,sid); sp._element.getparent().remove(sp._element)   # remove high school
chips={20:'창업',51:'R&D',52:'진로',53:'발효',54:'지원',55:'IP',56:'AX',57:'ECO'}
labels={58:'기술창업',59:'R&D 사업화',60:'진로·취창업',61:'발효·대체소재',62:'정부지원사업',63:'특허·지식재산',64:'AI 활용 실무',65:'친환경 제조'}
for sid,tx in chips.items(): set_text(by_id(s1,sid),[tx])
for sid,tx in labels.items(): set_text(by_id(s1,sid),[tx])
by_id(s1,65).left=Emu(5930080); by_id(s1,65).width=Emu(1063869)
# lecture cards -> 3 most recent
set_text(by_id(s1,68),["탐나는인재 13기 '넥스톤'"]); set_text(by_id(s1,71),['Date : 2026. 08. 04–06.','Host : 제주더큰내일센터','Role : 멘토단 (약 100명)'])
set_text(by_id(s1,74),['업프로젝트 기업멘토']);        set_text(by_id(s1,72),['Date : 2025. 06.','Host : 제주더큰내일센터','Role : 계획 코칭·멘토링'])
set_text(by_id(s1,76),['Y-Beginner Camp']);          set_text(by_id(s1,73),['Date : 2024. 11. 15.','Host : 와이앤아처(주)','Role : 예비창업자 1:1 멘토링'])
set_text(by_id(s1,82),['1 / 5 page'])

# ---------- Slide 2 ----------
s2=S[1]
set_text(by_id(s2,29),['발효와 추출로','대체소재를 만드는','기술창업가'])
set_text(by_id(s2,28),[
 '발효·추출 기술로 커피·카카오 등 글로벌 원자재를 대체하는 소재를 개발하는 스코비아일랜드의 대표입니다. 제주대학교에서 동물생명공학을 전공하고, 미래셀바이오에서 국가연구과제(R&D)와 상품기획을, LG상사 인니팜사업부에서 인사와 해외 농장개발을 경험한 뒤 2023년 창업했습니다.',
 '창업 후 특허 3건을 출원해 2건의 등록결정을 받았고, 청년창업사관학교·신사업창업사관학교·농식품 벤처육성 지원사업·LIPS II 등 정부 창업지원사업에 연이어 선정되어 수행했습니다. "선정되는 사업계획서"와 "R&D를 사업화하는 방법"을 대학생·예비창업자에게 현장 사례로 전달하며, 1인 기업의 AI 활용(AX) 실무 강의도 준비하고 있습니다.'])
by_id(s2,28).height=Emu(1900000)
set_text(by_id(s2,32),['대표 · 경영 총괄'])
set_text(by_id(s2,33),['추출·발효 기반 대체소재(대체커피·대체카카오·천연색소·바이오 대체가죽) 개발 및 B2B 공급','스코비 활용 반려견 식이섬유 간식 개발 — 특허 3건 출원, 2건 등록결정','정부 창업지원사업 5건 이상 선정·수행, AFPRO 2026 등 국내외 박람회 참가'])
by_id(s2,33).height=Emu(900000)
set_text(by_id(s2,37),['인도네시아 팜오일 사업부 인사(HR) 및 농장개발 업무','해외 현지 법인·농장 운영 지원'])
set_text(by_id(s2,51),['국가연구과제(R&D) 수행','바이오 소재 기반 상품기획'])
set_text(by_id(s2,58),['2 / 5 page'])

# ---------- Slide 3 ----------
s3=S[2]
set_text(by_id(s3,32,1),['업프로젝트 [기업 과제해결 프로젝트]'])
set_text(by_id(s3,33,1),['기업멘토 · 참여 청년 대상 계획 코칭 및 멘토링 · 최종발표회 참여'])
set_text(by_id(s3,58),['3 / 5 page'])

# ---------- new slides cloned from slide 3 ----------
A='{http://schemas.openxmlformats.org/drawingml/2006/main}'
PML='{http://schemas.openxmlformats.org/presentationml/2006/main}'
def clone_slide(src):
    new=p.slides.add_slide(src.slide_layout)
    for sh in list(new.shapes): sh._element.getparent().remove(sh._element)
    tree=new.shapes._spTree
    els=[e for e in src.shapes._spTree if e.tag in (PML+'sp',PML+'cxnSp')]
    return new, tree, els
def build_list_slide(title, page, rows, row_h):
    new,tree,els=clone_slide(s3)
    header=els[:4]; row=els[4:12]
    for e in header: tree.append(copy.deepcopy(e))
    shapes=list(new.shapes)
    set_text(shapes[1],[title]); set_text(shapes[2],[page])
    y0=1250000
    for i,(date,org,name,desc,lab1,lab2) in enumerate(rows):
        dy=i*row_h - 0
        base_rows=[]
        for e in row:
            c=copy.deepcopy(e); tree.append(c)
        rs=list(new.shapes)[-8:]
        for sh in rs: sh.top=Emu(sh.top+dy)
        # order: 40 org,41 date,45 line,47 line,34 lab,35 lab,32 name,33 desc
        set_text(rs[0],[org]); set_text(rs[1],date); set_text(rs[4],[lab1]); set_text(rs[5],[lab2]); set_text(rs[6],[name]); set_text(rs[7],[desc])
    return new

topics=[
 (['주제 ①'],'기술창업과 R&D 사업화','예비창업자, 대학생 · 60~120분','연구과제·특허를 제품과 매출로 연결하는 과정 / 대기업·연구소 출신 창업가의 실제 사례','대상','내용'),
 (['주제 ②'],'선정되는 정부 창업지원사업 활용법','예비창업자, 초기 창업기업 · 90~120분','청창사·신사업창업사관학교·농식품 벤처육성·LIPS II 선정 경험 기반 사업계획서 작성 포인트와 사업비 운영','대상','내용'),
 (['주제 ③'],'발효·대체소재 창업 사례','대학생, 예비창업자 · 60분','콤부차 부산물(스코비)에서 대체커피·대체카카오·바이오 가죽까지, 발효 기반 제품 개발 스토리','대상','내용'),
 (['주제 ④'],'진로·취창업 특강','대학생, 고교생 · 60분','대기업(LG상사)·바이오 연구소를 거쳐 창업까지, 전공을 살린 진로 설계','대상','내용'),
 (['주제 ⑤'],'AX 실무: 1인 기업의 AI 활용','예비창업자, 소상공인, 창업팀 · 120분(실습)','AI 도구로 사업계획서·IR·행정문서 작성과 지원사업 관리를 자동화하는 실무 워크숍','대상','내용'),
]
build_list_slide('LECTURE TOPICS','4 / 5 page',topics,1700000)

ach=[
 (['2026. 08 –','2026. 10'],'특허 (지식재산처)','반려견용 섬유질 간식 및 이의 제조방법 (10-2023-0167491)','등록결정 · 등록료 납부 완료 · 출원 2023. 11. 28 · 출원인/발명자 강상경','항목','내용'),
 (['2026. 09'],'특허 (지식재산처)','미생물 셀룰로오스의 제조방법 (10-2023-0167492)','등록결정 · 출원 2023. 11. 28 / 다용도 미생물 셀룰로오스의 제조방법(10-2024-0122507) 심사 중','항목','내용'),
 (['2026. 06 – 07'],'한국농업기술진흥원 · 한국엔젤투자협회','AFPRO 2026 참가 · 호남 엔젤리더스포럼 IR 발표기업 선정','제4회 농식품 테크 스타트업 창업박람회(코엑스) 감사장 수령, 에이빙뉴스 보도 · IR 발표기업 4개사 선정(6. 25)','항목','내용'),
 (['2026. 04'],'한국농업기술진흥원 호남A+센터','2026년 농식품 벤처육성 지원사업','창업기업 선정 · 협약 체결 (사업화자금 지원)','항목','내용'),
 (['2025. 09 – 10'],'중소벤처기업부 · 소상공인시장진흥공단','혁신소상공인 투자연계지원사업(LIPS II) 초기투자','선정 · 정부지원금 7,500만 원 / 제주지식재산센터 IP디딤돌 후속지원(포장디자인) 선정(9월)','항목','내용'),
 (['2024'],'중소벤처기업진흥공단 · 와이앤아처(주)','제주청년창업사관학교 14기','입교 · 졸업 / 제주관광대학교 창업보육센터 입주기업 선정(4월)','항목','내용'),
 (['2022 – 2024'],'소상공인시장진흥공단 · 제주더큰내일센터','신사업창업사관학교(제주) 16기 · 탐나는인재 6기','신사업창업사관학교 졸업 및 제주지역 우수사례 2년 연속 선정(2023·2024) · 탐나는인재 6기 수료','항목','내용'),
]
s5=build_list_slide('PATENT & ACHIEVEMENT','5 / 5 page',ach,1250000)

p.save('/home/user/-/resume/강상경_강사이력서_보완본.pptx')
print('saved')
