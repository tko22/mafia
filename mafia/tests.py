from django.utils import timezone
from django.test import TestCase
import random

import string

from mafiaapp.models import Game,User

def randomcode():
    return ''.join(random.choice(string.lowercase) for i in range(5))


class GameModelTests(TestCase):
    code1 = randomcode()
    code2 = randomcode()

    def setUp(self):
        Game.objects.create(game_code=self.code1)
        Game.objects.create(game_code=self.code2)

    def testGameCreation(self):
        first = Game.objects.get(game_code=self.code1)
        second = Game.objects.get(game_code=self.code2)
        self.assertEqual(first.game_code, self.code1)
        self.assertEqual(second.game_code, self.code2)
        first.delete()
        second.delete()

class UserModelTests(TestCase):
    name1 = 'tim'
    name2 = 'bob'
    def setUp(self):
        User.objects.create(role=1, name=self.name1, creator=True)
        User.objects.create(name=self.name2)

    def testUserCreation(self):
        first = User.objects.get(name=self.name1)
        second = User.objects.get(name=self.name2)
        self.assertEqual(first.name, self.name1)
        self.assertEqual(second.role, 0) #default should be 0
        first.delete()
        second.delete()


class GameAndUserTest(TestCase):
    code1 = randomcode()
    name1 = 'tim1'
    def setUp(self):
        game = Game.objects.create(game_code=self.code1)
        game.user_set.create(role=0, name=self.name1, creator=True)
        game.user_set.create(name=self.name2, creator=False)
        game.save()
    def check(self):
        game = Game.objects.get(game_code=self.code1)
        user_set = game.user_set.all()
        self.assertEqual(user_set[0], self.name1)
        self.assertEqual(user_set[1].game_id.game_code, self.code1 )
        self.assertEqual(game.in_game, False)