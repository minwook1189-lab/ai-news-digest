# AI 뉴스 다이제스트

평일(월~금) 오전 9시(KST), AI 관련 최신 뉴스를 자동으로 수집·요약하여 이메일로 발송하는 자동화 스크립트입니다.

## 주요 기능

- 주요 AI 뉴스 사이트 RSS 피드에서 최신 기사 자동 수집 (최근 48시간, 소스당 최대 3건)
- Groq API(LLaMA 3.3 70B)를 활용한 한국어 요약 및 카테고리 분류
- 커뮤니티 출처 기사에 ⚠️ 신뢰도 경고 자동 표시
- Outlook COM 자동화를 통한 HTML 이메일 발송 (다수 수신자 지원)
- Windows 작업 스케줄러로 평일(월~금) 오전 9시 자동 실행

## 뉴스 출처

| 출처 | 분야 | 신뢰도 |
|------|------|--------|
| MIT Technology Review | 심층 기술 분석 | 높음 |
| Wired AI | 사회·문화적 영향 | 높음 |
| Ars Technica | 기술 전반 | 높음 |
| The Verge AI | 소비자·빅테크 속보 | 높음 |
| DeepMind Blog | Google DeepMind 연구 발표 | 높음 |
| Hugging Face Blog | 오픈소스 모델·툴 릴리즈 | 높음 |
| The Gradient | 학술·연구자 중심 분석 | 높음 |
| TechCrunch AI | 스타트업·펀딩 동향 | 높음 |
| VentureBeat AI | 기업 AI 도입·B2B 동향 | 높음 |
| The Batch (deeplearning.ai) | 주간 AI 하이라이트 (Andrew Ng) | 높음 |
| Import AI | 연구 논문 중심 큐레이션 | 높음 |
| Last Week in AI | 주간 AI 동향 요약 | 높음 |
| Hacker News AI | 커뮤니티 인기글 (100점 이상만) | 주의 ⚠️ |

## 요구 사항

- Python 3.11 이상
- Microsoft Outlook (설치 및 로그인 상태)
- Groq API 키 ([console.groq.com](https://console.groq.com) 에서 무료 발급)

## 설치 방법

**1. 가상환경 생성 및 활성화**
```bash
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\activate

# Windows (cmd)
.venv\Scripts\activate.bat
```

**2. 패키지 설치**
```bash
pip install -r requirements.txt
```

**3. 환경 변수 설정**

`.env.example`을 복사하여 `.env` 파일을 생성하고 값을 입력합니다.
```bash
cp .env.example .env
```

```env
GROQ_API_KEY=your_groq_api_key
SMTP_EMAIL=your_email@example.com
SMTP_PASSWORD=your_password
RECIPIENT_EMAIL=recipient@example.com
```

> `.env` 파일은 절대 GitHub에 업로드하지 마세요. (`.gitignore`에 포함되어 있습니다)

**4. 즉시 실행 테스트**
```bash
python main.py
```

**5. 작업 스케줄러 등록 (평일 오전 9시 자동 실행)**

`setup_task.bat`을 더블클릭하거나 관리자 권한으로 실행합니다.

```
setup_task.bat
```

## 다른 PC에서 시작하는 경우

저장소를 clone한 후 아래 순서로 진행합니다.

```bash
git clone https://github.com/minwook1189-lab/ai-news-digest.git
cd ai-news-digest

# 가상환경 생성 및 패키지 설치
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# .env 파일 생성 (직접 값 입력)
cp .env.example .env
```

## 주의 사항

- 평일(월~금) 오전 9시에 **PC가 켜져 있고 Outlook이 로그인된 상태**여야 합니다.
- `.env` 파일은 절대 GitHub에 업로드하지 마세요. (`.gitignore`에 포함되어 있습니다)
- 여러 수신자에게 보내려면 `RECIPIENT_EMAIL`을 쉼표로 구분합니다.
  ```
  RECIPIENT_EMAIL=user1@example.com, user2@example.com
  ```
- ⚠️ 표시가 붙은 Hacker News 출처는 커뮤니티 게시글로, 정확도를 별도 확인하는 것을 권장합니다.

## 파일 구조

```
ai_news_digest/
├── main.py           # 메인 스크립트
├── run.bat           # 작업 스케줄러용 실행 파일
├── setup_task.bat    # 작업 스케줄러 자동 등록 스크립트
├── requirements.txt  # 패키지 목록
├── .env              # 환경 변수 (GitHub 업로드 금지)
├── .env.example      # 환경 변수 예시
├── .venv/            # 가상환경 (GitHub 업로드 금지)
└── .gitignore        # Git 제외 파일 목록
```
