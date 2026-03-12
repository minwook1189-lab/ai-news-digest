# AI 뉴스 다이제스트

매일 오전 9시(KST), AI 관련 최신 뉴스를 자동으로 수집·요약하여 이메일로 발송하는 자동화 스크립트입니다.

## 주요 기능

- 주요 AI 뉴스 사이트 RSS 피드에서 최신 기사 자동 수집
- Google Gemini API를 활용한 한국어 요약 및 카테고리 분류
- Outlook COM 자동화를 통한 HTML 이메일 발송
- Windows 작업 스케줄러로 매일 오전 9시 자동 실행

## 뉴스 출처

| 출처 | 분야 |
|------|------|
| TechCrunch AI | 스타트업·산업 동향 |
| VentureBeat AI | 기업·기술 뉴스 |
| MIT Technology Review | 심층 기술 분석 |
| The Verge AI | 소비자·빅테크 |
| Wired AI | 사회·문화적 영향 |
| Ars Technica | 기술 전반 |
| Google DeepMind Blog | 연구 발표 |
| OpenAI Blog | OpenAI 공식 소식 |

## 요구 사항

- Python 3.11 이상
- Microsoft Outlook (설치 및 로그인 상태)
- Google Gemini API 키 ([aistudio.google.com](https://aistudio.google.com) 에서 발급)

## 설치 방법

**1. 패키지 설치**
```bash
python -m pip install -r requirements.txt
```

**2. 환경 변수 설정**

`.env.example`을 복사하여 `.env` 파일을 생성하고 값을 입력합니다.
```bash
cp .env.example .env
```

```env
GEMINI_API_KEY=your_gemini_api_key
SMTP_EMAIL=your_email@example.com
SMTP_PASSWORD=your_password
RECIPIENT_EMAIL=recipient@example.com
```

**3. 즉시 실행 테스트**
```bash
python main.py
```

**4. 작업 스케줄러 등록 (매일 오전 9시 자동 실행)**

PowerShell을 관리자 권한으로 실행 후:
```powershell
$action = New-ScheduledTaskAction -Execute 'C:\경로\ai_news_digest\run.bat'
$trigger = New-ScheduledTaskTrigger -Daily -At '09:00AM'
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable
Register-ScheduledTask -TaskName 'AI News Digest' -Action $action -Trigger $trigger -Settings $settings -Force
```

## 주의 사항

- 매일 오전 9시에 **PC가 켜져 있고 Outlook이 로그인된 상태**여야 합니다.
- `.env` 파일은 절대 GitHub에 업로드하지 마세요. (`.gitignore`에 포함되어 있습니다)
- 여러 수신자에게 보내려면 `RECIPIENT_EMAIL`을 세미콜론으로 구분합니다.
  ```
  RECIPIENT_EMAIL=user1@example.com; user2@example.com
  ```

## 파일 구조

```
ai_news_digest/
├── main.py          # 메인 스크립트
├── run.bat          # 작업 스케줄러용 실행 파일
├── requirements.txt # 패키지 목록
├── .env             # 환경 변수 (GitHub 업로드 금지)
├── .env.example     # 환경 변수 예시
└── logs/            # 실행 로그
```
