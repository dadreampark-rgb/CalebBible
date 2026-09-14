# Orchestration Trace 양식 (응답 강제 구조)

> 대표 스킬이 사용자 명령에 응답할 때 반드시 이 4부 구조로 표시(기준 #10). inline 시뮬레이션 단독 금지.

```
## (a) 발동·분류
- 발동 마스터: churchplan-prayer-scripture-kit
- 상속(있으면): goals 영성 축(통독 완주·새벽 참여 신호)·vision(표어·core_scriptures)
- 목사 1회 입력: 통독 트랙 선택 / 새벽 시즌 시점 / 교회 기도 형편 (지원 스킬 — 없어도 작동)

## (b) 호출 Trace
| 순서 | 하위 스킬 | AI Agent | 한 일 | 산출 |
|------|-----------|----------|-------|------|
| 1 | scripture-track-builder ★ | 길을 내는 자 | 통독 트랙 일별 배정·정경 실재·은혜 융통성 | reading_track |
| 2 | prayer-topic-composer | 함께 아뢰는 자 | 월별 전교인 기도제목(전사) | prayer_topics |
| 3 | family-worship-guide | 식탁을 펴는 자 | 가정예배 가이드(1:1 말씀나눔·실재 본문) | family_worship |
| 4 | dawn-prayer-season-writer | 새벽을 깨우는 자 | 새벽기도 시즌 안내문(표어 연계·은혜 톤) | dawn_prayer_season |
| (확정 후) 5 | kit-renderer | 키트를 묶는 자 | 인쇄용 키트 docx+pdf | 키트 파일 |
| 6 | fidelity-guard | 은혜를 지키는 자 | 성경 실재·곡해·율법 톤 검증 | 검증 리포트 |

## (c) 하위 산출물 (각 별도 섹션)
### 📖 연간 성경통독 트랙 (scripture-track-builder — 정경 실재·은혜 융통성)
### 🙏 월별 전교인 기도제목 (prayer-topic-composer)
### 🏠 가정예배 가이드 (family-worship-guide — 1:1 말씀나눔)
### 🌅 새벽기도 시즌 안내문 (dawn-prayer-season-writer)
### 📦 인쇄용 영성 키트 (kit-renderer — 목사 확정 후에만)
### 🛡️ 영성 키트 검증 (fidelity-guard)

## (d) 마스터 통합 + 확정 초대 (별도 섹션)
### 📖 통독 트랙 한눈 (어떤 트랙·은혜의 융통성)
### 🙏 월별 기도제목 / 🏠 가정예배 / 🌅 새벽 시즌
### 🌱 영성 축 연결 (통독 완주·새벽 참여는 #9 점검으로 — 채찍 아닌 격려)
### 🙏 "은혜의 초청입니다. 통독 트랙과 새벽 시즌을 어떻게 정하시겠습니까?"
   — [목사 검토·확정 HITL 대기. 트랙·기도제목·시즌 확정 전에는 최종 키트를 묶지 않는다.]
### (확정 완료 후) 📦 인쇄용 영성 키트 (docx + pdf)
```

## 원칙
- **(d)에서 반드시 확정을 기다린다.** 통독 트랙·시즌 제시와 최종 키트 묶기 사이에 목사의 확정 HITL이 있다.
- **은혜의 초청이지 율법적 압박이 아니다** — 율법·정죄 어휘 금지(전 섹션).
- **성경은 실재해야 한다** — bible_validator·곡해 금지.
- **전사하되 지어내지 않는다** — 없는 약속·수치 단언 금지.
- **지원 스킬·자유 호출** — goals/vision 없어도 목사 입력으로 작동.
- fidelity-guard 실패 시 (c)에 위반 노출, 해당 분석 재실행(임의 보정 금지).
