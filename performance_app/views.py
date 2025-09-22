# performance_app/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import ReviewSerializer, EmployeeSerializer, GoalSerializer
from .models import Review, Employee, Goal, ReviewCycle
from .utils import calculate_final_score, get_performance_trend, calculate_goal_achievement, identify_outliers
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.parsers import MultiPartParser, JSONParser
import csv, io
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.utils import timezone

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user_id': user.id})
        return Response({'detail':'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    def post(self, request):
        user = request.user
        if hasattr(user, 'auth_token'):
            user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ReviewCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request):
        """
        POST /reviews
        expected body: employee, reviewer, cycle, review_type, scores: [{criteria,score,comments},...]
        """
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            # Prevent duplicate self-review / duplicates handled by unique_together in model
            try:
                review = serializer.save()
            except Exception as e:
                return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReviewSubmitView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, pk):
        review = get_object_or_404(Review, pk=pk, is_deleted=False)
        # simple permission: only reviewer or HR can submit
        user_emp = getattr(request.user, 'employee', None)
        if not request.user.is_staff and (user_emp is None or review.reviewer_id != user_emp.id) and (not (user_emp and user_emp.role=='hr')):
            return Response({'detail':'Not allowed'}, status=status.HTTP_403_FORBIDDEN)
        with transaction.atomic():
            # reload for update
            rev = Review.objects.select_for_update().get(pk=review.pk)
            rev.status = 'submitted'
            rev.submitted_date = timezone.now()
            rev.save()
        return Response({'detail':'submitted'}, status=status.HTTP_200_OK)

class ReviewDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, pk):
        review = get_object_or_404(Review, pk=pk, is_deleted=False)
        return Response(ReviewSerializer(review).data)

class EmployeeReviewsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, id):
        emp = get_object_or_404(Employee, pk=id, is_deleted=False)
        qs = emp.reviews.filter(is_deleted=False).select_related('cycle','reviewer').prefetch_related('scores')
        data = ReviewSerializer(qs, many=True).data
        return Response(data)

class PerformanceTrendView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, id):
        result = get_performance_trend(id, num_cycles=3)
        return Response(result)

class EmployeeGoalsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, id):
        emp = get_object_or_404(Employee, pk=id, is_deleted=False)
        qs = Goal.objects.filter(employee=emp, is_deleted=False)
        return Response(GoalSerializer(qs, many=True).data)

class DepartmentSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, dept):
        # compute average final score for latest closed cycle
        latest = ReviewCycle.objects.filter(status='closed').order_by('-end_date').first()
        if not latest:
            return Response({'detail':'no closed cycles'}, status=status.HTTP_400_BAD_REQUEST)
        emps = Employee.objects.filter(department=dept, is_deleted=False)
        items = []
        for e in emps:
            score = calculate_final_score(e.id, latest.id)
            items.append({'employee_id': e.id, 'name': e.name, 'score': score})
        # compute summary
        scores = [i['score'] for i in items if i['score'] is not None]
        avg = sum(scores)/len(scores) if scores else None
        top_performers = sorted([i for i in items if i['score'] is not None], key=lambda x: -x['score'])[:10]
        return Response({'cycle': latest.name, 'average_score': avg, 'top_performers': top_performers})
from rest_framework.parsers import MultiPartParser, JSONParser
import csv, io

class BulkImportReviewsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, JSONParser]

    def post(self, request):
        created = []
        criteria_map = {
            "technical": "technical",
            "communication": "communication",
            "leadership": "leadership",
            "goals": "goals",
            "technical skills": "technical",
            "goal achievement": "goals"
        }

        # --- Handle CSV ---
        if "file" in request.FILES:
            f = request.FILES["file"]
            data = f.read().decode("utf-8")
            reader = csv.DictReader(io.StringIO(data))

            for row in reader:
                try:
                    emp = Employee.objects.get(email=row["employee_email"])
                    rev = Employee.objects.get(email=row["reviewer_email"])
                    cycle = ReviewCycle.objects.get(name=row["cycle_name"])
                    
                    review, _ = Review.objects.get_or_create(
                        employee=emp,
                        reviewer=rev,
                        cycle=cycle,
                        review_type=row["review_type"]
                    )

                    for c in ("technical", "communication", "leadership", "goals"):
                        Score.objects.update_or_create(
                            review=review,
                            criteria=c,
                            defaults={
                                "score": int(row[c]),
                                "comments": row.get("comments", "")
                            }
                        )
                    created.append(review.id)

                except Exception as e:
                    print("CSV import error:", str(e))
                    continue

            return Response({"created": created}, status=status.HTTP_201_CREATED)

        # --- Handle JSON ---
        payload = request.data if isinstance(request.data, list) else request.data.get("reviews", [])
        for item in payload:
            try:
                emp = Employee.objects.get(email=item["employee_email"])
                rev = Employee.objects.get(email=item["reviewer_email"])
                cycle = ReviewCycle.objects.get(name=item["cycle_name"])

                review, _ = Review.objects.get_or_create(
                    employee=emp,
                    reviewer=rev,
                    cycle=cycle,
                    review_type=item["review_type"]
                )

                for s in item.get("scores", []):
                    crit = criteria_map.get(s["criteria"].lower(), None)
                    if not crit:
                        continue
                    Score.objects.update_or_create(
                        review=review,
                        criteria=crit,
                        defaults={
                            "score": int(s["score"]),
                            "comments": s.get("comments", "")
                        }
                    )
                created.append(review.id)

            except Exception as e:
                print("JSON import error:", str(e))
                continue

        return Response({"created": created}, status=status.HTTP_201_CREATED)
