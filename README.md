# pixel-clone

원본 사이트를 스크린샷 감이 아니라 **DOM 좌표·computed style을 자로 재서** 로컬에 옮기는 Cursor Agent Skill.

라이브 커머스처럼 배너·상품이 매일 바뀌면 페이지를 잠그고 넘어간다.
화면이 고정된 사이트면 팀 루프로 한 번에 끝내는 쪽이 맞다.

## 설치 (동료)

이 폴더를 Cursor 스킬 위치에 둔다.

```bat
git clone https://github.com/pioneer3339/pixel-clone.git "%USERPROFILE%\.cursor\skills\pixel-clone"
```

macOS / Linux:

```bash
git clone https://github.com/pioneer3339/pixel-clone.git ~/.cursor/skills/pixel-clone
```

Cursor를 다시 열거나 Agent 세션을 새로 시작한다.
「원본이랑 똑같이」, 「픽셀 복제」, 「팀모드로 전체 돌려」라고 하면 이 스킬을 탄다.

## 파일

| 파일 | 내용 |
|---|---|
| `SKILL.md` | 실측 루프, 금지 사항, 팀 루프 요약 |
| `helpers.md` | 브라우저 evaluate / MAE 코드 |
| `team-loop.md` | 메인·워커 역할, 워커 프롬프트, 잠금 규칙 |
| `scripts/mae.py` | 두 장 스크린샷 RGB MAE |

## 한 줄

원본 뷰포트 고정 → 팝업 제거 → `getBoundingClientRect` + `getComputedStyle` → 그 숫자를 CSS/마크업에 박기 → 로컬에서 같은 자로 재기 → 틀린 숫자만 고치기.

근거는 숫자다. 스크린샷은 확인용이다.

## 팀 루프

메인이 페이지 큐를 돌리고, 워커는 **한 페이지**만 재서 좌표 표를 돌려준다.
공용 `main.tsx`면 코드 수정 워커는 한 번에 한 명. 측정만 병렬.
좌표가 맞으면 잠근다. GIF MAE로 잠금을 풀지 않는다.
사이트 원샷 완성을 약속하지 않는다. 한 바퀴 후 잠긴 것/남은 것을 보고한다.

## 주의

개인 학습·내부용. 원본 이미지·폰트·상표를 이 스킬과 함께 배포하지 말 것.
결제/로그인 실연동은 범위 밖이다.
