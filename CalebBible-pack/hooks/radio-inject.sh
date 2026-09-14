#!/bin/sh
# 에이전트 라디오 수동적 인지 주입(AGENTRADIO) — PostToolUse(Bash)·UserPromptSubmit 훅.
# 미확인 멘션이 있을 때만 컨텍스트로 주입한다: 에이전트는 작업을 멈추지 않고 턴 경계에서
# 새 정보를 '지나가듯' 인지한다(wait_for_mention의 터미널 에이전트 등가).
# ★fast-path: dirty-<role> 플래그 파일 존재 검사([ -f ])만으로 무멘션 턴을 0비용 통과 —
#   PostToolUse는 고빈도라 python 기동 자체가 비용이다. 플래그는 radio send가 세운다.
PACK="${CALEBBIBLE_PACK_DIR:-$HOME/.CalebBible/pack}"
ROLE="${CALEBBIBLE_ROLE:-}"
[ -n "$ROLE" ] || exit 0                                   # 무역할 일반 셸 — 라디오 무관
RADIO_DIR="${CALEBBIBLE_RADIO_DIR:-$HOME/.CalebBible/state/radio}"
[ -f "$RADIO_DIR/dirty-$ROLE" ] || exit 0                  # 미확인 멘션 없음 — 0비용 통과
[ -f "$PACK/bin/CalebBible_radio.py" ] || exit 0            # 도구 부재 시 조용히 통과(H-HOOK-2)
CALEBBIBLE_PY="$(command -v python3 || command -v python || command -v py)"
[ -n "$CALEBBIBLE_PY" ] || exit 0
# --brief --ack: 압축 주입 + 커서 전진(같은 멘션의 매 턴 재주입 방지). 실패 무해(다음 send가 재플래그).
"$CALEBBIBLE_PY" "$PACK/bin/CalebBible_radio.py" inbox --role "$ROLE" --brief --ack 2>/dev/null || true
exit 0
