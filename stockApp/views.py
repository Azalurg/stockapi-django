from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from stockApp.models import CustomUser
from stockApp.serializers import UserSerializer


@csrf_exempt
def users_list(request):
    if request.method == 'GET':
        snippets = CustomUser.objects.all()
        serializer = UserSerializer(snippets, many=True)
        return JsonResponse(serializer.data, safe=False)
