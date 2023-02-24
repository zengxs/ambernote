import dj_rest_auth.urls
from django.urls import include, path, re_path

from .views import AccountConfirmEmailView, AccountEmailVerificationSentView

# API endpoints: /api/authx/
urlpatterns = [
    # Registration endpoints
    path('registration/', include([
        # Override some empty TemplateView with our own view
        re_path(
            r'^account-confirm-email/(?P<key>[-:\w]+)/$',
            AccountConfirmEmailView.as_view(),
            name='account_confirm_email',
        ),
        path(
            'account-email-verification-sent/',
            AccountEmailVerificationSentView.as_view(),
            name='account_email_verification_sent',
        ),
        # Otherwise, the default registration view will be used
        path('', include('dj_rest_auth.registration.urls')),
    ])),
    # Login, logout, password reset, etc.
    path('', include([
        url
        for url in dj_rest_auth.urls.urlpatterns
        # Exclude the default user details view (read and update)
        # because we have our own view in amber.urls
        if url.name not in ['rest_user_details']
    ])),
]
