#!/usr/bin/env python3
"""호러·판별(이상현상 검문 교대 근무) 장르 규칙 시뮬레이션. 표준 라이브러리만, 시드 고정 결정론."""
import argparse
import datetime
import random
import sys

# ------------------------------------------------------------ 밸런스 (logic.md §2 JSON과 같은 값)
CONFIG = {
    "nights": 5,                        # 예시값 (FNAF 5밤 구조 참고)
    "night_seconds": 600,               # FNAF 1: 한 밤 약 10분 (README §4)
    "visitor_seconds": 45,              # 예시값: 손님 1명 평균 소요
    "visitors_per_night": 12,           # 예시값
    "scripted_per_night": [2, 3],       # Papers, Please: 하루 스크립트 2~3명 (README §4)
    "rules_per_night": [1, 2],          # 예시값 (★4: 밤마다 1~2개)
    "anomaly_ratio_by_night": [0.25, 0.30, 0.35, 0.40, 0.50],  # 예시값: 밤마다 상승
    "lethal_cap_per_night": 1,          # 예시값 (★6: 치명은 드물게)
    "free_mistakes_per_night": 2,       # Papers, Please (README §4)
    "penalty_ladder": [5, 5, 10, 15, 20],  # Papers, Please (README §4)
    "penalty_step_after_ladder": 5,     # 예시값: "20…" 이후 +5씩 연장
    "fee_per_visitor": 10,              # 예시값 (복채, 게임 내 재화)
    "threat_per_admit": 1,              # 예시값
    "threat_max": 3,                    # 예시값: 누적 시 게임 오버
    "threat_reset_per_night": True,     # 예시값
    "too_subtle_threshold": 0.30,       # 예시값: 발견률 미만이면 '너무 미묘'
    "too_subtle_window_nights": 3,      # 예시값
    "too_subtle_min_shown": 4,          # 예시값
    "bot_false_reject_rate": 0.05,      # 예시값 (테스트 봇 전용)
    "current_year": 2026,               # 서류 대조 기준 연도
    "ipchun_month_day": [2, 4],         # 예시값: 입춘 경계. 실제는 만세력 절기표(anomaly_detection.md §4)
}
ACCEPT, REJECT = "accept", "reject"     # 판정 동사는 둘뿐 (★1)

# 이상현상 풀. rule = 이것을 '찾을 수 있게' 해 주는 규칙. visibility = 테스트 봇의 발견 확률(예시값).
ANOMALY_POOL = [
    {"id": "six_fingers", "kind": "person", "rule": "r_face", "visibility": 0.75, "lethal": False},
    {"id": "no_shadow", "kind": "person", "rule": "r_face", "visibility": 0.55, "lethal": False},
    {"id": "cold_breath", "kind": "person", "rule": "r_face", "visibility": 0.15, "lethal": False},
    {"id": "date_mismatch", "kind": "data", "rule": "r_date", "visibility": 0.80, "lethal": False},
    {"id": "future_birth_year", "kind": "data", "rule": "r_date", "visibility": 0.85, "lethal": False},
    {"id": "mirror_no_reflection", "kind": "person", "rule": "r_mirror", "visibility": 0.60, "lethal": False},
    {"id": "zodiac_mismatch", "kind": "data", "rule": "r_zodiac", "visibility": 0.70, "lethal": False},
    {"id": "unblinking", "kind": "person", "rule": "r_blink", "visibility": 0.45, "lethal": False},
    {"id": "day_pillar_mismatch", "kind": "data", "rule": "r_daypillar", "visibility": 0.60, "lethal": False},
    {"id": "whisper_behind", "kind": "person", "rule": "r_whisper", "visibility": 0.40, "lethal": False},
    {"id": "ipchun_boundary", "kind": "data", "rule": "r_ipchun", "visibility": 0.50, "lethal": False},
    {"id": "hollow_eyes", "kind": "person", "rule": "r_knock", "visibility": 0.90, "lethal": True},
]
POOL_BY_ID = {a["id"]: a for a in ANOMALY_POOL}
# 규칙. night = 그 밤의 '주인의 공지'(NOTICE 상태)에서 전달한다. 대사 중에는 주지 않는다 (★4).
RULES = [
    {"id": "r_face", "night": 1, "text": "손님의 손가락 수와 그림자를 확인하라"},
    {"id": "r_date", "night": 1, "text": "말한 생년월일시를 만세력 기록과 대조하라"},
    {"id": "r_mirror", "night": 2, "text": "거울에 손님이 비치는지 보라"},
    {"id": "r_zodiac", "night": 2, "text": "띠가 출생연도와 맞는지 보라"},
    {"id": "r_blink", "night": 3, "text": "눈을 깜빡이지 않는 손님은 돌려보내라"},
    {"id": "r_daypillar", "night": 4, "text": "일주가 기록과 맞는지 보라"},
    {"id": "r_whisper", "night": 4, "text": "등 뒤에서 속삭임이 들리면 돌려보내라"},
    {"id": "r_ipchun", "night": 5, "text": "입춘 전 출생은 전년 연주를 쓴다"},
    {"id": "r_knock", "night": 5, "text": "노크 소리 뒤에 온 손님은 절대 들이지 마라"},
]

