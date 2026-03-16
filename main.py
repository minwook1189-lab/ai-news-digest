import feedparser
import win32com.client
from groq import Groq
from datetime import datetime, timezone, timedelta
import calendar
import os
import re
from dotenv import load_dotenv

load_dotenv()

def remove_non_korean_cjk(text):
    """한국어·ASCII·이모지만 유지, 나머지 외국 문자 제거 (화이트리스트 방식)"""
    return re.sub(
        r'[^\u0000-\u024F'       # ASCII + 라틴 확장 (영어·특수문자·URL)
        r'\uAC00-\uD7AF'         # 한글 음절
        r'\u1100-\u11FF'         # 한글 자모
        r'\u3130-\u318F'         # 한글 호환 자모
        r'\u2000-\u206F'         # 일반 구두점
        r'\u2100-\u218F'         # 문자형 기호
        r'\u2600-\u27BF'         # 기타 기호 (⚠️ 등)
        r'\U0001F000-\U0001FFFF' # 이모지 (🔗💡 등)
        r']',
        '', text
    )

GROQ_API_KEY    = os.getenv('GROQ_API_KEY')
SMTP_EMAIL      = os.getenv('SMTP_EMAIL')
SMTP_PASSWORD   = os.getenv('SMTP_PASSWORD')

# 수신자: 쉼표 또는 세미콜론으로 여러 명 지정 가능 (예: "a@mail.com, b@mail.com")
_raw_recipients = os.getenv('RECIPIENT_EMAIL', '')
RECIPIENT_TO = '; '.join(
    r.strip() for r in _raw_recipients.replace(',', ';').split(';') if r.strip()
)

RSS_FEEDS = [
    # 미디어/저널리즘 (공식 출처 — 신뢰도 높음)
    ('MIT Technology Review', 'https://www.technologyreview.com/feed/',                                    False),
    ('Wired AI',              'https://www.wired.com/feed/category/artificial-intelligence/latest/rss',    False),
    ('Ars Technica',          'https://feeds.arstechnica.com/arstechnica/technology-lab',                  False),
    ('The Verge AI',          'https://www.theverge.com/ai-artificial-intelligence/rss/index.xml',         False),
    # 연구·학술 (공식 출처 — 신뢰도 높음)
    ('DeepMind Blog',         'https://deepmind.google/blog/rss.xml',                                      False),
    ('Hugging Face Blog',     'https://huggingface.co/blog/feed.xml',                                      False),
    ('The Gradient',          'https://thegradient.pub/rss/',                                              False),
    # 산업·스타트업 (공식 출처 — 신뢰도 높음)
    ('TechCrunch AI',         'https://techcrunch.com/category/artificial-intelligence/feed/',             False),
    ('VentureBeat AI',        'https://venturebeat.com/category/ai/feed/',                                 False),
    # 뉴스레터·큐레이션 (공식 출처 — 신뢰도 높음)
    ('The Batch (deeplearning.ai)', 'https://www.deeplearning.ai/the-batch/feed/',                         False),
    ('Import AI',             'https://importai.substack.com/feed',                                        False),
    ('Last Week in AI',       'https://lastweekin.ai/feed',                                                False),
    # 커뮤니티 (비공식 출처 — 신뢰도 주의 필요, 100점 이상 인기 게시물만)
    ('Hacker News AI',        'https://hnrss.org/newest?q=AI+LLM+GPT&points=100',                         True),
]

MAX_PER_SOURCE = 3
HOURS_WINDOW   = 48  # 최근 48시간 기사만 수집


def parse_published(entry) -> datetime | None:
    """feedparser의 published_parsed(UTC struct_time)를 UTC datetime으로 변환."""
    t = entry.get('published_parsed') or entry.get('updated_parsed')
    if t:
        return datetime(*t[:6], tzinfo=timezone.utc)
    return None


def format_date(entry) -> str:
    """기사 게시일을 'MM/DD' 형식으로 반환."""
    dt = parse_published(entry)
    if dt:
        kst = dt + timedelta(hours=9)
        return kst.strftime('%m/%d')
    return ''


def fetch_news():
    articles = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=HOURS_WINDOW)

    for source_name, url, is_community in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            count = 0
            for entry in feed.entries:
                if count >= MAX_PER_SOURCE:
                    break
                link = entry.get('link', '')
                if not link.startswith('http'):
                    continue
                pub_dt = parse_published(entry)
                if pub_dt and pub_dt < cutoff:
                    continue  # 오래된 기사 제외
                articles.append({
                    'source':       source_name,
                    'title':        entry.get('title', '').strip(),
                    'link':         link,
                    'summary':      entry.get('summary', '')[:800],
                    'published':    format_date(entry),
                    'is_community': is_community,
                })
                count += 1
            print(f"  [{source_name}] {count}개 수집")
        except Exception as e:
            print(f"  [{source_name}] 오류: {e}")
    return articles


