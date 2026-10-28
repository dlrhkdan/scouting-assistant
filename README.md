# Scouting Assistant: K리그1·2 24세 이하 풀백

Claude Code 안에서 쓰는 작은 개인용 스카우팅 도우미입니다. CSV 파일 하나와 파이썬 스크립트 하나로 이루어져 있고, 웹 앱이나 외부 API는 없습니다.

## 1. 목적과 사용자

사용자는 저 자신입니다. 실제 구단이 어떤 기준으로 젊은 풀백을 평가하는지 궁금했고, 덜 알려진 K리그1(K1)·K리그2(K2)의 24세 이하 선수에 집중했습니다.

지표 하나로 순위 매기기, 선수 비교, 날짜별 관찰 메모, 리포트 저장을 할 수 있습니다. Claude Code는 한국어로 답합니다. 모든 계산은 `scout.py`가 하므로 Claude Code가 숫자를 추정하지 않습니다. 규칙은 `CLAUDE.md`에 있습니다.

## 2. 사용 방법

**설치가 필요 없습니다.** `scout.py`는 파이썬 표준 라이브러리만 사용하며, 시스템의 `python3`로 실행합니다.

### 슬래시 명령어 (Claude Code 안에서)

| 명령어 | 하는 일 |
|---|---|
| `/compare <Name@Team> ...` | `scout.py compare`를 실행하고 장단점을 요약합니다. 경고(리그 다름, 표본 부족, 듀얼 % 종류)를 모두 다시 보여줍니다. |
| `/report <조건>` | `list`와 `rank`를 `--save`로 실행하고, 요약을 `reports/<날짜>_report_<slug>.md`에 씁니다. |
| `/note <Name@Team> <내용>` | `scout.py note`로 `watchlist/`에 날짜가 붙은 메모를 추가합니다. |

### scout.py 직접 실행

```
python3 scout.py --help
python3 scout.py metrics
```

하위 명령: `list`, `rank`, `compare`, `show`, `note`, `metrics`.
주요 필터: `--league K1|K2|all`, `--min-minutes 600`, `--include-small`, `--specialists`, `--side L|R`, `--max-age N`, `--save`.

예시:

```
# K2 오른쪽 전문 풀백, 90분당 태클 순위
python3 scout.py rank --by tackles --side R --league K2 --specialists

# 23세 이하 왼쪽 전문 풀백, 90분당 패스 성공 상위 5명, reports/에 저장
python3 scout.py rank --by passes --side L --max-age 23 --specialists --top 5 --save

# 선수 한 명의 전체 프로필 (데이터 메모와 관찰 메모 포함)
python3 scout.py show "Choi Woo-Jin@Jeonbuk Hyundai Motors FC"
```

선수는 `Name@Team` 형식으로 지정합니다. 같은 이름이 다른 클럽에 있을 수 있기 때문입니다.

기본 동작: K1과 K2는 따로 순위를 매깁니다(`--combine`으로 합치면 리그 칸이 남습니다). 리그 출전 600분 미만이거나 출전 시간이 비어 있는 선수는 `small sample`로 표시되고, `--include-small`을 쓰지 않으면 순위에서 빠집니다. 전환 선수(예: `CB/LB`)는 포함되며 따로 표시됩니다. `--specialists`는 첫 포지션이 LB, RB, LWB, RWB인 선수만 남깁니다. 종합 점수는 없습니다.

## 3. 데이터

- 파일: `data/players.csv`
- **59명** (K1 20명, K2 39명), FotMob 공개 선수 페이지 기준.
- **2026-10-27** 기준으로 팀별로 모았고, 수집은 별도의 Claude 채팅의 도움을 받았습니다. 모든 행에 `as_of_date` = 2026-10-27과 FotMob 선수 페이지 링크(`source`)가 있습니다.
- **선정 기준:** 24세 이하이고, 팀 페이지에서 풀백이나 윙백으로 표시된 선수.
- 누적 기록은 시즌 합계이고, 90분당 값은 `scout.py`가 `league_minutes`로 계산합니다.
- `duels_won_pct`는 FotMob의 "볼 경합 성공 %" 값입니다. `ground_duels_won_pct`와는 서로 비교하지 않습니다.
- `rating_*` 칸은 제 평가를 위해 일부러 비워 두었습니다.
- `notes`에는 확인할 내용(임대, 계약 만료, "to verify")이 있으며, 확정된 사실로 다루지 않습니다.

