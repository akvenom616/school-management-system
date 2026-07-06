from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'students', views.StudentViewSet)
router.register(r'fee-components', views.FeeComponentViewSet)
router.register(r'fee-payments', views.FeePaymentViewSet)
router.register(r'notices', views.NoticeViewSet)
router.register(r'student-messages', views.StudentMessageViewSet)
router.register(r'student-queries', views.StudentQueryViewSet)
router.register(r'homeworks', views.HomeworkViewSet)

app_name = 'school'

urlpatterns = [
    path('', include(router.urls)),
    path('student/<int:student_id>/fee-components/', views.StudentFeeComponentViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='student-fee-components'),
    path('student/<int:student_id>/fee-components/<int:pk>/', views.StudentFeeComponentViewSet.as_view({
        'delete': 'destroy'
    }), name='student-fee-component-detail'),
]