def summarize_with_groq(articles):
    client = Groq(api_key=GROQ_API_KEY)

    today = datetime.now().strftime("%Y년 %m월 %d일")

    def format_article(i, a):
        community_note = " [커뮤니티]" if a.get('is_community') else ""
        return (
            f"[{i+1}] 제목: {a['title']} ({a['published']})\n"
            f"출처: {a['source']}{community_note}\n"
            f"링크: {a['link']}\n"
            f"내용: {a['summary']}"
        )

    content = "\n\n".join([format_article(i, a) for i, a in enumerate(articles)])

    prompt = f"""당신은 AI 전문 뉴스 큐레이터입니다.
아래는 {today} 수집된 AI 관련 뉴스입니다. 다음 지침에 따라 정리해주세요.

⚠️ 언어 규칙 (반드시 준수):
- 모든 출력은 한국어로만 작성. 영어 단어·외국어 단어를 문장 중간에 절대 섞지 말 것
- 회사명·제품명·고유명사(예: OpenAI, ChatGPT, TechCrunch)만 영어 허용
- 일반 단어는 예외 없이 한국어로 번역 (lawyer→변호사, psychosis→정신증, report→보고서 등)
- 뉴스 제목도 반드시 자연스러운 한국어로 완전히 번역

지침:
1. 뉴스를 카테고리별로 분류 (예: 대형 언어 모델, AI 기업 동향, 연구·기술, 정책·규제, 기타)
2. 각 뉴스를 2~3문장으로 요약 — 한국어 원어민이 쓴 것처럼 자연스럽게 작성. 직역 투·나열식 표현 금지. 문장은 반드시 완전한 형태로 끝낼 것 (절단 금지)
3. 각 항목에 반드시 출처명, 원문 링크, 게시일(MM/DD)을 그대로 포함 (링크를 절대 수정하지 말 것)
4. 중복되거나 덜 중요한 뉴스는 제외
5. 기사가 없는 카테고리는 출력하지 말 것 — 절대 내용을 지어내지 말 것
6. 출처에 [커뮤니티] 표시가 있는 항목은 링크 앞에 ⚠️를 붙이고, 출처명 뒤에 "(커뮤니티 출처, 정확도 확인 권장)"을 추가할 것
7. HTML 형식으로 출력 (이메일 본문용)

뉴스 목록:
{content}

출력 형식 (HTML):
<h3>카테고리명</h3>
<ul>
  <li>
    <b>뉴스 제목</b> <span class="date">MM/DD</span><br>
    요약 내용 (2~3문장)<br>
    🔗 <a href="원문링크그대로">출처명</a>
    <!-- 커뮤니티 출처인 경우: ⚠️ <a href="원문링크그대로">출처명</a> (커뮤니티 출처, 정확도 확인 권장) -->
  </li>
</ul>
"""
    response = client.chat.completions.create(
        model='gemma2-9b-it',
        messages=[
            {'role': 'system', 'content': '당신은 한국어 전문 AI 뉴스 큐레이터입니다. 반드시 한국어로만 답변하세요. 일본어, 중국어, 영어 등 한국어 이외의 언어는 절대 사용하지 마세요.'},
            {'role': 'user', 'content': prompt},
        ],
    )
    return remove_non_korean_cjk(response.choices[0].message.content)


def get_ai_tip():
    client = Groq(api_key=GROQ_API_KEY)
    prompt = """AI 업계에서 자주 등장하는 용어나 개념 하나를 골라 설명해주세요.
대상은 비전공자지만 AI에 관심 있는 직장인입니다. 매번 다른 주제로 선택하세요.
주제 예시: LLM, RAG, MCP, 파인튜닝, 임베딩, 토크나이저, 추론(inference), 컨텍스트 윈도우,
프롬프트 엔지니어링, 에이전트, 벡터DB, 멀티모달, RLHF, 할루시네이션, CLI, API 등.

⚠️ 중요: 모든 출력은 반드시 한국어로만 작성하세요. 영어나 다른 언어는 절대 사용하지 마세요.

다음 구조로 한국어 HTML을 작성하세요:
- 용어 이름과 한 줄 정의
- 비유나 실생활 예시로 쉽게 설명 (2~3문장)
- 왜 중요한지 또는 어디에 쓰이는지 (1~2문장)

HTML 형식 (아래를 그대로 따를 것):
<b>💡 오늘의 AI 용어: [용어명]</b><br>
내용
"""
    response = client.chat.completions.create(
        model='gemma2-9b-it',
        messages=[
            {'role': 'system', 'content': '당신은 한국어 AI 교육 전문가입니다. 반드시 한국어로만 답변하세요. 일본어, 중국어, 영어 등 한국어 이외의 언어는 절대 사용하지 마세요.'},
            {'role': 'user', 'content': prompt},
        ],
    )
    return remove_non_korean_cjk(response.choices[0].message.content)


