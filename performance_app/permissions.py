# performance_app/permissions.py
from rest_framework.permissions import BasePermission

class IsHR(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'employee') and (request.user.employee.role == 'hr' or request.user.is_staff)

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'employee') and (request.user.employee.role == 'manager' or request.user.is_staff)

class IsOwnerOrHR(BasePermission):
    def has_object_permission(self, request, view, obj):
        # obj is Review or Employee
        user_emp = getattr(request.user, 'employee', None)
        if request.user.is_staff:
            return True
        if isinstance(obj, type) and hasattr(obj, 'employee'):
            # fallback
            pass
        # allow if the user is HR or the employee is the owner
        if user_emp and getattr(obj, 'employee', None) == user_emp:
            return True
        if user_emp and user_emp.role == 'hr':
            return True
        return False
