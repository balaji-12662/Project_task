# performance_app/utils.py
from .models import Review, Score, ReviewCycle, Employee, Goal
from django.db.models import Avg, Q, Prefetch
import math
from django.db import transaction

WEIGHTS = {
    'manager': 0.5,
    'self': 0.3,
    'peer': 0.2,
}

def _avg_score_for_review(review):
    agg = review.scores.aggregate(avg_score=Avg('score'))
    return agg['avg_score'] or 0.0

def calculate_final_score(employee_id, cycle_id):
    """
    Calculate weighted final score for employee for a cycle.
    Normalizes weights if one type missing.
    """
    reviews_qs = Review.objects.filter(employee_id=employee_id, cycle_id=cycle_id, status='submitted', is_deleted=False).prefetch_related('scores')
    if not reviews_qs.exists():
        return None

    type_averages = {}
    for r in reviews_qs:
        avg = _avg_score_for_review(r)
        type_averages.setdefault(r.review_type, []).append(avg)

    # compute mean per type
    mean_by_type = {}
    for t, vals in type_averages.items():
        mean_by_type[t] = sum(vals)/len(vals) if vals else 0.0

    # available types
    available_types = list(mean_by_type.keys())
    if not available_types:
        return None

    # normalize weights to available types
    total_weight = sum(WEIGHTS[t] for t in available_types if t in WEIGHTS)
    if total_weight == 0:
        # fallback equal weights
        normalized = {t: 1/len(available_types) for t in available_types}
    else:
        normalized = {t: WEIGHTS[t]/total_weight for t in available_types}

    final_score = 0.0
    for t, mean in mean_by_type.items():
        w = normalized.get(t, 0)
        final_score += mean * w

    return round(final_score, 3)

def get_performance_trend(employee_id, num_cycles=3):
    """
    Return list of {cycle_name, score, change_vs_prev} for last num_cycles (recent first).
    """
    cycles = ReviewCycle.objects.order_by('-end_date')[:50]  # limit to 50 cycles
    results = []
    prev_score = None
    count = 0
    for cycle in cycles:
        score = calculate_final_score(employee_id, cycle.id)
        if score is None:
            continue
        change = None
        if prev_score is not None:
            # improvement percent relative to prev
            if prev_score == 0:
                change = None
            else:
                change = round(((score - prev_score) / prev_score) * 100.0, 2)
        results.append({'cycle': cycle.name, 'score': score, 'change_vs_prev_pct': change})
        prev_score = score
        count += 1
        if count >= num_cycles:
            break
    # return most recent first
    return results

def identify_outliers(department):
    """
    For latest CLOSED cycle, compute department mean & std of final scores;
    return employees with |score - mean| > 1.5 * std.
    """
    latest_cycle = ReviewCycle.objects.filter(status='closed').order_by('-end_date').first()
    if not latest_cycle:
        return []

    # get employees in department
    emps = list(Employee.objects.filter(department=department, is_deleted=False))
    scores = []
    emp_score_map = {}
    for emp in emps:
        s = calculate_final_score(emp.id, latest_cycle.id)
        if s is not None:
            scores.append(s)
            emp_score_map[emp.id] = s

    n = len(scores)
    if n == 0:
        return []

    mean = sum(scores) / n
    variance = sum((x - mean) ** 2 for x in scores) / n
    std = math.sqrt(variance)

    threshold = 1.5 * std
    outliers = []
    for emp_id, s in emp_score_map.items():
        if abs(s - mean) > threshold:
            outliers.append({
                'employee_id': emp_id,
                'score': s,
                'difference': round(s - mean, 3),
                'mean': round(mean, 3),
                'std': round(std, 3),
            })
    return outliers

def calculate_goal_achievement(employee_id, cycle_id):
    """
    Returns dict with 'avg_progress' (0-100), 'completed_pct' and 'goal_count'
    """
    qs = Goal.objects.filter(employee_id=employee_id, cycle_id=cycle_id, is_deleted=False)
    total = qs.count()
    if total == 0:
        return {'avg_progress': None, 'completed_pct': None, 'goal_count': 0}
    progress_sum = sum([g.progress for g in qs])
    completed = qs.filter(status='completed').count()
    avg_progress = round(progress_sum / total, 2)
    completed_pct = round((completed / total) * 100.0, 2)
    return {'avg_progress': avg_progress, 'completed_pct': completed_pct, 'goal_count': total}