## 4. 작업 과정

1. **데이터 수집:** FotMob에서 팀별로 `players.csv`를 만들었습니다.
2. **CLAUDE.md 규칙 작성:** 계산은 scout.py만, K1/K2 항상 표시, 표본 부족 표시, `Name@Team` 식별, 표준 라이브러리만 사용.
3. **scout.py와 슬래시 명령어:** `/compare`, `/report`, `/note`.
4. **테스트:** note와 report 명령을 실행해 봤습니다.
5. **버그 수정:** 저장한 리포트끼리 덮어쓸 수 있었습니다. 이제 파일 이름에 필터가 들어가고(예: `_sideL_age23`), 같은 이름이 있으면 `_2`, `_3`이 붙습니다.
6. **검증 스크립트:** `tests/check_per90.py`와 `docs/verification.md`. 이제 `CLAUDE.md`에 `scout.py`를 바꿀 때마다 이 스크립트를 실행하라고 적혀 있습니다.

## 5. Claude Code 사용 증거

전체 발췌: [docs/evidence.md](docs/evidence.md)

1. **버그 발견:** 리포트를 저장한 뒤, 필터가 다른 리포트끼리 덮어쓸 수 있다는 문제를 찾았습니다.
2. **수정 증명:** 같은 조건과 다른 조건으로 저장해 보고 새 파일 이름을 보여줬습니다.
3. **하지 않은 검증 기록 거부:** 별도 채팅에서 한 검증은 기록하지 않고, 대신 직접 실행하자고 제안했습니다.
4. **독립 검증:** `tests/check_per90.py`가 5명 모두 `scout.py`와 일치했고, 제 손계산과도 같았습니다.
5. **질문이 바뀌면 순위도 바뀜:** 나이 상한 23 → 24에서 선수가 추가되고, K2 오른쪽 풀백 한 명은 태클 1위·패스 정확도 꼴찌였습니다.
6. **데이터 한계 지적:** 두 선수는 듀얼 % 종류가 불분명한데, `scout.py`는 전체 듀얼로 처리한다고 알려줬습니다.

## 6. 검증

자세한 내용: [docs/verification.md](docs/verification.md). 실제 결과는 모두 실행 화면에서 옮겼습니다.

| 사례 | 확인한 것 | 결과 |
|---|---|---|
| A. 나이 상한 23 → 24 | `rank --by passes --side L --specialists`를 `--max-age 23`과 `24`로 실행 | 24세로 바꾸면 Kim Ryun-Seong(K1), Son Ho-Jun·Kim Ju-Sung·Lee Taek-Geun(K2)이 추가됨. 통과 |
| B. 같은 그룹, 지표 2개 | K2 오른쪽 전문 풀백, `tackles`와 `pass_acc` | Noh Seung-Ik @ Paju Frontier가 태클 1위(2.58), 패스 정확도 8명 중 8위(62.2%, 239/384). 통과 |
| C. 90분당 값 독립 계산 | `python3 tests/check_per90.py` | `5/5 match - PASS`, 종료 코드 0 |
| D. 오류를 잡는지 | 스크래치 복사본의 `scout.py`에서 `* 90`을 `* 91`로 변경 | 5명 모두 FAIL (예: Choi Woo-Jin 33.56 vs 33.93), `0/5 match`, 종료 코드 1. 통과 |

**`tests/check_per90.py`**는 `scout.py`를 import하지 않습니다. 필터(23세 이하 왼쪽 전문 풀백, 600분 이상)를 스스로 다시 적용하고, CSV에서 `successful_passes × 90 / league_minutes`를 계산한 뒤, `scout.py`를 실행해 출력과 비교합니다. 하나라도 다르면 종료 코드 1로 끝납니다.

