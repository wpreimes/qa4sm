from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from validator.context_processors import globals_processor
from django.http import JsonResponse
from rest_framework import status
from django.conf import settings


@api_view(['GET'])
@permission_classes([AllowAny])
def global_params(request):
    data = globals_processor(request)
    data['app_version'] = settings.APP_VERSION
    # add parameters for 'Help' page
    help_context = {
        'expiry_period' : settings.VALIDATION_EXPIRY_DAYS,
        'warning_period' : settings.VALIDATION_EXPIRY_WARNING_DAYS,
        }
    data.update(help_context)

    return JsonResponse(data, status=status.HTTP_200_OK)
