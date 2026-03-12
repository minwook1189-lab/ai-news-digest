import feedparser
import win32com.client
from google import genai
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY  = os.getenv('GEMINI_API_KEY')
SMTP_EMAIL      = os.getenv('SMTP_EMAIL')
SMTP_PASSWORD   = os.getenv('SMTP_PASSWORD')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')

RSS_FEEDS = [
    ('TechCrunch AI',        'https://techcrunch.com/category/artificial-intelligence/feed/'),
    ('VentureBeat AI',       'https://venturebeat.com/category/ai/feed/'),
    ('MIT Technology Review','https://www.technologyreview.com/feed/'),
    ('The Verge AI',         'https://www.theverge.com/ai-artificial-intelligence/rss/index.xml'),
    ('Wired AI',             'https://www.wired.com/feed/category/artificial-intelligence/latest/rss'),
    ('Ars Technica',         'https://feeds.arstechnica.com/arstechnica/technology-lab'),
    ('Google DeepMind',      'https://deepmind.google/blog/rss.xml'),
    ('OpenAI Blog',          'https://openai.com/blog/rss/'),
]

MAX_PER_SOURCE = 4


def fetch_news():
    articles = []
    for source_name, url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:MAX_PER_SOURCE]:
                link = entry.get('link', '')
                if not link.startswith('http'):
                    continue  # 잘못된 링크 제외
                articles.append({
                    'source':    source_name,
                    'title':     entry.get('title', '').strip(),
                    'link':      link,
                    'summary':   entry.get('summary', '')[:800],
                    'published': entry.get('published', ''),
                })
            print(f"  [{source_name}] {min(MAX_PER_SOURCE, len(feed.entries))}개 수집")
        except Exception as e:
            print(f"  [{source_name}] 오류: {e}")
    return articles


def summarize_with_gemini(articles):
    client = genai.Client(api_key=GEMINI_API_KEY)

    today = datetime.now().strftime("%Y년 %m월 %d일")
    content = "\n\n".join([
        f"[{i+1}] 제목: {a['title']}\n출처: {a['source']}\n링크: {a['link']}\n내용: {a['summary']}"
        for i, a in enumerate(articles)
    ])

    prompt = f"""당신은 AI 전문 뉴스 큐레이터입니다.
아래는 {today} 수집된 AI 관련 뉴스입니다. 다음 지침에 따라 한국어로 정리해주세요.

지침:
1. 뉴스를 카테고리별로 분류 (예: 대형 언어 모델, AI 기업 동향, 연구·기술, 정책·규제, 기타)
2. 각 뉴스를 2~3문장으로 핵심만 요약
3. 각 항목에 반드시 출처명과 원문 링크를 그대로 포함 (링크를 절대 수정하지 말 것)
4. 중복되거나 덜 중요한 뉴스는 제외
5. HTML 형식으로 출력 (이메일 본문용)

뉴스 목록:
{content}

출력 형식 (HTML):
<h3>📌 카테고리명</h3>
<ul>
  <li>
    <b>뉴스 제목</b><br>
    요약 내용 (2~3문장)<br>
    🔗 출처: <a href="원문링크그대로">출처명</a>
  </li>
</ul>
"""
    response = client.models.generate_content(
        model='gemini-flash-latest',
        contents=prompt,
    )
    return response.text


def send_email(html_summary):
    today = datetime.now().strftime("%Y년 %m월 %d일")

    html_body = f"""<html>
<head><style>
  body  {{ font-family: 'Malgun Gothic', Arial, sans-serif; max-width: 720px; margin: 0 auto; color: #333; padding: 16px; }}
  h2   {{ color: #1a73e8; border-bottom: 2px solid #1a73e8; padding-bottom: 8px; }}
  h3   {{ color: #2c5f8a; margin-top: 28px; }}
  li   {{ margin-bottom: 18px; line-height: 1.7; }}
  a    {{ color: #1a73e8; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  .footer {{ color: #aaa; font-size: 12px; margin-top: 36px; border-top: 1px solid #eee; padding-top: 12px; }}
</style></head>
<body>
  <h2>AI 뉴스 다이제스트 - {today}</h2>
  {html_summary}
  <div class="footer">
    이 메일은 매일 오전 9시(KST)에 자동 발송됩니다.<br>
    수신 거부를 원하시면 회신해 주세요.
  </div>
</body>
</html>"""

    outlook = win32com.client.Dispatch('Outlook.Application')
    mail = outlook.CreateItem(0)  # 0 = olMailItem
    mail.To      = RECIPIENT_EMAIL
    mail.Subject = f'[AI 뉴스 다이제스트] {today}'
    mail.HTMLBody = html_body
    mail.Send()

    print(f"  이메일 발송 완료 → {RECIPIENT_EMAIL}")


def main():
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{now}] AI 뉴스 수집 시작")

    articles = fetch_news()
    print(f"  총 {len(articles)}개 기사 수집")

    print("  Gemini로 요약 중...")
    summary = summarize_with_gemini(articles)

    print("  이메일 발송 중...")
    send_email(summary)

    print("  완료")


if __name__ == '__main__':
    main()
