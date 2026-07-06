from rest_framework import serializers
from .models import (
    Student,
    FeeComponent,
    StudentFeeComponent,
    FeePayment,
    Notice,
    StudentMessage,
    Homework,
    StudentQuery,
)


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'id', 'name', 'email', 'phone', 'class_name',
            'dob', 'parent_name', 'student_id', 'password', 'created_at'
        ]
        read_only_fields = ['id', 'student_id', 'created_at']
        extra_kwargs = {
            'password': {
                'required': False,
                'allow_blank': True,
            }
        }


class StudentDetailSerializer(serializers.ModelSerializer):
    fee_components = serializers.SerializerMethodField()
    total_fees = serializers.SerializerMethodField()
    total_paid = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()
    messages = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = [
            'id', 'name', 'email', 'phone', 'class_name',
            'dob', 'parent_name', 'student_id', 'password',
            'fee_components', 'total_fees', 'total_paid', 'balance', 'messages'
        ]
        read_only_fields = ['id', 'student_id', 'password']
    
    def get_fee_components(self, obj):
        components = obj.fee_components.all()
        return StudentFeeComponentSerializer(components, many=True).data
    
    def get_total_fees(self, obj):
        return sum(float(c.amount) for c in obj.fee_components.all())
    
    def get_total_paid(self, obj):
        return sum(float(p.amount) for p in obj.payments.all())
    
    def get_balance(self, obj):
        total_fees = self.get_total_fees(obj)
        total_paid = self.get_total_paid(obj)
        return total_fees - total_paid

    def get_messages(self, obj):
        return StudentMessageSerializer(obj.messages.all(), many=True).data


class FeeComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeComponent
        fields = ['id', 'name', 'amount', 'frequency', 'created_at']
        read_only_fields = ['id', 'created_at']


class StudentFeeComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFeeComponent
        fields = ['id', 'name', 'amount', 'frequency', 'created_at']
        read_only_fields = ['id', 'created_at']


class FeePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeePayment
        fields = ['id', 'student_id', 'amount', 'date', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class StudentMessageSerializer(serializers.ModelSerializer):
    student_id = serializers.PrimaryKeyRelatedField(source='student', read_only=True)
    student_name = serializers.CharField(source='student.name', read_only=True)

    class Meta:
        model = StudentMessage
        fields = ['id', 'student_id', 'student_name', 'title', 'content', 'date', 'created_at']
        read_only_fields = ['id', 'created_at', 'student_id', 'student_name']


class StudentQuerySerializer(serializers.ModelSerializer):
    student_id = serializers.PrimaryKeyRelatedField(source='student', read_only=True)
    student_name = serializers.CharField(source='student.name', read_only=True)

    class Meta:
        model = StudentQuery
        fields = ['id', 'student_id', 'student_name', 'subject', 'message', 'reply', 'status', 'date', 'created_at']
        read_only_fields = ['id', 'created_at', 'student_id', 'student_name']


class HomeworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Homework
        fields = ['id', 'title', 'description', 'class_name', 'due_date', 'file', 'created_at']
        read_only_fields = ['id', 'created_at']


class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = ['id', 'title', 'content', 'date', 'created_at']
        read_only_fields = ['id', 'created_at']
