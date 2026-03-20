from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login

from .serializers import (
    SendVerificationCodeSerializer,
    VerifyEmailCodeSerializer,
    SignupSerializer,
    LoginSerializer
)

from .services import (
    request_email_verification,
    verify_email_code
)

class SendEmailCodeView(APIView):

    def post(self, request):
        serializer = SendVerificationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        request_email_verification(email=email)

        return Response(
            {"message": "인증코드를 이메일로 전송했습니다."},
            status=status.HTTP_200_OK
        )

class VerifyEmailCodeView(APIView):

    def post(self, request):
        serializer = VerifyEmailCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]

        success = verify_email_code(email=email, code=code)

        if not success:
            return Response(
                {"message": "인증코드가 올바르지 않거나 만료되었습니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"message": "이메일 인증이 완료되었습니다."},
            status=status.HTTP_200_OK
        )
class SignupView(APIView):

    def post(self, request):

        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        return Response(
            {
                "message": "회원가입이 완료되었습니다.",
                "email": user.email,
                "nickname": user.nickname
            },
            status=status.HTTP_201_CREATED
        )
from rest_framework_simplejwt.tokens import RefreshToken


class LoginView(APIView):

    def post(self, request):

        serializer = LoginSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        )
