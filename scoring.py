# =====================================
# scoring.py
# Crypto Pro Premium Bot V3
# =====================================

def clamp(value, min_value=0, max_value=100):
    return max(min_value, min(max_value, value))


# =====================================
# LONG SCORING
# =====================================

def score_long(
    oi_change_1h,
    oi_change_4h,
    volume_change,
    price_change,
    day_change,
    funding_rate,
    trend_score
):
    score = 0
    reasons = []

    # -----------------------------
    # OI (40 points)
    # -----------------------------

    oi_score = 0

    if oi_change_1h >= 15:
        oi_score += 25
        reasons.append(f"OI 1H +{oi_change_1h:.1f}%")

    elif oi_change_1h >= 10:
        oi_score += 18
        reasons.append(f"OI 1H +{oi_change_1h:.1f}%")

    elif oi_change_1h >= 5:
        oi_score += 10
        reasons.append(f"OI 1H +{oi_change_1h:.1f}%")

    if oi_change_4h >= 30:
        oi_score += 15
        reasons.append(f"OI 4H +{oi_change_4h:.1f}%")

    elif oi_change_4h >= 20:
        oi_score += 10
        reasons.append(f"OI 4H +{oi_change_4h:.1f}%")

    elif oi_change_4h >= 10:
        oi_score += 5
        reasons.append(f"OI 4H +{oi_change_4h:.1f}%")

    score += min(40, oi_score)

    # -----------------------------
    # VOLUME (25)
    # -----------------------------

    if volume_change >= 150:
        score += 25
        reasons.append(f"Volume +{volume_change:.1f}%")

    elif volume_change >= 100:
        score += 20
        reasons.append(f"Volume +{volume_change:.1f}%")

    elif volume_change >= 50:
        score += 10
        reasons.append(f"Volume +{volume_change:.1f}%")

    # -----------------------------
    # DAY CHANGE
    # -----------------------------

    if 0 <= day_change <= 5:
        score += 15
        reasons.append("Still early")

    elif 5 < day_change <= 10:
        score += 8
        reasons.append("Moving")

    elif 10 < day_change <= 15:
        score += 3
        reasons.append("Extended")

    elif day_change > 15:
        score -= 10
        reasons.append("Overextended")

    # -----------------------------
    # FUNDING
    # -----------------------------

    if abs(funding_rate) <= 0.01:
        score += 10
        reasons.append("Neutral funding")

    elif abs(funding_rate) <= 0.03:
        score += 5
        reasons.append("Healthy funding")

    else:
        score -= 10
        reasons.append("Crowded trade")

    # -----------------------------
    # TREND
    # -----------------------------

    score += min(10, max(0, trend_score))

    if trend_score >= 7:
        reasons.append("Strong trend")

    elif trend_score >= 4:
        reasons.append("Trend building")

    return clamp(score), reasons


# =====================================
# SHORT SCORING
# =====================================

def score_short(
    oi_change_1h,
    oi_change_4h,
    volume_change,
    price_change,
    day_change,
    funding_rate,
    breakdown_score
):
    score = 0
    reasons = []

    # -----------------------------
    # Reject fake shorts
    # -----------------------------

    if breakdown_score == 0 and price_change >= 0:
        return 0, []

    # -----------------------------
    # OI
    # -----------------------------

    if oi_change_1h >= 10:
        score += 15
        reasons.append(f"OI 1H +{oi_change_1h:.1f}%")

    if oi_change_4h >= 20:
        score += 10
        reasons.append(f"OI 4H +{oi_change_4h:.1f}%")

    # -----------------------------
    # VOLUME
    # -----------------------------

    if volume_change >= 100:
        score += 25
        reasons.append(f"Volume +{volume_change:.1f}%")

    elif volume_change >= 50:
        score += 15
        reasons.append(f"Volume +{volume_change:.1f}%")

    # -----------------------------
    # FUNDING
    # -----------------------------

    if funding_rate >= 0.05:
        score += 25
        reasons.append("Overcrowded longs")

    elif funding_rate >= 0.03:
        score += 15
        reasons.append("Long bias")

    # -----------------------------
    # BREAKDOWN
    # -----------------------------

    score += min(25, breakdown_score)

    if breakdown_score >= 15:
        reasons.append("Breakdown detected")

    # -----------------------------
    # DAY CHANGE
    # -----------------------------

    if day_change <= -10:
        score += 10
        reasons.append("Heavy weakness")

    elif day_change <= -5:
        score += 5
        reasons.append("Weak day")

    return clamp(score), reasons


# =====================================
# RANKING
# =====================================

def rank_candidates(candidates):
    return sorted(
        candidates,
        key=lambda x: x["score"],
        reverse=True
    )