# 수작업 손님 (밤마다 2~3명). anomaly=None이면 정상 손님.
SCRIPTED = {
    1: [("단골 할머니", None), ("장갑 낀 청년", "six_fingers")],
    2: [("야간 택시기사", None), ("거울을 피하는 여자", "mirror_no_reflection"), ("수험생", None)],
    3: [("띠를 잘못 말한 남자", "zodiac_mismatch"), ("옆집 아저씨", None)],
    4: [("경비원", None), ("눈을 뜬 채 웃는 손님", "unblinking"), ("일주가 다른 손님", "day_pillar_mismatch")],
    5: [("노크 뒤의 손님", "hollow_eyes"), ("단골 할머니", None)],
}

ZODIAC = ["쥐", "소", "호랑이", "토끼", "용", "뱀", "말", "양", "원숭이", "닭", "개", "돼지"]
GANJI = ["갑을병정무기경신임계"[i % 10] + "자축인묘진사오미신유술해"[i % 12] for i in range(60)]


# ------------------------------------------------------------ 서류 대조 (데이터 이상현상)
def make_record(rng, cfg=CONFIG):
    """가게 만세력에 기록된 '진짜' 생년월일시."""
    y = rng.randint(cfg["current_year"] - 70, cfg["current_year"] - 15)
    return {"year": y, "month": rng.randint(1, 12), "day": rng.randint(1, 28), "hour": rng.randint(0, 23)}

def derive(record, cfg=CONFIG):
    """기록 → 띠·연주·일주. 연주·띠는 입춘 경계로 바뀐다 (예시 공식, 실제는 만세력 라이브러리)."""
    py = record["year"] if (record["month"], record["day"]) >= tuple(cfg["ipchun_month_day"]) else record["year"] - 1
    ordinal = datetime.date(record["year"], record["month"], record["day"]).toordinal()
    return {"zodiac": ZODIAC[(py - 4) % 12], "year_pillar": GANJI[(py - 4) % 60], "day_pillar": GANJI[ordinal % 60]}

def make_stated(record, anomaly_id, rng, cfg=CONFIG):
    """손님이 '말한' 서류. anomaly_id가 데이터 이상현상이면 그 필드 하나만 어긋나게 만든다."""
    stated = dict(record, **derive(record, cfg))
    if anomaly_id == "date_mismatch":
        stated["day"] = rng.choice([d for d in range(1, 29) if d != record["day"]])
    elif anomaly_id == "future_birth_year":
        stated["year"] = cfg["current_year"] + rng.randint(1, 30)
    elif anomaly_id == "zodiac_mismatch":
        stated["zodiac"] = ZODIAC[(ZODIAC.index(stated["zodiac"]) + rng.choice([1, -1])) % 12]
    elif anomaly_id == "day_pillar_mismatch":
        stated["day_pillar"] = GANJI[(GANJI.index(stated["day_pillar"]) + rng.randint(1, 59)) % 60]
    elif anomaly_id == "ipchun_boundary":   # 입춘 전 출생인데 달력 연도로 연주를 말함
        record["month"], record["day"] = cfg["ipchun_month_day"][0], rng.randint(1, cfg["ipchun_month_day"][1] - 1)
        stated = dict(record, **derive(record, cfg))
        stated["year_pillar"] = GANJI[(record["year"] - 4) % 60]
    return stated

