# performance_app/tests.py
from django.test import TestCase
from .models import Employee, ReviewCycle, Review, Score, Goal
from django.contrib.auth.models import User
from .utils import calculate_final_score, get_performance_trend, identify_outliers, calculate_goal_achievement

class CoreLogicTests(TestCase):
    def setUp(self):
        # create users & employees
        u1 = User.objects.create_user(username='alice', password='pass')
        e1 = Employee.objects.create(name='Alice', email='alice@example.com', department='Eng', role='employee', user=u1)
        u2 = User.objects.create_user(username='bob', password='pass')
        e2 = Employee.objects.create(name='Bob', email='bob@example.com', department='Eng', role='manager', user=u2)
        cycle1 = ReviewCycle.objects.create(name='2024 Q1', start_date='2024-01-01', end_date='2024-03-31', status='closed')
        cycle2 = ReviewCycle.objects.create(name='2024 Q2', start_date='2024-04-01', end_date='2024-06-30', status='closed')

        # create manager review for e1 in cycle1
        r1 = Review.objects.create(employee=e1, reviewer=e2, cycle=cycle1, review_type='manager', status='submitted')
        Score.objects.create(review=r1, criteria='technical', score=8)
        Score.objects.create(review=r1, criteria='communication', score=7)
        Score.objects.create(review=r1, criteria='leadership', score=6)
        Score.objects.create(review=r1, criteria='goals', score=9)

        # self review
        r2 = Review.objects.create(employee=e1, reviewer=e1, cycle=cycle1, review_type='self', status='submitted')
        Score.objects.create(review=r2, criteria='technical', score=7)
        Score.objects.create(review=r2, criteria='communication', score=6)
        Score.objects.create(review=r2, criteria='leadership', score=7)
        Score.objects.create(review=r2, criteria='goals', score=8)

    def test_calculate_final_score(self):
        e = Employee.objects.get(email='alice@example.com')
        cycle = ReviewCycle.objects.get(name='2024 Q1')
        score = calculate_final_score(e.id, cycle.id)
        self.assertIsNotNone(score)
        # expected: manager avg = (8+7+6+9)/4 = 7.5, self avg = (7+6+7+8)/4 = 7.0
        # weights normalized: manager 0.5, self 0.3 => total 0.8 => normalized manager 0.625, self 0.375
        # final = 7.5*0.625 + 7.0*0.375 = 7.34375 -> ~7.344
        self.assertAlmostEqual(score, 7.344, places=3)

    def test_goal_achievement_empty(self):
        e = Employee.objects.get(email='alice@example.com')
        cycle = ReviewCycle.objects.get(name='2024 Q1')
        ga = calculate_goal_achievement(e.id, cycle.id)
        self.assertEqual(ga['goal_count'], 0)
