# Korean-market UI reference

Apply these rules for Korean-language or Korean-market products. They override generic Western defaults.

## Market color convention

- Rise (up, gain) is red. Fall (down, loss) is blue. This is the opposite of the US. Flat (unchanged) is gray.
- Do not use green for gains or red for losses in KRW stock, crypto, or fund screens: users read it as the reverse.
- Pair color with a sign or arrow (`▲ 1.2%`, `▼ 0.8%`) so meaning does not rely on color alone.
- Red/blue are not error/info here. Keep an error state (form validation) visually distinct from "rise" red.

## Currency

- Format KRW as `₩1,234,000` or `1,234,000원`. Use thousands separators and no decimals; the won has no minor unit.
- Pick one form per product and keep it consistent. Use `원` in running Korean text and `₩` in dense tables.

## Large-number units (만 / 억 / 조)

- 만 = 10^4, 억 = 10^8, 조 = 10^12. Examples: `3,400만`, `1.2억`, `12조 3,400억`.
- Use units for summaries, cards, charts axes, and market caps where scanning matters.
- Use full digits for prices, balances, order and payment amounts, and anything the user must verify or copy.
- Show at most two unit levels (`12조 3,400억`, not `12조 3,400억 5,000만`). Keep the same unit within one column.

## Fonts

- Stack: `"Pretendard", "SUIT", "Noto Sans KR", -apple-system, "Apple SD Gothic Neo", "Malgun Gothic", system-ui, sans-serif`.
- Pretendard and SUIT pair well with Latin text and digits. Noto Sans KR is the widely available fallback.
- Load only the weights in use (400, 500, 700) and use `font-display: swap`; Korean font files are large.

## Line breaking and spacing

- Use `word-break: keep-all` so Korean breaks at spaces, not mid-word.
- Add `overflow-wrap: anywhere` so long tokens (URLs, order numbers, English words) cannot overflow the container.
- Body line-height is about 1.5-1.7 for Hangul. Headings can go down to 1.3. Letter-spacing stays at 0 or slightly negative (about -0.01em) for large headings.
- Keep body text at 14-16px minimum; Hangul strokes get dense below that.

## Dates and times

- Date: `2026. 11. 20.` (period after each part, including the day) or `2026년 11월 20일`.
- Short form with weekday: `11월 20일 (금)`.
- Time: 24-hour `14:05`. Use `오후 2:05` only in conversational contexts.
- Do not use US `MM/DD/YYYY`; it is ambiguous for Korean users.

## Numerals in tables

- Use tabular figures for prices and quantities so columns align: `font-variant-numeric: tabular-nums;`.
- Right-align numeric columns and keep the unit (`원`, `%`, `주`) in the header or in a muted suffix.