def cross_check(stated, record, cfg=CONFIG):
    """말한 것과 기록된 것을 대조해 어긋난 필드 목록을 돌려준다. 비어 있으면 일치."""
    flags = ["date"] if any(stated[k] != record[k] for k in ("year", "month", "day", "hour")) else []
    if stated["year"] > cfg["current_year"]:
        flags.append("future_year")
    real = derive(record, cfg)
    return flags + [k for k in ("zodiac", "year_pillar", "day_pillar") if stated[k] != real[k]]


# ------------------------------------------------------------ 뽑기 가방 · 발견률 로그 · 벌점
class AnomalyBag:
    """Exit 8 규칙: 나올 수 있는 이상현상이 전부 나오기 전에는 같은 것을 다시 뽑지 않는다."""

    def __init__(self, ids):
        self.all, self.remaining = list(ids), list(ids)

    def draw(self, allowed, rng, avoid=()):
        """allowed(해금된 id) 안에서 중복 없이 뽑는다. 소진되면 다시 채운다. avoid(이 밤에 이미 나온 것)는 후순위."""
        for _ in range(2):
            pool = [i for i in self.remaining if i in allowed]
            cands = [i for i in pool if i not in avoid] or pool
            if cands:
                pick = rng.choice(cands)
                self.remaining.remove(pick)
                return pick
            self.remaining = list(self.all)
        raise ValueError("해금된 이상현상이 없음")

    def consume(self, aid):
        """수작업 손님이 쓴 이상현상도 가방에서 뺀다."""
        if aid in self.remaining:
            self.remaining.remove(aid)


class DetectionLog:
    """이상현상별 (밤 → [노출, 발견]) 기록 (★8)."""

    def __init__(self):
        self.rows = {}

    def record(self, night, aid, detected):
        cell = self.rows.setdefault(aid, {}).setdefault(night, [0, 0])
        cell[0], cell[1] = cell[0] + 1, cell[1] + int(detected)

    def rate(self, aid, nights):
        """(노출 수, 발견률). 노출이 없으면 발견률 None."""
        cells = [self.rows.get(aid, {}).get(n, [0, 0]) for n in nights]
        shown = sum(c[0] for c in cells)
        return shown, (sum(c[1] for c in cells) / shown if shown else None)

    def too_subtle(self, last_night, cfg=CONFIG):
        """최근 N밤 동안 충분히 노출됐는데 발견률이 임계 미만인 이상현상 id 목록."""
        nights = range(max(1, last_night - cfg["too_subtle_window_nights"] + 1), last_night + 1)
        rates = {aid: self.rate(aid, nights) for aid in self.rows}
        return sorted(a for a, (s, r) in rates.items() if s >= cfg["too_subtle_min_shown"] and r < cfg["too_subtle_threshold"])

def penalty_for(mistakes, cfg=CONFIG):
    """그 밤 k번째 실수의 벌점: 면제 횟수까지 0, 이후 사다리, 사다리 끝나면 +step씩."""
    idx, ladder = mistakes - cfg["free_mistakes_per_night"] - 1, cfg["penalty_ladder"]
    if idx < 0:
        return 0
    return ladder[idx] if idx < len(ladder) else ladder[-1] + cfg["penalty_step_after_ladder"] * (idx - len(ladder) + 1)


