# Pixel Clone — 팀 루프

메인이 페이지 큐를 돌린다. 워커는 한 장만 재고 고친다.
원샷으로 사이트 전체를 LOCK 했다고 말하지 않는다.

Cursor `Task` 서브에이전트를 쓸 때 이 문서를 워커 프롬프트에 붙인다.

## 큐

메인이 유지하는 표:

```
id | origin_url | local_url | files | status | retries
login | https://…/login | http://127.0.0.1:PORT/#/login | src/pages/Login.tsx, src/css/login.css | queued|running|lock|fail | 0-2
```

status 의미:

- `queued` — 아직
- `running` — 워커 1명 배정
- `lock` — 주요 블록 3px 안. 재오픈 금지
- `fail` — 2회 후에도 좌표 불일치. 메인 보고용. 자동 재할당 금지

`CONTEXT.md`에 잠금이 있으면 그대로 `lock`으로 시작한다.

## 한 턴의 순서

```
메인: 큐에서 queued 1장(파일 안 겹치면 N장) 꺼냄
  → 측정 워커 병렬 가능 (파일 쓰기 없음)
  → 구현은 파일 주인이 겹치지 않을 때만 병렬
  → 워커 리턴 표 검사
  → LOCK / 같은 페이지 retry / fail
  → 다음 queued
메인: 잠긴 수 / 남은 수 / fail 이유를 사용자에게 보고하고 멈춤
사용자가 이어 하라고 하면 fail·미잠금만 다시
```

사용자가 한 마디로 “전부 끝내” 해도 메인은 **한 바퀴 후 보고**한다. 무한 루프 금지.

## 워커 프롬프트 (이대로 넣기)

```
pixel-clone 워커. 페이지 하나만 한다. 다른 경로는 읽기만.

ORIGIN: {origin_url}
LOCAL: {local_url}
VIEWPORT: {width}x{height} dsf1 mobile:true
ALLOWED FILES: {file list or "none — measure only"}
LOCKED PAGES: {ids}  — 이 페이지 CSS/마크업을 건드리지 말 것
PORT: {local port}

할 일:
1. 원본 이동 → 뷰포트 → 팝업/채널톡/오토플레이 제거 → innerWidth 확인
2. 골격 스캔 후 주요 블록 [x,y,w,h] + font/color/padding
3. ALLOWED FILES가 있으면 그 파일만 수정. 숫자는 반올림 금지
4. 로컬을 같은 셀렉터로 재측정
5. 아래 표만 리턴. 완료 문장으로 퉁치지 말 것

금지: 파이썬 슬라이스 치환, 잠긴 페이지 수정, GIF MAE 때문에 좌표 재작성,
     높이만 보고 LOCK, ALLOWED 밖 파일 수정, 원본 텍스트 교정

리턴 형식:
PAGE: {id}
INNER: {n}
SOURCE_FN_COUNT: before={n} after={n}
FILES: {touched}
STATUS: LOCK | RETRY | MARKUP_FIRST | FAIL
BLOCKS:
selector | origin [x,y,w,h] | local [x,y,w,h] | d(x,y,w,h)
...
RETRY_LINES: 3px 넘는 셀렉터만
NOTES: 섹션 누락 / after 이미지 / 클래스 충돌 만
```

`ALLOWED FILES: none`이면 측정만. 메인이 숫자를 보고 직접 반영한다. 공용 `main.tsx`일 때 기본값.

## 메인 판정

| 워커 STATUS | 표 | 메인 |
|---|---|---|
| LOCK | 주요 블록 전부 3px 안 | 잠근다. MAE 보지 않음 |
| RETRY | 3px 넘는 줄 있음, 재시도 < 2 | 같은 페이지 재할당. RETRY_LINES만 고치라고 적는다 |
| MARKUP_FIRST | 섹션 수 불일치 | CSS 워커를 보내지 않는다. 마크업 워커 1명 |
| FAIL | 2회 소진 또는 파일 삭제 사고 | 큐에서 빼고 사용자에게 셀렉터 목록 |

픽셀 MAE는 메인이 **잠긴 뒤**, GIF·타이머를 양쪽 정지하고 찍을 때만. 점수가 나빠도 잠금을 풀지 않는다. 미디어 노이즈로 적는다.

## 병렬 가능 여부

```
측정만        → 병렬 OK
구현, 파일 교집합 없음 → 병렬 OK
구현, 공용 TSX/CSS   → 반드시 1명
best-of-n 워크트리    → 쓰지 말 것. 공용 CSS 머지가 좌표를 다시 섞는다
```

## 사고 후 점검 (메인)

워커가 TSX를 만졌으면 메인이 확인한다.

- `function Source` (또는 페이지 export) 개수가 줄지 않았는가
- 잠긴 페이지 셀렉터 CSS가 diff에 들어갔는가 → 되돌린다
- 로컬 포트가 합의 포트인가

## 보고 템플릿 (사용자에게)

```
잠김: login, legal, service
재시도 대기: cart (btn y-3.5)
실패: 없음
이번 바퀴에서 안 함: home, product (잠금 유지 / GIF 페이지는 좌표만)
원샷 완료 아님. 이어 하려면 남은 id를 말하면 됨.
```
