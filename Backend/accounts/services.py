import random
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.hashers import check_password, make_password

from .models import EmailVerification


VERIFICATION_CODE_EXPIRE_MINUTES = 10


def generate_verification_code() -> str:
    """
    6자리 숫자 인증코드 생성
    """
    return f"{random.randint(0, 999999):06d}"


def create_email_verification(email: str, user=None) -> tuple[EmailVerification, str]:
    """
    이메일 인증 레코드 생성 + 원본 코드 반환
    DB에는 해시만 저장하고, 원본 코드는 메일 발송에만 사용
    """
    raw_code = generate_verification_code()
    code_hash = make_password(raw_code)

    expires_at = timezone.now() + timedelta(minutes=VERIFICATION_CODE_EXPIRE_MINUTES)

    verification = EmailVerification.objects.create(
        user=user,
        email=email,
        code_hash=code_hash,
        status="PENDING",
        expires_at=expires_at,
    )

    return verification, raw_code


def expire_previous_pending_verifications(email: str) -> None:
    """
    기존 미인증 코드들을 만료 처리
    """
    EmailVerification.objects.filter(
        email=email,
        status="PENDING",
    ).update(status="EXPIRED")


def send_verification_email(email: str, code: str) -> None:
    """
    실제 메일 발송
    settings.py에 EMAIL_BACKEND, EMAIL_HOST_USER 등 설정 필요
    """
    subject = "[서비스명] 이메일 인증코드 안내"
    message = (
        f"안녕하세요.\n\n"
        f"이메일 인증코드는 {code} 입니다.\n"
        f"{VERIFICATION_CODE_EXPIRE_MINUTES}분 안에 입력해주세요."
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        recipient_list=[email],
        fail_silently=False,
    )


@transaction.atomic
def request_email_verification(email: str, user=None) -> EmailVerification:
    """
    인증코드 발급 전체 흐름
    1) 이전 pending 만료
    2) 새 인증코드 생성
    3) 메일 발송
    """
    expire_previous_pending_verifications(email)
    verification, raw_code = create_email_verification(email=email, user=user)
    send_verification_email(email=email, code=raw_code)
    return verification


@transaction.atomic
def verify_email_code(email: str, code: str) -> bool:
    """
    사용자가 입력한 인증코드 검증
    성공하면 최신 PENDING 레코드를 VERIFIED로 변경
    """
    verification = (
        EmailVerification.objects.filter(
            email=email,
            status="PENDING",
        )
        .order_by("-created_at")
        .first()
    )

    if verification is None:
        return False

    now = timezone.now()
    if verification.expires_at < now:
        verification.status = "EXPIRED"
        verification.save(update_fields=["status"])
        return False

    if not check_password(code, verification.code_hash):
        return False

    verification.status = "VERIFIED"
    verification.verified_at = now
    verification.save(update_fields=["status", "verified_at"])
    return True