# ------------------------------------------------------------ 손님 · 봇
class Visitor:
    """줄에 선 손님 하나. 정상이거나 이상현상 하나를 지닌다."""

    def __init__(self, night, index, name, anomaly_id, scripted):
        self.night, self.index, self.name, self.anomaly_id, self.scripted = night, index, name, anomaly_id, scripted
        self.is_anomaly = anomaly_id is not None
        self.lethal = bool(anomaly_id and POOL_BY_ID[anomaly_id]["lethal"])
        self.telegraph, self.record, self.stated = False, None, None   # telegraph: 이 손님 차례에 예고(노크·잡음)

def scripted_bot(visitor, rng, cfg=CONFIG):
    """플레이테스터 대역 봇. visibility 확률로 '살펴보고', 데이터형은 실제 대조 결과로 판단한다."""
    if not visitor.is_anomaly:
        return REJECT if rng.random() < cfg["bot_false_reject_rate"] else ACCEPT
    a = POOL_BY_ID[visitor.anomaly_id]
    looked = rng.random() < a["visibility"]
    if a["kind"] == "data":
        return REJECT if looked and cross_check(visitor.stated, visitor.record, cfg) else ACCEPT
    return REJECT if looked else ACCEPT


# ------------------------------------------------------------ 게임 (상태 머신 + 밤 루프)
class Game:
    """LOBBY → NOTICE → SHIFT → NIGHT_END → (다음 밤 | RESULTS). SHIFT 중 위협 누적 시 GAME_OVER."""

    def __init__(self, seed, cfg=CONFIG, pool=ANOMALY_POOL, rules=RULES, scripted=SCRIPTED, bot=scripted_bot):
        self.rng = random.Random(seed)
        self.cfg, self.pool, self.rules, self.scripted, self.bot = cfg, pool, rules, scripted, bot
        self.bag, self.detlog = AnomalyBag([a["id"] for a in pool]), DetectionLog()
        self.state, self.money, self.threat, self.active_rules, self.events, self.nights = "LOBBY", 0, 0, [], [], []

    def transition(self, to):
        """상태 전이를 기록하고 바꾼다."""
        self.events.append(("state", self.state, to))
        self.state = to

    def unlocked_ids(self):
        """지금까지 전달된 규칙으로 찾을 수 있는 이상현상 id 집합."""
        return {a["id"] for a in self.pool if a["rule"] in self.active_rules}

    def generate_visitors(self, n):
        """수작업 손님을 고르게 배치하고, 나머지는 그 밤의 규칙·비율로 생성한다."""
        cfg, total, lethal_used = self.cfg, self.cfg["visitors_per_night"], 0
        scripted, (lo, hi) = self.scripted.get(n, []), cfg["scripted_per_night"]
        assert lo <= len(scripted) <= hi, f"밤 {n} 수작업 손님 수 {len(scripted)}"
        visitors = [None] * total
        for i, (name, aid) in enumerate(scripted):       # 지루한 구간이 없도록 고르게 퍼뜨린다
            slot = int((i + 1) * total / (len(scripted) + 1) + 0.5) - 1
            visitors[slot] = Visitor(n, slot, name, aid, True)
            if aid:
                self.bag.consume(aid)
                lethal_used += int(POOL_BY_ID[aid]["lethal"])
        free = [i for i in range(total) if visitors[i] is None]
        ratio = cfg["anomaly_ratio_by_night"][min(n, len(cfg["anomaly_ratio_by_night"])) - 1]
        anomaly_slots = set(self.rng.sample(free, int(len(free) * ratio + 0.5)))
        for i in free:
            aid = None
            if i in anomaly_slots:
                allowed = self.unlocked_ids()
                if lethal_used >= cfg["lethal_cap_per_night"] or i == 0:   # 첫 손님은 치명형 금지(예고 자리 확보)
                    allowed = {a for a in allowed if not POOL_BY_ID[a]["lethal"]}
                aid = self.bag.draw(allowed, self.rng, {v.anomaly_id for v in visitors if v and v.is_anomaly})
                lethal_used += int(POOL_BY_ID[aid]["lethal"])
            visitors[i] = Visitor(n, i, f"손님{i + 1}", aid, False)
        for i, v in enumerate(visitors):                  # 서류 생성 + 치명형 앞 손님에 예고 (★6)
            v.record = make_record(self.rng, cfg)
            v.stated = make_stated(v.record, v.anomaly_id, self.rng, cfg)
            if v.lethal:
                visitors[i - 1].telegraph = True
        return visitors

    def resolve(self, night, v, verdict):
        """판정 한 건을 정산한다: 복채·벌점·위협. 재화 증감은 이 함수만 거친다."""
        correct = (verdict == REJECT) == v.is_anomaly
        if correct and verdict == ACCEPT:
            night["fees"] += self.cfg["fee_per_visitor"]
        elif not correct:
            night["mistakes"] += 1
            night["penalties"] += penalty_for(night["mistakes"], self.cfg)
            if v.is_anomaly:                              # 들여보냄 → 즉사 대신 위협 게이지 (★5)
                self.threat += self.cfg["threat_max"] if v.lethal else self.cfg["threat_per_admit"]
        if v.is_anomaly:
            self.detlog.record(night["n"], v.anomaly_id, verdict == REJECT)
        self.events.append(("visitor", night["n"], v.index, v.anomaly_id, verdict, self.state))
        return correct

    def run_night(self, n):
        """한 밤: 공지(규칙 전달) → 교대 근무(타이머 안에서 손님 처리) → 결산."""
        cfg = self.cfg
        night = {"n": n, "mistakes": 0, "fees": 0, "penalties": 0, "elapsed": 0, "served": 0, "timer_ended": False}
        self.transition("NOTICE")
        for r in [r for r in self.rules if r["night"] == n]:
            self.active_rules.append(r["id"])
            self.events.append(("rule", n, r["id"], self.state))
        if cfg["threat_reset_per_night"]:
            self.threat = 0
        night["visitors"] = visitors = self.generate_visitors(n)
        night["anomalies"] = sum(v.is_anomaly for v in visitors)
        self.transition("SHIFT")
        for v in visitors:
            if night["elapsed"] + cfg["visitor_seconds"] > cfg["night_seconds"]:
                night["timer_ended"] = True
                break
            night["elapsed"] += cfg["visitor_seconds"]
            night["served"] += 1
            self.resolve(night, v, self.bot(v, self.rng, cfg))
            if self.threat >= cfg["threat_max"]:
                self.transition("GAME_OVER")
                break
        self.money += night["fees"] - night["penalties"]
        night["threat_end"] = self.threat
        self.nights.append(night)
        if self.state == "SHIFT":
            self.transition("NIGHT_END")
        return night

    def run(self):
        """로비에서 시작해 밤을 차례로 돌리고 요약을 돌려준다."""
        for n in range(1, self.cfg["nights"] + 1):
            if self.run_night(n) and self.state == "GAME_OVER":
                break
        if self.state != "GAME_OVER":
            self.transition("RESULTS")
        return {"state": self.state, "money": self.money, "nights_done": len(self.nights),
                "too_subtle": self.detlog.too_subtle(len(self.nights), self.cfg)}