**예외 사례:**

- **D (일부러 틀린 계산):** 틀린 공식을 잡아내므로, 이 스크립트는 실제로 실패할 수 있습니다.
- **A (나이 경계):** 추가된 4명은 모두 정확히 24세이므로, `--max-age`는 상한 나이를 포함합니다.
- **출전 시간 빈칸:** `league_minutes`가 빈 4명은 표본 부족으로 처리되어 두 스크립트 모두에서 제외됩니다.

## 7. 잘된 점과 어려웠던 점

### 잘된 점
1. 코드보다 규칙을 먼저 정했다. CLAUDE.md에 "계산은 scout.py만 한다", "K리그1과 2를 섞지 않는다", "600분 미만은 표본 부족으로 표시한다" 같은 규칙을 먼저 적었다. 덕분에 Claude가 숫자를 지어내지 않았다.
2. AI 결과를 그대로 믿지 않고 확인했다. scout.py 결과를 내가 따로 계산한 값, 그리고 별도의 검증 스크립트와 비교했다. 5명 모두 값이 일치했다.
3. 데이터를 작게, 정직하게 모았다. 팀 단위로 나눠서 모았고, 확실하지 않은 값은 추측하지 않고 빈칸으로 둔 뒤 "확인 필요"라고 표시했다.

### 어려웠던 점
1. 리포트 파일이 덮어써졌다. 같은 날 다른 조건으로 리포트를 저장하면 기존 파일이 경고 없이 사라졌다. Claude Code가 이 문제를 찾았고, 파일 이름에 조건을 넣고 중복이면 _2, _3을 붙이도록 고쳐 달라고 했다.
2. Claude Code가 요청보다 많은 일을 했다. 계획만 요청했는데 코드와 명령어까지 한 번에 만들었다. 다음에는 단계마다 내 승인을 받고 진행하라고 요청할 것이다.
3. 환경 설정에서 막혔다. 다운로드한 CSV를 Ubuntu에서 찾지 못했고, GitHub가 비밀번호 로그인을 거부했다. 터미널에서 파일을 직접 만들고, gh auth login으로 로그인해서 해결했다.

## 8. 알려진 한계

- **한 시점 데이터**(2026-10-27)이고, **FotMob 하나만** 사용했으며 다른 출처로 교차 확인하지 않았습니다.
- **출전 시간 빈칸:** Ahn Jae-Min, Choi Jae-Hyeok, Lim Jun-Young, Joao Pedro는 K리그 출전 시간이 없어 순위에 넣을 수 없습니다.
- **듀얼 % 종류:** Kim Ju-Sung과 Son Ho-Jun은 notes에 전체인지 지상인지 적혀 있지 않습니다. 값은 전체 듀얼로 처리되며, FotMob에서 확인이 필요합니다.
- **지상 듀얼 값이 적음:** `ground_duels_won_pct`가 있는 행은 4개뿐입니다.
- **아주 작은 표본의 비율**(예: 크로스 2/2 = 100%)은 원래 개수를 함께 보여줘도 믿기 어렵습니다.
- **검증 범위가 좁음:** `check_per90.py`는 지표 1개, 선수 5명만 확인합니다. 전환 선수(예: Kim Ho-Jin, Yu Sun)와 다른 지표는 다루지 않습니다.
- **기록만 사용:** 전술이나 영상은 반영되지 않고, `rating_*`는 아직 비어 있습니다.
- notes의 **"to verify" 항목**은 아직 확인하지 않았습니다.

## 9. 채점용 핵심 파일

1. `scout.py`: 필터, 순위, 90분당 계산, 메모, 리포트 저장
2. `CLAUDE.md`: 이 프로젝트에서 Claude Code가 따르는 규칙
3. `.claude/commands/report.md`: `/report` 슬래시 명령어
4. `tests/check_per90.py`: 90분당 값 독립 검증 (5/5 PASS)
5. `data/players.csv`: 59명 데이터
