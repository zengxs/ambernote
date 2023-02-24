from allauth.account.models import EmailConfirmationHMAC
from allauth.account.views import EmailVerificationSentView
from django.shortcuts import redirect
from rest_framework import permissions, views


class AccountConfirmEmailView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, key: str):
        """
        GET method should not change state. We don't perform confirm email address here,
        just redirect to front-end page and prompt user to click a button to make a POST
        request to confirm email address.
        """
        # goto front-end (SPA) page
        return redirect(f'/auth/account-confirm-email/{key}/')

    def post(self, request, key: str):
        """
        Perform email address confirmation.
        """
        EmailConfirmationHMAC.from_key(key).confirm(request)
        return redirect('/')


class AccountEmailVerificationSentView(EmailVerificationSentView):
    pass
