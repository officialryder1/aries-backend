# django util
from django.http import JsonResponse  # noqa: F401
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.db.models import Q

# third parties
from .pusher import pusher_client
# models
from ..models import Note, Character, Player, Player_rank, Card, Rarity, Match, MatchResult, PlayerCard, MatchRequest  # noqa: F401
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
def requestMatch(request):
    user = request.GET.get('user_id')
    user_id = User.objects.get(pk=user)
    match_request = MatchRequest.objects.create(requester=user_id)

    match_request.save()
    pusher_client.trigger('match-channel', 'new-match', {
        'requester_name': match_request.requester.username,
        'match_request_id': match_request.id
    })
    return Response({"message": "Searching for a match..."})

@api_view(['POST', 'GET'])
def FindMatch(request):
    user = request.GET.get('user_id')

    
    match_request = MatchRequest.objects.filter(status='pending').exclude(requestee=user)
    serializer = MatchRequestSerializer(match_request, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
def AcceptMatch(request, pk):    
        user_id = request.GET.get('user_id')

        # Validate and retrieve the player
        try:
            player = Player.objects.get(user=user_id)
        except Player.DoesNotExist:
            return Response({"error": "Player not found"}, status=status.HTTP_404_NOT_FOUND)
        
        #Match event creation
    
        try:
            match_request = MatchRequest.objects.get(pk=pk, status="pending")
        except MatchRequest.DoesNotExist:
            return Response({"error": "Match request not found or already accepted"}, status=status.HTTP_404_NOT_FOUND)
        
        match_request.requestee = player.user

        match_request.status = "accepted"
        match_request.save()

        match = Match.objects.create(player_one=match_request.requester, player_two=player.user)

        pusher_client.trigger('match-channel', 'match-accepted', {
            'message': f'User {user_id} has accepted the match!',
            'match_id': match.id,
            'redirect_url': f'/game/{match.id}'
        })
        # Create the match instance
        match_url = reverse('matchDetail', kwargs={'pk': match.id})
       
        return Response({"message": "Match accepted", "redirect_url": match_url}, status=status.HTTP_200_OK)
       
@api_view(['GET'])
def matchDetail(request, pk):
    match = get_object_or_404(Match, pk=pk)
    
    serializer = MatchSerializer(match)

    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def match_status(request):
    user_id = request.GET.get('user_id')

    # Validate and retrieve the player
    try:
        player = Player.objects.get(user=user_id)
    except Player.DoesNotExist:
        return Response({"error": "Player not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Retrieve the match where the player is involved
    match = Match.objects.filter(player_one=player.user).first() or Match.objects.filter(player_two=player.user).first()

    if not match:
        return Response({"status": "No match found"}, status=status.HTTP_200_OK)

    # Serialize the match details
    serializer = MatchSerializer(match)
    return Response({"status": match.status, "match": serializer.data}, status=status.HTTP_200_OK)

@api_view(['GET'])
def pending_matches(request):
    user_id = request.GET.get('user_id')

    # Validate and retrieve the player
    try:
        player = Player.objects.get(user=user_id)
    except Player.DoesNotExist:
        return Response({"error": "Player not found"}, status=status.HTTP_404_NOT_FOUND)

    # Find all pending matches for this player
    pending_matches = Match.objects.filter(
        (Q(player_one=player.user) | Q(player_two=player.user)),
        status="waiting"
    )

    if not pending_matches.exists():
        return Response({"status": "No pending matches found"}, status=status.HTTP_200_OK)

    # Serialize the pending matches
    serializer = MatchSerializer(pending_matches, many=True)
    return Response({"pending_matches": serializer.data}, status=status.HTTP_200_OK)