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
set_text(by_id(s1,82),['1 / 6 page'])

# ---------- Slide 2 ----------
s2=S[1]
set_text(by_id(s2,29),['발효와 추출로','대체소재를 만드는','기술창업가'])
set_text(by_id(s2,28),[
 '발효·추출 기술로 커피·카카오 등 글로벌 원자재를 대체하는 소재를 개발하는 스코비아일랜드의 대표입니다. 제주대학교에서 동물생명공학을 전공하고, 미래셀바이오에서 국가연구과제(R&D)와 상품기획을, LG상사 인니팜사업부에서 인사와 해외 농장개발을 경험한 뒤 2023년 창업했습니다.',
 '창업 후 특허 3건을 출원해 2건의 등록결정을 받았고, 청년창업사관학교·신사업창업사관학교·농식품 벤처육성 지원사업·LIPS II 등 정부 창업지원사업에 연이어 선정되어 수행했습니다. 대학·창업지원기관에서 선배 창업가 특강, MVP 전략 강의, 해커톤 멘토링을 진행하고 있으며, 정부 창업지원 프로그램 평가위원과 R&D 과제기획 연구위원으로도 참여하고 있습니다.'])
by_id(s2,28).height=Emu(1900000)
set_text(by_id(s2,32),['대표 · 경영 총괄'])
set_text(by_id(s2,33),['추출·발효 기반 대체소재(대체커피·대체카카오·천연색소·바이오 대체가죽) 개발 및 B2B 공급','스코비 활용 반려견 식이섬유 간식 개발 — 특허 3건 출원, 2건 등록결정','정부 창업지원사업 5건 이상 선정·수행, AFPRO 2026 등 국내외 박람회 참가'])
by_id(s2,33).height=Emu(900000)
set_text(by_id(s2,37),['인도네시아 팜오일 사업부 인사(HR) 및 농장개발 업무','해외 현지 법인·농장 운영 지원'])
set_text(by_id(s2,51),['국가연구과제(R&D) 수행','바이오 소재 기반 상품기획'])
set_text(by_id(s2,58),['2 / 6 page'])

# ---------- new slides cloned from slide 3 template ----------
s3=S[2]
PML='{http://schemas.openxmlformats.org/presentationml/2006/main}'
TPL=[copy.deepcopy(e) for e in s3.shapes._spTree if e.tag in (PML+'sp',PML+'cxnSp')]
def build_list_slide(title, page, rows, row_h):
    new=p.slides.add_slide(s3.slide_layout)
    for sh in list(new.shapes): sh._element.getparent().remove(sh._element)
    tree=new.shapes._spTree
    header=TPL[:4]; row=TPL[4:12]
    for e in header: tree.append(copy.deepcopy(e))
    shapes=list(new.shapes)
    set_text(shapes[1],[title]); set_text(shapes[2],[page])
    for i,(date,org,name,desc,lab1,lab2) in enumerate(rows):
        dy=i*row_h
        for e in row: tree.append(copy.deepcopy(e))
        rs=list(new.shapes)[-8:]
        for sh in rs: sh.top=Emu(sh.top+dy)
        set_text(rs[0],[org]); set_text(rs[1],date); set_text(rs[4],[lab1]); set_text(rs[5],[lab2]); set_text(rs[6],[name]); set_text(rs[7],[desc])
    return new

