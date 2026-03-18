# Backend/pulmonary_app/views.py
import os
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage

@csrf_exempt
def upload_test_file(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return JsonResponse({'error': 'No file provided'}, status=400)

        file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
        with default_storage.open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        return JsonResponse({'message': 'Upload successful', 'filename': uploaded_file.name})
    return JsonResponse({'error': 'Invalid request method'}, status=405)
