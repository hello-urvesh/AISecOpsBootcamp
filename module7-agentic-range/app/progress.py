"""
Simple progress and gamification.

Tracks which range and difficulty each player has solved, awards points, and
gives a rank. Stored as a small json file so progress survives a restart.
"""
import os
import json
import threading

STORE = os.environ.get("PROGRESS_PATH", "/data/progress.json")
_lock = threading.Lock()

RANKS = [
    (0, "Recruit"),
    (300, "Field Operator"),
    (700, "Red Team Specialist"),
    (1200, "Elite Red Teamer"),
]


def _load():
    try:
        with open(STORE) as f:
            return json.load(f)
    except Exception:
        return {}


def _save(data):
    os.makedirs(os.path.dirname(STORE), exist_ok=True)
    tmp = STORE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f)
    os.replace(tmp, STORE)


def _key(player):
    return player.strip() or "player"


def get(player):
    with _lock:
        data = _load()
        return data.get(_key(player), {"solves": {}, "points": 0})


def solve(player, range_id, difficulty, points):
    """Record a solve. Returns (was_first, total_points, rank)."""
    with _lock:
        data = _load()
        rec = data.setdefault(_key(player), {"solves": {}, "points": 0})
        tag = f"{range_id}:{difficulty}"
        first = tag not in rec["solves"]
        if first:
            rec["solves"][tag] = points
            rec["points"] = sum(rec["solves"].values())
            _save(data)
        return first, rec["points"], rank_for(rec["points"])


def rank_for(points):
    name = RANKS[0][1]
    for threshold, label in RANKS:
        if points >= threshold:
            name = label
    return name


def next_rank(points):
    for threshold, label in RANKS:
        if points < threshold:
            return label, threshold
    return None, None


def is_solved(player, range_id, difficulty):
    rec = get(player)
    return f"{range_id}:{difficulty}" in rec.get("solves", {})


def leaderboard():
    with _lock:
        data = _load()
    rows = [{"player": p, "points": v.get("points", 0), "solved": len(v.get("solves", {}))}
            for p, v in data.items()]
    rows.sort(key=lambda r: (-r["points"], r["player"]))
    return rows
