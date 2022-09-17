from uuid import uuid4

from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.models import USERS, SESSIONS, GAMES
from api.serializers import UserSerializer


@api_view(['POST'])
def register(request):
    """ User registration api """
    try:
        username = request.POST['username']
        password = request.POST['password']

        find = USERS.find_one({'username': username})
        if find:
            return Response({'status': 'failed', 'message': 'duplicate'})

        serializer = UserSerializer(data=[{'username': username, 'password': password}], many=True)
        if serializer.is_valid():
            USERS.insert_one({'username': username, 'password': password, 'balance': 0})

            return Response({'status': 'ok', 'message': 'success'})
    except Exception:
        return Response({'status': 'failed', 'message': 'error'})


@api_view(['POST'])
def login(request):
    """ User login api """
    try:
        username = request.POST['username']
        password = request.POST['password']
        serializer = UserSerializer(data=[{'username': username, 'password': password}], many=True)
        if not serializer.is_valid:
            raise ValueError

        find = USERS.find_one({'username': username, 'password': password})
        if find:
            token = str(uuid4())
            games = [str(i['_id']) for i in GAMES.find()]
            SESSIONS.insert_one({'username': username, 'token': token, 'expired': False})
            return Response({
                'status': 'ok',
                'token': token,
                'balance': find['balance'],
                'games': games,
                'message': 'success',
            })
        else:
            return Response({'status': 'failed', 'message': 'unauthorized'})
    except Exception:
        return Response({'status': 'failed', 'message': 'error'})
