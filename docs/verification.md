# scout.py 검증 기록

- 검증일: 2026-10-28
- 데이터: `data/players.csv` (FotMob, as of 2026-10-27)
- 실제 결과 칸에는 실행 화면에 나온 값만 옮겼습니다.

| 사례 | 실행한 명령 | 기대 결과 | 실제 결과 | 통과 |
|---|---|---|---|---|
| A. 나이 상한 23 → 24 | `python3 scout.py rank --by passes --side L --specialists --max-age 23`<br>`python3 scout.py rank --by passes --side L --specialists --max-age 24` | 24세로 바꾸면 K1에 Kim Ryun-Seong, K2에 Son Ho-Jun·Kim Ju-Sung·Lee Taek-Geun이 새로 들어옴 | 23세: K1 Choi Woo-Jin, Kim Jae-Hyun / K2 Bae Seo-Joon, Lee Sang-Min, Lee Jun-Jae<br>24세: K1 Choi Woo-Jin, **Kim Ryun-Seong @ Jeju SK (30.52)**, Kim Jae-Hyun / K2 Bae Seo-Joon, Lee Sang-Min, **Son Ho-Jun @ Gyeongnam FC (26.96)**, Lee Jun-Jae, **Kim Ju-Sung @ Chungnam Asan FC (23.93)**, **Lee Taek-Geun @ Paju Frontier (22.79)** | 통과 |
| B. K2 오른쪽 전문 풀백, 지표 2개 | `python3 scout.py rank --by tackles --side R --league K2 --specialists`<br>`python3 scout.py rank --by pass_acc --side R --league K2 --specialists` | Noh Seung-Ik이 tackles 1위, pass_acc 꼴찌 | tackles: 1위 `Noh Seung-Ik @ Paju Frontier`, 2.58 (8명 중)<br>pass_acc: 8위 `Noh Seung-Ik @ Paju Frontier`, 62.2% (239/384) (8명 중 마지막) | 통과 |
| C. 90분당 패스 성공 값 독립 계산 | `python3 tests/check_per90.py`<br>(내부에서 `python3 scout.py rank --by passes --side L --max-age 23 --specialists` 실행) | CSV에서 직접 계산한 값(`successful_passes × 90 / league_minutes`)과 scout.py 출력이 23세 이하 왼쪽 전문 풀백(600분 이상) 전원 일치 | 아래 표 참고. `5/5 match - PASS`, exit=0 | 통과 |

## C 상세: tests/check_per90.py 출력

`scout.py`를 import하지 않고 CSV를 직접 읽어 같은 조건으로 거른 뒤 계산한 값입니다.

| Lg | Player | League min | Successful passes (CSV) | CSV per90 | scout.py | Match |
|---|---|---|---|---|---|---|
| K1 | Choi Woo-Jin @ Jeonbuk Hyundai Motors FC | 1561 | 582 | 33.56 | 33.56 | OK |
| K1 | Kim Jae-Hyun @ FC Anyang | 672 | 185 | 24.78 | 24.78 | OK |
| K2 | Bae Seo-Joon @ Seoul E-Land FC | 604 | 254 | 37.85 | 37.85 | OK |
| K2 | Lee Jun-Jae @ Suwon Samsung Bluewings | 613 | 178 | 26.13 | 26.13 | OK |
| K2 | Lee Sang-Min @ Suwon Samsung Bluewings | 1030 | 373 | 32.59 | 32.59 | OK |

검증 범위: 전문 선수만 포함했습니다. 전환 선수(Kim Ho-Jin, Yu Sun 등)가 들어가는 기본 순위는 이 스크립트로 검증하지 않았습니다.
