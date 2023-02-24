"""
AmberNote views for serving the SPA files and API documentation.
"""

from django.conf import settings
from django.http import FileResponse, HttpResponse
from django.utils.http import http_date
from django.views.decorators.http import require_http_methods
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

# swagger schema view
schema_view = get_schema_view(
    openapi.Info(
        title='AmberNote API',
        default_version='v1',
        description='AmberNote API',
        license=openapi.License(
            'AGPL-3.0 License',
            'https://www.gnu.org/licenses/agpl-3.0.en.html',
        ),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


@require_http_methods(['GET', 'HEAD'])
def spa_files_view(request, path: str):
    """
    Serves the SPA files.
    """
    # serve static files
    filepath = settings.SPA_ROOT / path
    if not filepath.is_file():
        filepath = settings.SPA_ROOT / 'index.html'

        if settings.DEBUG:
            # use HttpResponse to serve the index.html file in debug mode
            # so that debug-toolbar can be injected.
            return HttpResponse(content_type='text/html', content=filepath.read_text())

    response = FileResponse(filepath.open('rb'), as_attachment=False)

    filestat = filepath.stat()
    # get last modified timestamp from file
    last_modified = int(filestat.st_mtime)
    # set Last-Modified header
    response['Last-Modified'] = http_date(last_modified)
    response['ETag'] = f'"{last_modified:x}-{filestat.st_size:x}"'

    if settings.DEBUG:
        response['Cache-Control'] = 'no-cache,no-store,public'  # disable caching in debug mode
    else:
        response['Cache-Control'] = 'max-age=7200,public'  # cache for 2 hours

    return response
