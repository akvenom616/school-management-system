from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
from django.core.cache import cache
from django.shortcuts import get_object_or_404
import hashlib
import secrets

from .models import (
    Student,
    FeeComponent,
    StudentFeeComponent,
    FeePayment,
    Notice,
    StudentMessage,
    Homework,
    StudentQuery,
    generate_random_password,
)
from .serializers import (
    StudentSerializer,
    StudentDetailSerializer,
    FeeComponentSerializer,
    StudentFeeComponentSerializer,
    FeePaymentSerializer,
    NoticeSerializer,
    StudentMessageSerializer,
    HomeworkSerializer,
    StudentQuerySerializer,
)


def _attempt_key(student_id):
    return f"student_login_attempts:{student_id}"


def _lock_key(student_id):
    return f"student_login_lock:{student_id}"


def _is_login_locked(student_id):
    lock_until = cache.get(_lock_key(student_id))
    if not lock_until:
        return False
    return lock_until > __import__('time').time()


def _record_failed_login(student_id):
    attempts = cache.get(_attempt_key(student_id), 0) + 1
    cache.set(_attempt_key(student_id), attempts, timeout=15 * 60)

    if attempts >= settings.LOGIN_ATTEMPT_LIMIT:
        lockout_seconds = settings.LOGIN_ATTEMPT_LOCKOUT_MINUTES * 60
        cache.set(_lock_key(student_id), __import__('time').time() + lockout_seconds, timeout=lockout_seconds)


def _clear_login_state(student_id):
    cache.delete(_attempt_key(student_id))
    cache.delete(_lock_key(student_id))


class StudentViewSet(viewsets.ModelViewSet):
    """API endpoint for students."""
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return StudentDetailSerializer
        return StudentSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new student with auto-generated credentials."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Generate student ID and password
        student_id = f"STU{secrets.randbelow(100000):05d}"
        password = request.data.get('password') or generate_random_password(12)
        
        student = serializer.save(student_id=student_id, password=password)
        
        response_data = serializer.data
        response_data['password'] = password
        response_data['student_id'] = student_id
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Update student information (password excluded from update)."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Allow password update through normal update (admin-chosen passwords)
        data = request.data.copy()
        
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """Reset student password."""
        student = self.get_object()
        new_password = generate_random_password(12)
        student.password = new_password
        student.save()
        
        return Response({
            'message': 'Password reset successfully',
            'password': new_password
        })
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """Student login endpoint."""
        student_id = request.data.get('student_id')
        password = request.data.get('password')

        if not student_id or not password:
            return Response(
                {'error': 'student_id and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if _is_login_locked(student_id):
            return Response(
                {
                    'error': (
                        'Account temporarily locked due to repeated failed login attempts. '
                        f'Try again in {settings.LOGIN_ATTEMPT_LOCKOUT_MINUTES} minutes.'
                    )
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        try:
            student = Student.objects.get(student_id=student_id)
        except Student.DoesNotExist:
            _record_failed_login(student_id)
            return Response(
                {'error': 'Invalid student ID or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if student.password != password:
            _record_failed_login(student_id)
            return Response(
                {'error': 'Invalid student ID or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        _clear_login_state(student_id)
        serializer = StudentDetailSerializer(student)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def dashboard(self, request, pk=None):
        """Get student dashboard data."""
        student = self.get_object()
        serializer = StudentDetailSerializer(student)
        return Response(serializer.data)


class FeeComponentViewSet(viewsets.ModelViewSet):
    """API endpoint for global fee components."""
    queryset = FeeComponent.objects.all()
    serializer_class = FeeComponentSerializer


class StudentFeeComponentViewSet(viewsets.ModelViewSet):
    """API endpoint for student-specific fee components."""
    serializer_class = StudentFeeComponentSerializer
    
    def get_queryset(self):
        student_id = self.kwargs.get('student_id')
        return StudentFeeComponent.objects.filter(student_id=student_id)
    
    def create(self, request, *args, **kwargs):
        """Add a fee component to a student."""
        student_id = self.kwargs.get('student_id')
        student = get_object_or_404(Student, id=student_id)
        
        fee_component_id = request.data.get('fee_component_id')
        if fee_component_id:
            fee_component = get_object_or_404(FeeComponent, id=fee_component_id)
            student_fee = StudentFeeComponent.objects.create(
                student=student,
                name=fee_component.name,
                amount=fee_component.amount,
                frequency=fee_component.frequency
            )
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            student_fee = serializer.save(student=student)
        
        serializer = self.get_serializer(student_fee)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, *args, **kwargs):
        """Remove a fee component from a student."""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FeePaymentViewSet(viewsets.ModelViewSet):
    """API endpoint for fee payments."""
    queryset = FeePayment.objects.all()
    serializer_class = FeePaymentSerializer
    
    def get_queryset(self):
        student_id = self.request.query_params.get('student_id')
        if student_id:
            return FeePayment.objects.filter(student_id=student_id)
        return FeePayment.objects.all()
    
    def create(self, request, *args, **kwargs):
        """Record a new fee payment."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def student_payments(self, request):
        """Get payment history for a student."""
        student_id = request.query_params.get('student_id')
        if not student_id:
            return Response(
                {'error': 'student_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payments = FeePayment.objects.filter(student_id=student_id)
        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)


class StudentQueryViewSet(viewsets.ModelViewSet):
    """API endpoint for student queries shared between students and admin."""
    queryset = StudentQuery.objects.all()
    serializer_class = StudentQuerySerializer

    def get_queryset(self):
        student_id = self.request.query_params.get('student_id')
        if student_id:
            return StudentQuery.objects.filter(student_id=student_id)
        return StudentQuery.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student_id = request.data.get('student_id')
        student = get_object_or_404(Student, id=student_id)
        serializer.save(student=student, status='Pending')
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class HomeworkViewSet(viewsets.ModelViewSet):
    """API endpoint for homework uploads visible to students by class."""
    queryset = Homework.objects.all()
    serializer_class = HomeworkSerializer

    def get_queryset(self):
        class_name = self.request.query_params.get('class_name')
        queryset = Homework.objects.all()
        if class_name:
            queryset = queryset.filter(class_name__iexact=class_name)
        return queryset.order_by('-due_date', '-created_at')


class NoticeViewSet(viewsets.ModelViewSet):
    """API endpoint for notices."""
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest notices."""
        limit = request.query_params.get('limit', 5)
        notices = Notice.objects.all()[:int(limit)]
        serializer = self.get_serializer(notices, many=True)
        return Response(serializer.data)


class StudentMessageViewSet(viewsets.ModelViewSet):
    """API endpoint for student-specific messages."""
    queryset = StudentMessage.objects.all()
    serializer_class = StudentMessageSerializer

    def get_queryset(self):
        student_id = self.request.query_params.get('student_id')
        if student_id:
            return StudentMessage.objects.filter(student_id=student_id)
        return StudentMessage.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student_id = request.data.get('student_id')
        student = get_object_or_404(Student, id=student_id)
        serializer.save(student=student)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
