# django util
from django.http import JsonResponse  # noqa: F401
from django.contrib.auth.models import User

# models
from ..models import Note, Character, Player, Player_rank, Card, Rarity, Match, MatchResult, PlayerCard, MatchRequest
from .serializers import UserSerializer, RegisterSerializer, NoteSerializer, CardSerializer, CharacterSerializer, PlayerSerializer, MatchSerializer, MatchResultSerializer, PlayerCardSerializer, MatchRequestSerializer

# restFrameWork 
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.http import require_GET


@api_view(['GET'])
def getRoutes(request):
    routes = [
        '/api/token',
        '/api/token/refresh'
        '/api/register',
        '/api/notes',
        '/api/create_note',
        '/api/user/${int}',
        '/api/delete/${int}'
    ]
    return Response(routes)

    

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        # ...

        return token
    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer



@require_GET
def check_user_exists(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'User ID is required'}, status=400)

    try:
        user = User.objects.get(pk=user_id)
        return JsonResponse({'exists': True})
    except User.DoesNotExist:
        return JsonResponse({'exists': False})
    

@api_view(['GET'])
def getUser(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getNote(request):
    user = request.user
    notes = user.note_set.all()
    serializer = NoteSerializer(notes, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_note(request):
    serializer = NoteSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['PUT', 'DELETE'])
def delete_note(request, pk):
    try:
        note = Note.objects.get(pk=pk)
    except Note.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    note.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(["POST"])
# @permission_classes([IsAuthenticated])
def create_avatar(request):
    serializer = PlayerSerializer(data=request.data)
    # user = request.user
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'GET'])
def character(request):
    if request.method == 'GET':
        character = Character.objects.all()
        serializer = CharacterSerializer(character, many=True)
        return Response(serializer.data)

@api_view(['POST', 'GET'])
def card(request):
    if request.method == 'GET':
        card = Card.objects.all()
        serializer = CardSerializer(card, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        serializer = CardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


@api_view(['GET'])
def get_player(request):
    user_id = request.GET.get('user_id')  # Use 'user_id' to get the user ID from query parameters

    if not user_id:
        return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(pk=user_id)  # Fetch the user object by ID
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    players = Player.objects.filter(user=user)  # Filter players by the user
    serializer = PlayerSerializer(players, many=True)


    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_card(request, pk ):
    try:
        card = Card.objects.get(pk=pk)
        serializer = CardSerializer(card)
        return Response(serializer.data)
    except Card.DoesNotExist:
        return Response({'error': "Card not found"}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
def update_player_card(request):
    user = request.GET.get('user_id')
    try:
        player = Player.objects.get(user=user)
    except Player.DoesNotExist:
        return Response({"error": "Player not found"}, status=status.HTTP_404_NOT_FOUND)
    
    cards = request.data.get('card', [])
    if not cards:
        return Response({"error": "No cards provided"}, status=status.HTTP_400_BAD_REQUEST)
    
    card_objects = Card.objects.filter(id__in=cards)
    player.card.set(card_objects)
    player.save()

    serializer = PlayerSerializer(player)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_character(request, pk):
    try:
        character = Character.objects.get(pk=pk)
        serializer = CharacterSerializer(character)
        return Response(serializer.data)
    except Character.DoesNotExist:
        return Response({"error": "Character not found"}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET', 'POST'])
def match(request):
    if request.method == 'GET':
        match = Match.objects.all()
        serializer = MatchSerializer(match, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        pass

@api_view(['GET', 'POST'])
def findMatch(request):
    user = request.GET.get('user_id')
    user_id = User.objects.get(pk=user)
    match_request = MatchRequest.objects.create(requester=user_id)
    match_request.save()
    return Response({"message": "Match request created, waiting for a match"})

@api_view(['POST'])
def UpdateMatch(request):
    user = request.GET.get('user_id')
    
    try:
       match = MatchRequest.objects.get(requester=user)
    except Match.DoesNotExist:
        return Response({"error": "Match not found"}, status=status.HTTP_400_BAD_REQUEST)
     