# ------------------------------------------------------------ 테스트 (이름은 logic.md §3 '검증'과 일치)
_honest_bot = lambda v, rng, cfg: REJECT if v.is_anomaly else ACCEPT   # 항상 정답인 봇 (생성 규칙 검사용)  # noqa: E731

def test_anomaly_no_repeat_until_exhausted():
    rng, ids = random.Random(1), [a["id"] for a in ANOMALY_POOL]
    bag = AnomalyBag(ids)
    assert sorted(bag.draw(set(ids), rng) for _ in ids) == sorted(ids), "소진 전 중복 발생"
    assert sorted(bag.draw(set(ids), rng) for _ in ids) == sorted(ids), "리필 후 한 바퀴에 중복 발생"
    small = AnomalyBag(["a", "b", "c"])
    night = [small.draw({"a", "b"}, rng, set()) for _ in range(2)]
    assert small.draw({"a", "b"}, rng, set(night)) in night, "해금 2개뿐이면 리필 후 재등장은 허용"
    assert small.draw({"a", "b", "c"}, rng, set(night)) == "c", "리필 뒤에는 이 밤에 안 나온 것을 먼저"

def test_anomaly_draw_only_unlocked():
    rng, allowed = random.Random(2), {"six_fingers", "no_shadow"}
    bag = AnomalyBag([a["id"] for a in ANOMALY_POOL])
    draws = [bag.draw(allowed, rng) for _ in range(10)]
    assert set(draws) <= allowed and draws[0] != draws[1], draws