L=[
 (['2026. 10. 08'],'제주대학교 RISE사업단 창업지원팀','교과목 「창업성공스토리」 특강','강사 · 제주대 재학생 60명 내외 · 창업 계기, 사업 운영 과정, 경험담 · 교양강의동 4128호 · 16:00–17:50','행사명','역할·내용'),
 (['2026. 09. 30'],'제주더큰내일센터 (운영 MYSC)','탐나는인재 12기 창업트랙 1단계 이수식 — 선배 창업가 특강·패널 토크쇼','강사 및 패널 · 창업트랙 12기 17명 · 사업 소개, 창업 과정 공유, 질의응답 · 센터 3층 라운지','행사명','역할·내용'),
 (['2026. 09. 12'],'제주패스파인더 · 뉴키즈인베스트먼트','창업기수제 「패스파이오니어 3기」','강사 · "MVP 사례 및 온·오프라인 MVP 전략과 실무" + 지원사업 활용 팁 · 예비창업자 15팀 · 15:00–17:00','행사명','역할·내용'),
 (['2026. 09. 03'],'뉴키즈인베스트먼트','창업가 조찬모임','연사 · 창업 경험 공유','행사명','역할·내용'),
 (['2026. 08. 21'],'제주대학교 창업보육센터 (중기부·창업진흥원 주관)','「모두의 창업 프로젝트」 1기 2라운드 진출평가','외부 평가위원 · 1라운드 진출자 20명 서면평가·채점 및 심의 · 제주대 산학협력관 · 14:00–17:00','행사명','역할·내용'),
 (['2026. 08. 04 –','2026. 08. 06'],'제주더큰내일센터',"탐나는인재 13기 선발 면접과정 '넥스톤' (2박3일)",'멘토단으로 참여 · 면접대상자, 멘토단, 운영진 약 100명 · 제주 에코그린리조트','행사명','역할·내용'),
 (['2026. 06'],'제주테크노파크 정책기획단','수요기반 R&D과제 기획 지원사업','비상임연구위원 위촉 · 과제 기획보고서 작성 참여','행사명','역할·내용'),
 (['2026. 02. 03 –','2026. 02. 05'],'제주더큰내일센터 (운영 잇지제주)',"탐나는인재 12기 해커톤 '넥스톤 : The Questioner' (2박3일)",'멘토 (2팀 전담) · 팀 프로젝트 멘토링, 관찰평가, 최종 피칭 심사 · 참여자 약 60명, 14팀 · 에코그린리조트','행사명','역할·내용'),
 (['2025. 06'],'제주더큰내일센터','업프로젝트 [기업 과제해결 프로젝트]','기업멘토 · 참여 청년 대상 계획 코칭 및 멘토링 · 최종발표회 참여','행사명','역할·내용'),
 (['2025. 05'],'소상공인시장진흥공단 · 와이앤아처(주)','신사업창업사관학교(제주) 18기 선배 창업가 특강','강사 · 창업 실패 사례와 실무 팁, 원가분석·지원사업 활용 · 강의 후 수강생 사업계획서·IR 피드백','행사명','역할·내용'),
 (['2024. 11. 15'],'와이앤아처(주)','Y-Beginner Camp (제주)','예비창업자 1:1 멘토링 (주제: R&D, 기술창업) · 15:00–18:00 · 유탑유블레스호텔 제주(함덕)','행사명','역할·내용'),
 (['2023. 11. 16'],'언더독스 / 하나금융그룹','하나 소셜벤처 유니버시티 제주 워케이션 마르쉐','연사로 참여 · 창업팀 26팀(52명)의 아이템 설명을 듣고 현장 피드백 제공 · 라마다프라자 제주호텔','행사명','역할·내용'),
 (['2023. 11. 10'],'제주대학교 진로취업과','진로·취창업 특강 (파주시진로지원센터 창업경진대회 수상 고교생 대상)','강사 · 수상 고등학생, 교사 등 18명 · 제주대학교 중앙도서관 라이브러리홀 · 13:30–14:30','행사명','역할·내용'),
]
build_list_slide('LECTURE · MENTORING · JUDGING (1/2)','3 / 6 page',L[:7],1250000)
build_list_slide('LECTURE · MENTORING · JUDGING (2/2)','4 / 6 page',L[7:],1250000)

