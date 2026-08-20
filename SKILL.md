---
name: pixel-clone
description: Clones a live website into a local app by measuring the original DOM (getBoundingClientRect + getComputedStyle) at a fixed mobile viewport and copying those numbers into CSS/markup. Orchestrates a page-by-page parent/worker loop (team mode) without claiming one-shot site completion. Use when the user asks for a 1:1 clone, pixel replica, 원본 복제, 픽셀 복제, 화면 똑같이, 팀모드, 루프 엔지니어링, 페이지별 에이전트, METHOD.md 실측 루프, or to stop guessing CSS from screenshots.
---

# Pixel Clone — 원본 DOM 실측 복제

스크린샷을 보고 CSS를 감으로 맞추지 않는다.
원본을 자로 잰 뒤 **그 숫자를 그대로** 로컬에 박고, 같은 자로 다시 잰다.

온브릭스에서 검증한 루프. 사이트는 달라도 순서는 같다.
사이트별 상수·완료 페이지는 그 프로젝트의 `CONTEXT.md` / `METHOD.md`를 읽는다. 이 스킬은 **방법**만 강제한다.

법적 전제: 개인 학습·비공개. 원본 이미지·폰트·상표를 외부 배포하지 않는다. 결제/로그인은 데모만.

## 한 줄

```
원본 뷰포트 고정 → 팝업/애니메이션 제거 → rect+computed 추출
→ 숫자 그대로 CSS/마크업/JSON → 로컬 같은 스크립트 재측정
→ 틀린 숫자만 고침 → 픽셀 diff는 확인용
```

근거는 항상 evaluate 숫자다. 스크린샷은 확인용이다.

## 시작 전에 고정할 것

사용자와 한 번만 정한다. 안 정하면 모든 좌표가 가짜다.

| 항목 | 기본 (온브릭스) | 다른 사이트 |
|---|---|---|
| 뷰포트 | 390 × 844, dsf 1, `mobile: true` | 원본 모바일 CSS가 켜지는 폭 |
| 로컬 포트 | 프로젝트 전용 포트. 다른 클론과 공유 금지 | 새 포트 |
| 라우팅 | 원본 경로 ↔ 로컬 hash/path 표 | 페이지마다 URL 쌍 |

CDP:

```js
Emulation.setDeviceMetricsOverride
{ width: 390, height: 844, deviceScaleFactor: 1, mobile: true }
```

창만 좁히면 데스크톱 CSS가 남는다. 측정 전 `innerWidth`가 목표 폭인지 evaluate로 확인한다.
페이지 이동 후 device metrics가 풀린다. **이동할 때마다 다시 건다.**

헬퍼 코드·MAE 스크립트: [helpers.md](helpers.md)
페이지 여러 장을 팀으로 돌릴 때: [team-loop.md](team-loop.md)

## 한 페이지 = 한 바퀴

하위 워커는 페이지를 한 장만 한다. 메인이 여러 장을 순번에 올리는 것과 다르다.
워커가 홈+상세+카트를 한 호출에서 끝내지 않는다.

### A. 원본

1. 원본 URL로 이동, 뷰포트 재적용
2. 팝업·채널톡·앱 띠·오토플레이 제거. 히어로 슬라이드 인덱스 고정
3. 골격 스캔 → 섹션 목록 (클래스, 문서 y, 높이, 텍스트 앞 80자)
4. 섹션별 `[x,y,w,h]` + font/color/padding/margin/border/radius/`::after`
5. 화면에 보이는 텍스트 그대로 (원본 띄어쓰기 버그도 복제)
6. 이미지 URL은 `currentSrc` / `background-image`. 로컬 `public/assets/`에 저장. 런타임 CDN 금지

### B. 로컬 반영

1. 섹션 수가 다르면 **CSS 금지, 마크업 먼저**
2. 클래스명은 원본에 가깝게. 전역 짧은 클래스(`.cart`, `.search`, `.bottom`)는 prefix
3. 숫자 반올림 금지. `46.3px`, `font-weight: 800` 그대로
4. 공통 카드 컴포넌트에 서로 다른 모듈을 억지로  squish 하지 않는다
5. HMR이 의심되면 서버 재시작 + `?t=` 하드 리로드

### C. 로컬 재측정

원본과 **같은 셀렉터, 같은 헬퍼**. 표로 한 줄씩.

```
요소     원본 [x,y,w,h]      로컬 [x,y,w,h]     판정
btn-tel  [220,83.5,150,46]  [220,80,150,46]    y-3.5 → 그 요소 padding만
```

차이 3px 이상이면 **그 요소의 padding/margin/font만** 고친다. 옆 섹션을 같이 건드리지 않는다.

### D. 픽셀 확인

동일 scrollY, 동일 폭 캡처 후 `scripts/mae.py` (또는 [helpers.md](helpers.md)의 Pillow 조각).

- 좌표 틀림 → 아직 C
- 좌표 맞는데 MAE 높음 → 폰트/이미지/GIF/아이콘. 레이아웃 회귀가 아니다
- 위 1000px만 좋음 → 아래 모듈만 다시 잰다

