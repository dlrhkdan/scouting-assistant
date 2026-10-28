# Claude Code evidence (6 excerpts)

Excerpts are copied from my Claude Code sessions on 2026-10-28. Claude Code replied in Korean. "…" marks parts I left out.

## 1. Claude Code found a bug in report saving
After saving a report, Claude Code checked scout.py and found that reports with different filters could overwrite each other.

> 다만 scout.py 코드를 확인해 보니 문제가 하나 있습니다. 파일 이름에 필터 조건이 들어가지 않습니다. 이름은 날짜_list_리그 또는 날짜_rank_지표_리그 형식이고, 같은 이름이 있으면 경고 없이 덮어씁니다(scout.py:314-320).
>
> 고치는 방법 제안 (save_report 한 곳만 수정):
> 1. 파일 이름에 주요 필터를 붙입니다. 예: 2026-10-28_list_all_sideL_age23.md
> 2. 그래도 같은 이름이 있으면 덮어쓰지 않고 _2, _3을 붙입니다.

## 2. I approved the fix and asked it to prove it worked
I asked: "Apply both, then save twice with the same filters and once with different filters, and show me the file names."

> | list --side L --max-age 23 --save (1회차) | 2026-10-28_list_all_sideL_age23.md |
> | list --side L --max-age 23 --save (2회차, 같은 조건) | 2026-10-28_list_all_sideL_age23_2.md |
> | list --side R --save (다른 조건) | 2026-10-28_list_all_sideR.md |
> | rank --by passes --side L --max-age 23 --specialists --top 5 --save | 2026-10-28_rank_passes_all_sideL_age23_spec_top5.md |

## 3. Claude Code refused to record a check it had not done
I asked it to add "per-90 values match my own CSV calculation" to the verification table. I had done that calculation in a separate chat, not in Claude Code.

> "CSV로 직접 계산한 90분당 값과 5명 모두 일치"하는 검증은 이 대화에서 한 적이 없습니다. … (a) 지금 실제로 검증하기 … (b) 표에서 빼기 …

I chose (a), so it wrote tests/check_per90.py.

## 4. Independent check script: 5/5 match
tests/check_per90.py reads the CSV directly (without importing scout.py) and compares per-90 values.

> | K1 | Choi Woo-Jin @ Jeonbuk Hyundai Motors FC | 1561 | 582 | 33.56 | 33.56 | OK |
> | K1 | Kim Jae-Hyun @ FC Anyang | 672 | 185 | 24.78 | 24.78 | OK |
> | K2 | Bae Seo-Joon @ Seoul E-Land FC | 604 | 254 | 37.85 | 37.85 | OK |
> | K2 | Lee Jun-Jae @ Suwon Samsung Bluewings | 613 | 178 | 26.13 | 26.13 | OK |
> | K2 | Lee Sang-Min @ Suwon Samsung Bluewings | 1030 | 373 | 32.59 | 32.59 | OK |
>
> 5/5 match - PASS

These values also match my separate hand calculation (33.56, 24.78, 37.85, 26.13, 32.59).

## 5. Rankings change when the scouting question changes
From docs/verification.md (cases A and B):

> A. 나이 상한 23 → 24: 24세로 바꾸면 K1에 Kim Ryun-Seong (30.52), K2에 Son Ho-Jun (26.96)·Kim Ju-Sung (23.93)·Lee Taek-Geun (22.79)이 새로 들어옴 — 통과
>
> B. K2 오른쪽 전문 풀백: tackles 1위 Noh Seung-Ik @ Paju Frontier, 2.58 / pass_acc 8위(마지막) Noh Seung-Ik, 62.2% (239/384) — 통과

## 6. Claude Code pointed out a data limitation
> 데이터 주의점: Kim Ju-Sung과 Son Ho-Jun은 notes에 듀얼 %가 전체인지 지상인지 명시되지 않았다고 되어 있습니다. 그런데 값이 duels_won_pct 칸에 들어 있어서 scout.py는 "전체 듀얼"로 처리합니다. … FotMob에서 확인해 보시는 게 좋겠습니다.

I decided to define duels_won_pct as FotMob's "볼 경합 성공 %" and list this as a known limitation.
