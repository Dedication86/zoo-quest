from django.db import connection
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@extend_schema(responses={200: OpenApiResponse(description="Service is healthy")}, tags=["system"])
@api_view(["GET"])
@permission_classes([AllowAny])
@throttle_classes([])
def health(request):
    """Liveness + database check. Railway and uptime monitors hit this."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db = "ok"
    except Exception:  # pragma: no cover - only fires when Postgres is down
        db = "unavailable"
    status = 200 if db == "ok" else 503
    return Response(
        {"status": "ok" if db == "ok" else "degraded", "database": db, "version": "0.1.0"}, status=status
    )