### E. 다음 페이지

구조 + 주요 블록 좌표가 맞으면 다음으로 간다.
픽셀 0은 목표가 아니다.

## 금지

- 스크린샷 옆에 두고 “헤더가 조금 크다”로 CSS 때리기
- “이 카드는 대충 170” 반올림
- 높이만 맞고 완료
- 파이썬/`index()` 슬라이스로 큰 TSX 치환 (사이 함수가 삭제됨). 치환 전후 `function` 개수 확인
- 끝난 페이지 좌표를 처음부터 다시 짜기
- GIF·실시간 상품 때문에 MAE가 높다고 모듈 y를 다시 짜기
- 원본 텍스트 교정 (오탈자·띄어쓰기도 복제 대상)
- 이모지로 아이콘 때우기 (레이아웃은 맞아도 픽셀이 틀림)

## 디버깅 (숫자 이상할 때)

1. `innerWidth`가 목표 폭인가
2. 팝업/채널톡을 껐는가 (안 끄면 헤더 y가 밀림)
3. `position:fixed`에 `scrollY`를 더하지 않았는가
4. 로컬 섹션이 빠졌는가 → 빠졌으면 CSS 금지
5. 전역 클래스 충돌인가
6. 모바일 규칙이 `@media (min-width: …)` 안에만 있는가
7. `:has()` 예외를 한 줄만 고치고 다른 `!important`를 남겼는가
8. HMR인가 → 리로드
9. 에셋 용량 0인가 (curl 실패)
10. `::before`/`::after` 이미지를 빠뜨렸는가
11. MAE가 GIF/실시간 상품 노이즈인가

점이 어긋져 보이면 `document.elementsFromPoint(x, y)`로 역추적한다.
computed가 안 바뀌면 스타일시트 `cssRules`를 순회해서 **이긴 규칙**을 찾는다.

## 픽셀 0을 포기하는 지점

다음이면 레이아웃이 맞아도 MAE가 높다. 좌표가 맞으면 다음 페이지로 간다.

- 히어로/배너 GIF (같은 파일이어도 캡처 시각이 다름)
- 원본 상품·리뷰수 실시간 변경
- 웹폰트 OS 힌팅
- 에디터 본문 사진 수천 px
- 채널톡을 비워 둔 것과 제거한 것의 하단 여백

MAE를 다시 찍을 때는 **양쪽 GIF·에디터·타이머를 정지한 뒤**에만. 좌표부터 다시 짜지 않는다.

## 구현 습관

- 반응형으로 맞추지 않는다. 목표 폭 전용 절대값
- 헤더 종류가 페이지마다 다르면 본문 y가 전부 밀린다. 원본 헤더 높이를 먼저 잰다
- 하단 내비는 원본이 보여주는 페이지에만 켠다. 숨김 셀렉터가 여러 줄이면 전부 고친다
- 가격 문자열은 원본 그대로. 로컬에서 다시 `toLocaleString` 하면 띄어쓰기·원이 갈린다
- 레이어(검색, 옵션 시트)는 **닫힌 DOM이 아니라 연 상태**로 잰다

## 팀 루프 (메인이 돌림)

사용자가 “전체 돌려”, “팀모드”, “루프로 완성”이면 이 섹션 + [team-loop.md](team-loop.md).
**사이트 원샷 완성을 약속하지 않는다.** 한 바퀴는 “잠긴 페이지가 늘고, 실패 페이지만 남는다”이다.

### 메인만 한다

1. `CONTEXT.md`가 있으면 페이지 표(원본 URL ↔ 로컬 경로, 잠금 여부)를 읽는다. 없으면 원본 내비로 목록을 만든다.
2. 잠긴 페이지는 큐에 넣지 않는다.
3. 워커에게 넘길 때 **페이지 하나, 원본 URL 하나, 로컬 URL 하나, 만져도 되는 파일 목록**만 준다.
4. 워커 리턴은 좌표 표다. “완료했습니다” 문장은 통과가 아니다.
5. 표에서 3px 넘는 줄만 재할당. 최대 2회. 그다음에도 좌표가 안 맞으면 메인에 남기고 사용자에게 보고.
6. 좌표가 맞으면 그 페이지를 잠근다. 다시 열지 않는다.
7. GIF/실시간 상품 MAE는 재할당 이유가 아니다.

### 파일 주인이 겹치면 병렬 금지

공용 `main.tsx` / `source-modules.css`면 코드 수정 워커는 **한 번에 1명**.
측정(원본 evaluate만, 파일 수정 없음)은 병렬 가능. 반영은 메인이 직렬로 한다.

페이지 파일이 쪼개져 있고 목록이 안 겹칠 때만 구현 워커를 병렬로 켠다.

### 워커에게 금지시키는 것

- 다른 페이지 파일·셀렉터 수정
- 파이썬 슬라이스로 큰 TSX 치환
- 잠긴 페이지 좌표 재작성
- MAE만 보고 모듈 y를 다시 짜기
- 높이만 맞고 `STATUS: LOCK`

워커 프롬프트 템플릿·리턴 표 형식은 [team-loop.md](team-loop.md).
