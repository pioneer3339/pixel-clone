# Pixel Clone helpers

SKILL.md의 루프에서 쓰는 evaluate / MAE 조각. 페이지마다 새로 짜지 않는다.

뷰포트 숫자는 프로젝트 합의값으로 바꾼다. 아래는 mobile 390 × 844 / desktop 1440 × 900.

측정 전 반드시 `innerWidth`가 목표 폭인지 확인한다.

원본 브레이크포인트 찾기:

```js
(() => {
  const bps = new Set();
  for (const sheet of document.styleSheets) {
    let rules; try { rules = sheet.cssRules; } catch { continue; }
    for (const rule of rules) {
      if (rule.conditionText) bps.add(rule.conditionText);
    }
  }
  return JSON.stringify({ innerWidth, innerHeight, media: [...bps] });
})()
```

desktop 폭은 잡힌 `min-width` 이상으로 고른다.

## 소음 제거

원본/로컬 양쪽에 넣는다. 셀렉터는 사이트에 맞게 추가.

```js
(() => {
  document.querySelectorAll(
    '.layer.active,.review-write-layer.active'
  ).forEach(e => e.classList.remove('active'));
  document.querySelectorAll(
    '.dim,.layer__bg,#ch-plugin,.ch-plugin,.toast,.float-coupon,.app-down'
  ).forEach(e => { try { e.remove(); } catch (_) {} });
  const s = document.createElement('style');
  s.textContent = [
    '*{animation:none!important;transition:none!important}',
    'iframe{visibility:hidden!important}',
    '.layer,.dim,#ch-plugin{display:none!important}',
  ].join('');
  document.head.appendChild(s);
  document.querySelectorAll('.swiper').forEach(el => {
    const sw = el.swiper;
    if (!sw) return;
    try { sw.autoplay && sw.autoplay.stop(); sw.slideTo(0, 0); } catch (_) {}
  });
  window.scrollTo(0, 0);
  return innerWidth;
})()
```

루프 모드 로컬 히어로: `swiper.slideToLoop(index, 0)`.

## rect + computed

`getBoundingClientRect().y`는 뷰포트 기준. 문서 y는 `+ scrollY`.
`position: fixed` / `sticky`는 scrollY를 더하지 않는다.

```js
(() => {
  const r = (el) => {
    if (!el) return null;
    const b = el.getBoundingClientRect();
    const st = getComputedStyle(el).position;
    const y = (st === 'fixed' || st === 'sticky') ? b.y : b.y + scrollY;
    return [
      Math.round(b.x * 10) / 10,
      Math.round(y * 10) / 10,
      Math.round(b.width * 10) / 10,
      Math.round(b.height * 10) / 10,
    ];
  };
  const cs = (el, props) => el
    ? Object.fromEntries(props.map(p => [p, getComputedStyle(el)[p]]))
    : null;
  const after = (el) => {
    if (!el) return null;
    const s = getComputedStyle(el, '::after');
    return { content: s.content, w: s.width, h: s.height, bg: s.backgroundImage };
  };
  return JSON.stringify({
    url: location.href,
    w: innerWidth,
    h: innerHeight,
    header: r(document.querySelector('header')),
  });
})()
```

## 골격 스캔

셀렉터를 모르면 큰 블록부터.

```js
(() => {
  return JSON.stringify(
    [...document.querySelectorAll('section, main > div, [class*="module"]')]
      .slice(0, 40)
      .map(el => {
        const b = el.getBoundingClientRect();
        return {
          tag: el.tagName,
          cls: String(el.className).slice(0, 60),
          y: Math.round(b.y + scrollY),
          h: Math.round(b.height),
          text: el.innerText.replace(/\s+/g, ' ').trim().slice(0, 80),
        };
      })
  );
})()
```

## 점 → 요소

```js
document.elementsFromPoint(348, 22).map(el => ({
  tag: el.tagName,
  cls: String(el.className).slice(0, 80),
  r: el.getBoundingClientRect(),
}))
```

## 이긴 CSS 규칙

```js
(() => {
  const needle = '.bottom';
  const hits = [];
  for (const sheet of document.styleSheets) {
    let rules; try { rules = sheet.cssRules; } catch { continue; }
    for (const rule of rules) {
      const list = rule.cssRules ? [...rule.cssRules] : [rule];
      for (const r of list) {
        if (r.selectorText && r.selectorText.includes(needle))
          hits.push({ sel: r.selectorText, css: r.cssText.slice(0, 300), media: rule.conditionText });
      }
    }
  }
  return JSON.stringify(hits);
})()
```

## 캡처 MAE

CDP `Page.captureScreenshot` clip은 **그 뷰포트 크기**로 한다.
mobile `{ x:0, y:0, width:390, height:844, scale:1 }`
desktop `{ x:0, y:0, width:1440, height:900, scale:1 }`

```bash
python scripts/mae.py origin.png local.png --width 390
python scripts/mae.py origin.png local.png --width 1440
python scripts/mae.py origin.png local.png --width 390 --crop 0,540,390,844
```

Pillow 직접:

```python
from PIL import Image, ImageChops, ImageStat
W = 390  # or 1440
A = Image.open(origin).convert('RGB')
B = Image.open(local).convert('RGB')
h = min(A.height, B.height)
w = min(A.width, B.width, W)
d = ImageChops.difference(A.crop((0, 0, w, h)), B.crop((0, 0, w, h)))
mae = sum(ImageStat.Stat(d).mean) / 3
hist = d.convert('L').histogram()
diff_ratio = sum(hist[16:]) / (w * h) * 100
```