def test_visitor_mix_scripted_and_procedural():
    g, (lo, hi) = Game(3), CONFIG["scripted_per_night"]
    for n in range(1, CONFIG["nights"] + 1):
        g.active_rules = [r["id"] for r in RULES if r["night"] <= n]
        vs = g.generate_visitors(n)
        s = [v.index for v in vs if v.scripted]
        assert len(vs) == CONFIG["visitors_per_night"] and lo <= len(s) <= hi, s
        assert s[0] > 0 and s[-1] < len(vs) - 1, "수작업 손님이 맨 앞/뒤에 몰림"
        assert len(vs) - len(s) == sum(not v.scripted for v in vs)

def test_rules_accumulate_per_night():
    lo, hi = CONFIG["rules_per_night"]
    g = Game(4)
    for n in range(1, CONFIG["nights"] + 1):
        assert lo <= sum(r["night"] == n for r in RULES) <= hi, n
        night = g.run_night(n)
        assert len(g.active_rules) == sum(r["night"] <= n for r in RULES)
        for v in night["visitors"]:
            assert not v.is_anomaly or POOL_BY_ID[v.anomaly_id]["rule"] in g.active_rules, (n, v.anomaly_id)

def test_rules_delivered_outside_dialogue():
    g = Game(5)
    g.run()
    rule_events = [e for e in g.events if e[0] == "rule"]
    assert rule_events and all(e[3] == "NOTICE" for e in rule_events)
    assert all(e[5] == "SHIFT" for e in g.events if e[0] == "visitor")

def test_penalty_ladder_two_free_then_escalate():
    assert [penalty_for(k) for k in range(1, 9)] == [0, 0, 5, 5, 10, 15, 20, 25]

def test_penalty_resets_each_night():
    g = Game(6, bot=lambda v, rng, cfg: REJECT)   # 전부 돌려보내는 봇: 정상 손님마다 실수
    n1, n2 = g.run_night(1), g.run_night(2)
    assert n1["mistakes"] > CONFIG["free_mistakes_per_night"] and n2["mistakes"] > 0
    assert n2["penalties"] == sum(penalty_for(k) for k in range(1, n2["mistakes"] + 1))

def test_threat_gauge_game_over():
    g = Game(7, bot=lambda v, rng, cfg: ACCEPT)   # 전부 들여보내는 봇
    g.run()
    assert g.state == "GAME_OVER" and g.threat >= CONFIG["threat_max"] and len(g.nights) == 1
    assert g.nights[0]["served"] < CONFIG["visitors_per_night"], "게임 오버 뒤에도 손님을 받음"

def test_threat_resets_each_night():
    g = Game(8, bot=_honest_bot)
    g.threat = CONFIG["threat_max"] - 1
    g.run_night(1)
    assert g.threat == 0 and g.state == "NIGHT_END"

def test_document_crosscheck_flags_exactly_inconsistent():
    rng = random.Random(9)
    expect = {"date_mismatch": "date", "future_birth_year": "future_year", "zodiac_mismatch": "zodiac",
              "day_pillar_mismatch": "day_pillar", "ipchun_boundary": "year_pillar"}
    for _ in range(300):
        rec = make_record(rng)
        assert cross_check(make_stated(rec, None, rng), rec) == [], "정상 서류 오탐"
    for aid, field in expect.items():
        for _ in range(100):
            rec = make_record(rng)
            flags = cross_check(make_stated(rec, aid, rng), rec)
            assert field in flags, (aid, flags)

