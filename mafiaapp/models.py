# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Game(models.Model):
    in_game = models.BooleanField(default=False)
    game_code = models.CharField(max_length=5)
    add_vampire = models.BooleanField(default=False)
    add_cop = models.BooleanField(default=False)
    round_num = models.IntegerField(default=1)
    round_length = models.IntegerField(default=2)
    mafia_num = models.IntegerField(default=1)
    narrator_name = models.CharField(max_length=20)

    def __str__(self):
        return self.game_code


class User(models.Model):
    game_id = models.ForeignKey(Game, on_delete=models.CASCADE)
    # 0 - no role, 1- narrator, 2 - mafia, 3 - citizens, 4 - healer, 5 -vampire, 6 -cop
    role = models.IntegerField(default=0)
    name = models.CharField(max_length=10)
    creator = models.BooleanField(default=False)
    in_game = models.BooleanField(default=False)
    narrator = models.BooleanField(default=False)
    vampire = models.BooleanField(default=False)
    cop = models.BooleanField(default=False)

    def __str__(self):
        return self.name