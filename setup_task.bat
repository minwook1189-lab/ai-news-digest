@echo off
echo Windows 작업 스케줄러에 AI 뉴스 다이제스트 등록 중...

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$action = New-ScheduledTaskAction -Execute 'C:\Users\140773\Desktop\Cursor\ai_news_digest\run.bat';" ^
  "$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At 09:00AM;" ^
  "$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable:$false -ExecutionTimeLimit (New-TimeSpan -Hours 1);" ^
  "Register-ScheduledTask -TaskName 'AI News Digest' -Action $action -Trigger $trigger -Settings $settings -RunLevel Limited -Force | Out-Null;" ^
  "Write-Host '등록 완료'"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo 등록 완료! 평일 오전 9시 + Outlook 실행 중일 때만 발송됩니다.
    echo 누락된 실행은 복구하지 않습니다.
) else (
    echo.
    echo 등록 실패. 관리자 권한으로 다시 실행해 주세요.
)
pause