def test_night_escalation_anomaly_ratio_rises():
    ratios = CONFIG["anomaly_ratio_by_night"]
    assert all(a <= b for a, b in zip(ratios, ratios[1:])) and ratios[-1] > ratios[0]
    g = Game(10, bot=_honest_bot)
    g.run()
    counts = [nt["anomalies"] - sum(v.scripted and v.is_anomaly for v in nt["visitors"]) for nt in g.nights]
    assert len(counts) == CONFIG["nights"] and all(a <= b for a, b in zip(counts, counts[1:])), counts

def test_night_timer_ends_shift():
    cfg = dict(CONFIG, visitor_seconds=100)       # 12명 × 100초 > 600초 → 6명에서 끝
    night = Game(11, cfg=cfg).run_night(1)
    assert night["timer_ended"] and night["served"] == 6 and night["elapsed"] <= cfg["night_seconds"]
    assert not Game(11).run_night(1)["timer_ended"]

def test_lethal_rare_and_telegraphed():
    for seed in range(20):
        g = Game(100 + seed, bot=_honest_bot)
        g.run()
        for nt in g.nights:
            vs = nt["visitors"]
            assert sum(v.lethal for v in vs) <= CONFIG["lethal_cap_per_night"]
            for i, v in enumerate(vs):
                assert not v.lethal or (i > 0 and vs[i - 1].telegraph), (seed, nt["n"], i)

def test_detection_log_flags_too_subtle():
    log = DetectionLog()
    for n in (2, 3, 4):
        for i in range(2):
            log.record(n, "ghost", n == 2 and i == 0)     # 6회 노출, 1회 발견 ≈ 0.17
            log.record(n, "obvious", True)
    for _ in range(4):
        log.record(1, "stale", False)                     # 창(2~4밤) 밖이라 제외
    assert log.too_subtle(4) == ["ghost"], log.too_subtle(4)
    assert log.too_subtle(2) == ["stale"], "창 안(1~2밤)이면 stale은 잡히고, 노출 2회뿐인 ghost는 보류"

def test_full_run_deterministic():
    a, b = Game(42), Game(42)
    assert a.run() == b.run() and a.events == b.events and len(a.nights) >= 1

TESTS = [v for k, v in sorted(globals().items()) if k.startswith("test_")]


def run_tests():
    """모든 테스트를 돌리고 'passed k/n'을 출력한다. 종료 코드 = 실패 수."""
    failed = 0
    for t in TESTS:
        try:
            t()
            print(f"ok    {t.__name__}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"FAIL  {t.__name__}: {e!r}")
    print(f"passed {len(TESTS) - failed}/{len(TESTS)}")
    return failed

def run_demo(seed):
    """시드 고정으로 한 판을 돌리고 밤별 요약을 출력한다."""
    g = Game(seed)
    summary = g.run()
    print(f"seed={seed}  nights={CONFIG['nights']}  night={CONFIG['night_seconds']}s  visitors={CONFIG['visitors_per_night']}")
    for nt in g.nights:
        anomalies = [v.anomaly_id for v in nt["visitors"] if v.is_anomaly]
        print(f"밤 {nt['n']}: 새 규칙 {[r['id'] for r in RULES if r['night'] == nt['n']]} | 손님 {nt['served']}/{len(nt['visitors'])} "
              f"| 이상현상 {anomalies} | 실수 {nt['mistakes']} 벌점 -{nt['penalties']} 복채 +{nt['fees']} | 위협 {nt['threat_end']}")
    for aid in sorted(g.detlog.rows):
        print("  발견률 %-22s %d회 노출, %.2f" % ((aid,) + g.detlog.rate(aid, range(1, len(g.nights) + 1))))
    print(f"결과: {summary['state']}  재화 {summary['money']}  너무 미묘: {summary['too_subtle']}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="호러·판별 장르 규칙 시뮬레이션")
    for flag, kw in (("--test", {"action": "store_true"}), ("--demo", {"action": "store_true"}), ("--seed", {"type": int, "default": 2026})):
        ap.add_argument(flag, **kw)
    args = ap.parse_args()
    sys.exit(run_tests()) if args.test else run_demo(args.seed)
