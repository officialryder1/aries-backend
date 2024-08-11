from django.contrib import admin

# Register your models here.
from .models import  Note, Player_rank, Player, Rarity, Card, Character, Match, PlayerCard, MatchResult, MatchRequest


admin.site.register(Note)

admin.site.register(Player_rank)
admin.site.register(Player)
admin.site.register(Rarity)
admin.site.register(Card)
admin.site.register(Character)
admin.site.register(Match)
admin.site.register(MatchResult)
admin.site.register(PlayerCard)
admin.site.register(MatchRequest)