def send_email(html_summary, ai_tip):
    today = datetime.now().strftime("%Y년 %m월 %d일")
    weekday = ['월', '화', '수', '목', '금', '토', '일'][datetime.now().weekday()]

    html_body = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', Arial, sans-serif;
    background: #f0f2f5;
    color: #2d2d2d;
    padding: 24px 12px;
  }}
  .wrapper {{
    max-width: 680px;
    margin: 0 auto;
  }}
  .body {{
    background: #ffffff;
    padding: 32px;
    border-left: 1px solid #dde2ea;
    border-right: 1px solid #dde2ea;
  }}
  h3 {{
    font-size: 12px;
    font-weight: 700;
    color: #1558d6;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin: 32px 0 14px;
    padding-bottom: 8px;
    border-bottom: 2px solid #dde9ff;
  }}
  h3:first-child {{ margin-top: 0; }}
  ul {{
    list-style: none;
    padding: 0;
  }}
  li {{
    background: #f8f9fc;
    border: 1px solid #e4e8f0;
    border-left: 3px solid #1558d6;
    border-radius: 0 8px 8px 0;
    padding: 14px 16px;
    margin-bottom: 10px;
    line-height: 1.75;
  }}
  li b {{
    font-size: 14px;
    color: #111827;
    display: inline;
  }}
  .date {{
    display: inline-block;
    font-size: 10px;
    color: #ffffff;
    background: #6b7eb8;
    border-radius: 3px;
    padding: 1px 5px;
    margin-left: 6px;
    font-weight: 600;
    vertical-align: middle;
  }}
  .summary {{
    font-size: 13px;
    color: #4b5563;
    margin-top: 6px;
    line-height: 1.7;
  }}
  li a {{
    color: #1558d6;
    text-decoration: none;
    font-weight: 500;
    font-size: 12px;
  }}
  li a:hover {{ text-decoration: underline; }}
  .tip-box {{
    background: #fffbeb;
    border: 1px solid #fcd34d;
    border-radius: 8px;
    padding: 18px 20px;
    margin-top: 32px;
    font-size: 13px;
    color: #374151;
    line-height: 1.8;
  }}
  .footer {{
    background: #f0f2f5;
    border: 1px solid #dde2ea;
    border-top: none;
    border-radius: 0 0 12px 12px;
    padding: 16px 32px;
    text-align: center;
    font-size: 11px;
    color: #9ca3af;
    line-height: 1.9;
  }}
</style>
</head>
<body>
  <div class="wrapper">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#1558d6;border-radius:12px 12px 0 0;">
      <tr>
        <td style="padding:28px 32px;font-family:'Malgun Gothic',Arial,sans-serif;">
          <div style="font-size:11px;letter-spacing:2px;color:#a8c4ff;margin-bottom:8px;">AI NEWS DIGEST</div>
          <div style="font-size:24px;font-weight:700;color:#ffffff;margin-bottom:6px;">오늘의 AI 뉴스</div>
          <div style="font-size:13px;color:#c5d8ff;">{today} ({weekday}요일)</div>
        </td>
      </tr>
    </table>
    <div class="body">
      {html_summary}
      <div class="tip-box">
        {ai_tip}
      </div>
    </div>
    <div class="footer">
      매일 오전 9시(KST) 자동 발송<br>
      수신 거부를 원하시면 회신해 주세요
    </div>
  </div>
</body>
</html>"""

    outlook = win32com.client.Dispatch('Outlook.Application')
    mail = outlook.CreateItem(0)
    mail.To       = RECIPIENT_TO
    mail.Subject  = f'[AI 뉴스] {today} ({weekday}) 주요 소식'
    mail.HTMLBody = html_body
    mail.Send()

    print(f"  이메일 발송 완료 → {RECIPIENT_TO}")


def main():
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{now}] AI 뉴스 수집 시작")

    articles = fetch_news()
    print(f"  총 {len(articles)}개 기사 수집")

    if not articles:
        print("  수집된 기사 없음, 종료")
        return

    print("  Groq으로 요약 중...")
    summary = summarize_with_groq(articles)

    print("  AI 지식 생성 중...")
    tip = get_ai_tip()

    print("  이메일 발송 중...")
    send_email(summary, tip)

    print("  완료")


if __name__ == '__main__':
    main()
