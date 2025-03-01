from django.http import JsonResponse



def index(request):
    data = {
		"message": "Hi. It's JSON!",
		"status": "200",
	}
    return JsonResponse(data)
