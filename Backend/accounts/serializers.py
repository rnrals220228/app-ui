from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

from .models import EmailVerification

User = get_user_model()


class SendVerificationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()

    ALLOWED_DOMAINS = ["kookmin.ac.kr"]

    def validate_email(self, value):
        email = value.lower().strip()
        domain = email.split("@")[-1]

        if domain not in self.ALLOWED_DOMAINS:
            raise serializers.ValidationError("허용된 대학 이메일이 아닙니다.")

        return email


class VerifyEmailCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6, min_length=6)

    def validate_email(self, value):
        return value.lower().strip()

    def validate_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("인증코드는 숫자 6자리여야 합니다.")
        return value


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "nickname",
            "password",
            "password_confirm",
            "profile_image_url",
        ]

    def validate_email(self, value):
        email = value.lower().strip()

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("이미 가입된 이메일입니다.")

        return email

    def validate_nickname(self, value):
        nickname = value.strip()

        if User.objects.filter(nickname=nickname).exists():
            raise serializers.ValidationError("이미 사용 중인 닉네임입니다.")

        return nickname

    def validate(self, attrs):
        password = attrs.get("password")
        password_confirm = attrs.get("password_confirm")
        email = attrs.get("email")

        if password != password_confirm:
            raise serializers.ValidationError(
                {"password_confirm": "비밀번호가 일치하지 않습니다."}
            )

        verified_record = (
            EmailVerification.objects.filter(
                email=email,
                status="VERIFIED",
            )
            .order_by("-created_at")
            .first()
        )

        if not verified_record:
            raise serializers.ValidationError(
                {"email": "이메일 인증이 완료되지 않았습니다."}
            )

        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")

        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            email=validated_data["email"],
            nickname=validated_data["nickname"],
            profile_image_url=validated_data.get("profile_image_url"),
        )

        user.email_verified = True
        user.save(update_fields=["email_verified"])

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        return value.lower().strip()

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"),
            email=email,
            password=password,
        )

        if not user:
            raise serializers.ValidationError("이메일 또는 비밀번호가 올바르지 않습니다.")

        if not user.email_verified:
            raise serializers.ValidationError("이메일 인증이 완료되지 않은 계정입니다.")

        if user.is_suspended:
            raise serializers.ValidationError("정지된 계정입니다.")

        if not user.is_active:
            raise serializers.ValidationError("비활성화된 계정입니다.")

        attrs["user"] = user
        return attrs