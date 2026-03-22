@echo off
echo Windows 작업 스케줄러에 AI 뉴스 다이제스트 등록 중...

schtasks /create ^
  /tn "AI News Digest" ^
  /tr "C:\Users\140773\Desktop\Cursor\ai_news_digest\run.bat" ^
  /sc weekly ^
  /d MON,TUE,WED,THU,FRI ^
  /st 09:00 ^
  /ru "%USERNAME%" ^
  /f

if %ERRORLEVEL% EQU 0 (
    echo.
    echo 등록 완료! 평일(월~금) 오전 9시에 자동 실행됩니다.
) else (
    echo.
    echo 등록 실패. 관리자 권한으로 다시 실행해 주세요.
)
pause
