from django.contrib import admin
from .models import Student, FeeComponent, StudentFeeComponent, FeePayment, Notice, StudentMessage, Homework


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'student_id', 'email', 'class_name', 'phone')
    search_fields = ('name', 'student_id', 'email')
    list_filter = ('class_name', 'created_at')
    readonly_fields = ('student_id', 'created_at', 'updated_at')


@admin.register(FeeComponent)
class FeeComponentAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'frequency')
    search_fields = ('name',)
    list_filter = ('frequency',)


@admin.register(StudentFeeComponent)
class StudentFeeComponentAdmin(admin.ModelAdmin):
    list_display = ('student', 'name', 'amount', 'frequency')
    search_fields = ('student__name', 'name')
    list_filter = ('frequency',)


@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount', 'date')
    search_fields = ('student__name',)
    list_filter = ('date',)


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'date')
    search_fields = ('title', 'content')
    list_filter = ('date',)


@admin.register(StudentMessage)
class StudentMessageAdmin(admin.ModelAdmin):
    list_display = ('student', 'title', 'date')
    search_fields = ('student__name', 'title', 'content')
    list_filter = ('date', 'student__class_name')


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'class_name', 'due_date', 'file')
    search_fields = ('title', 'description', 'class_name')
    list_filter = ('class_name', 'due_date')