topics=[
 (['주제 ①'],'기술창업과 R&D 사업화','예비창업자, 대학생 · 60~120분','연구과제·특허를 제품과 매출로 연결하는 과정 / 대기업·연구소 출신 창업가의 실제 사례','대상','내용'),
 (['주제 ②'],'선정되는 정부 창업지원사업 활용법','예비창업자, 초기 창업기업 · 90~120분','청창사·신사업창업사관학교·농식품 벤처육성·LIPS II 선정 경험 기반 사업계획서 작성 포인트와 사업비 운영','대상','내용'),
 (['주제 ③'],'발효·대체소재 창업 사례','대학생, 예비창업자 · 60분','콤부차 부산물(스코비)에서 대체커피·대체카카오·바이오 가죽까지, 발효 기반 제품 개발 스토리','대상','내용'),
 (['주제 ④'],'진로·취창업 특강','대학생, 고교생 · 60분','대기업(LG상사)·바이오 연구소를 거쳐 창업까지, 전공을 살린 진로 설계','대상','내용'),
 (['주제 ⑤'],'MVP 사례와 온·오프라인 MVP 전략','예비창업자, 창업팀 · 120분','아이디어 검증 단계의 실제 MVP 사례 / 온라인(메타 광고 타겟 설정)·오프라인(입점 절차) 실무 전략','대상','내용'),
 (['주제 ⑥'],'AX 실무: 1인 기업의 AI 활용','예비창업자, 소상공인, 창업팀 · 120분(실습)','AI 도구로 사업계획서·IR·행정문서 작성과 지원사업 관리를 자동화하는 실무 워크숍','대상','내용'),
]
build_list_slide('LECTURE TOPICS','5 / 6 page',topics,1450000)

ach=[
 (['2026. 08 –','2026. 10'],'특허 (지식재산처)','반려견용 섬유질 간식 및 이의 제조방법 (10-2023-0167491)','등록결정 · 등록료 납부 완료 · 출원 2023. 11. 28 · 출원인/발명자 강상경','항목','내용'),
 (['2026. 09'],'특허 (지식재산처)','미생물 셀룰로오스의 제조방법 (10-2023-0167492)','등록결정 · 출원 2023. 11. 28 / 다용도 미생물 셀룰로오스의 제조방법(10-2024-0122507) 심사 중','항목','내용'),
 (['2026. 06 – 07'],'한국농업기술진흥원 · 한국엔젤투자협회','AFPRO 2026 참가 · 호남 엔젤리더스포럼 IR 발표기업 선정','제4회 농식품 테크 스타트업 창업박람회(코엑스) 감사장 수령, 에이빙뉴스 보도 · IR 발표기업 4개사 선정(6. 25)','항목','내용'),
 (['2026. 04'],'한국농업기술진흥원 호남A+센터','2026년 농식품 벤처육성 지원사업','창업기업 선정 · 협약 체결 (사업화자금 지원)','항목','내용'),
 (['2025. 09 – 10'],'중소벤처기업부 · 소상공인시장진흥공단','혁신소상공인 투자연계지원사업(LIPS II) 초기투자','선정 / 제주지식재산센터 IP디딤돌 후속지원(포장디자인) 선정(9월)','항목','내용'),
 (['2024'],'중소벤처기업진흥공단 · 와이앤아처(주)','제주청년창업사관학교 14기','입교 · 졸업 / 제주관광대학교 창업보육센터 입주기업 선정(4월)','항목','내용'),
 (['2022 – 2024'],'소상공인시장진흥공단 · 제주더큰내일센터','신사업창업사관학교(제주) 16기 · 탐나는인재 6기','신사업창업사관학교 졸업 및 제주지역 우수사례 2년 연속 선정(2023·2024) · 탐나는인재 6기 수료','항목','내용'),
]
build_list_slide('PATENT & ACHIEVEMENT','6 / 6 page',ach,1250000)

# remove original slide 3
sldIdLst=p.slides._sldIdLst
sld=list(sldIdLst)[2]
p.part.drop_rel(sld.rId); sldIdLst.remove(sld)

p.save('/home/user/-/resume/강상경_강사이력서_보완본.pptx')
print('saved')
