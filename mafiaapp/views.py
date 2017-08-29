# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.shortcuts import render

from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.http import JsonResponse
from django.core import exceptions

import random, string

from .models import Game, User

# 0 - no role, 1- narrator, 2 - mafia, 3 - citizens, 4 - healer, 5 -vampire, 6 -cop
roles = {0: "no role",
         1: "narrator",
         2: "mafia",
         3: "citizen",
         4: "healer",
         5: "vampire",
         6: "cop",
         }


def index(request):
    return render(request, 'mafiaapp/index.html')


# /game_id/
def lobby(request, game_id):
    game = get_object_or_404(Game, game_code=game_id)
    user_list = game.user_set.all()
    if 'user' in request.session:
        username = request.session['user']
        if user_list.filter(name=username).exists():
            user = user_list.get(name=username)
        else:
            return HttpResponse("Please create a user first")
    else:
        return HttpResponse("Please create a user first")
    userlist_nomainusr = user_list.exclude(name=user.name)
    return render(request, 'mafiaapp/lobby.html', {
        'game': game,
        'user': user,
        'userlist_nomainusr': userlist_nomainusr
    })


# /game_id/game
def ingame(request, game_id):
    game = get_object_or_404(Game, game_code=game_id)
    user_list = game.user_set.all()
    # check if game is in session
    if game.in_game:
        if 'user' in request.session:
            username = request.session['user']
            if (user_list.get(name=username)):
                user = user_list.get(name=username)
                if user.in_game == False:
                    return HttpResponse("Please wait until next game to join")
        else:
            return HttpResponse("Please create a user first")
        user_roles = {}
        for usr in user_list:
            user_roles[usr.name] = roles[usr.role]
        role = roles[user.role]
        print user_roles
        return render(request, 'mafiaapp/ingame.html', {
            'game': game,
            'user': user,
            'role': role,
            'narrator': game.narrator_name,
            'user_roles': user_roles,
        })
    else:
        redirect(lobby(game_id))


# /api/creategame
# creates game object and creator user in database
def createlobby(request):
    ret = {'status': 'success'}
    if request.method == 'POST':
        data = request.body
        jsondata = json.loads(data)
        name = jsondata['name']
        if len(name) > 10:
            ret['status'] = 'failed'
            ret['message'] = 'Name must be less than 10 characters'
            return JsonResponse(ret)
        game_code = randomcode()
        game = Game(game_code=game_code)
        game.save()
        user = game.user_set.create(role=0, name=name, creator=True)
        user.save()
        ret.update({'gamecode': game_code, 'name': name, 'creator': True})
        request.session['user'] = name
        return JsonResponse(ret)
    else:
        ret['status'] = 'failed'
        return JsonResponse(ret)


# /api/joingame
def joinlobby(request):
    ret = {'status': 'success'}
    if request.method == 'POST':
        data = request.body
        jsondata = json.loads(data)
        name = jsondata['name']
        if len(name) > 10:
            ret['status'] = 'failed'
            ret['message'] = 'Name must be less than 10 characters'
            return JsonResponse(ret)
        if (jsondata.get('code')):
            code = jsondata['code'].lower()
            try:
                if (Game.objects.get(game_code=code)):
                    game = Game.objects.get(game_code=code)
            except Exception:
                ret['status'] = 'failed'
                ret['message'] = 'Game Code not Valid'
                return JsonResponse(ret)
            try:
                if (game.user_set.get(name=name)):
                    ret['status'] = 'failed'
                    ret['message'] = 'Name taken'
                    return JsonResponse(ret)
            except Exception:
                user = game.user_set.create(role=0, name=name, creator=False)
                user.save()
            ret.update({'gamecode': code, 'name': name, 'creator': False})
            request.session['user'] = name
            return JsonResponse(ret)
        else:
            ret['status'] = 'failed'
            ret['message'] = 'code doesnt exist'
            return JsonResponse(ret)
    else:
        ret['status'] = 'failed'
        ret['message'] = 'not POST'
        return JsonResponse(ret)


def removeuser(request):
    ret = {'status': 'success'}
    if request.method == 'POST':
        data = request.body
        jsondata = json.loads(data)
        name = jsondata['name']
        code = jsondata['code']
        try:
            if (Game.objects.get(game_code=code)):
                game = Game.objects.get(game_code=code)
        except Exception:
            ret = returnfail(ret, 'Game Code not Valid')
            return JsonResponse(ret)
        try:
            if (game.user_set.get(name=name)):
                user = game.user_set.get(name=name)
                user.delete()
        except Exception:
            ret = returnfail(ret, 'Cannot get User')
            return JsonResponse(ret)
        game.save()
        return JsonResponse(ret)
    else:
        ret = returnfail(ret, 'not POST')
        return JsonResponse(ret)


def startgame(request):
    ret = {'status': 'success'}
    if request.method == 'POST':
        data = request.body
        jsondata = json.loads(data)

        # get configurations
        name = jsondata.get('name')
        code = jsondata.get('code')
        vampire = jsondata.get('vampire')
        time = jsondata.get('time')
        cop = jsondata.get('cop')
        narrator_name = jsondata.get('narrator')
        game = Game.objects.get(game_code=code)
        user_list = game.user_set.all()

        # check if user that started game is the creator
        if 'user' in request.session:
            username = request.session['user']
            user = user_list.get(name=username)
            if user.creator == False:
                ret = returnfail(ret, 'User that created the game must start the game')
        else:
            ret = returnfail(ret, 'create user')
            return JsonResponse(ret)

        # put config in database
        game.add_vampire = vampire
        game.add_cop = cop
        game.round_length = time  # add roundtime to database
        game.round_num = 0
        game.narrator_name = narrator_name
        game.save()
        # assign user roles
        narrator = user_list.get(name=narrator_name)
        narrator.role = 1
        narrator.save()
        i = 0
        vampire_index = 0
        cop_index = 0
        # one mafia
        mafia_index = random.randint(0, len(user_list) - 1)
        healer_index = random.randint(0, len(user_list) - 1)
        while (healer_index) == mafia_index: healer_index = random.randint(0, len(user_list) - 1)
        if user_list.count() < 5:
            ret['status'] = 'failed'
            ret['message'] = 'you need more players'
            return JsonResponse(ret)
        # one mafia
        if user_list.count() < 6:
            if vampire == True:
                print "vampire is true"
                vampire_index = random.randint(0, len(user_list) - 1)
                while (vampire_index == mafia_index or vampire_index == healer_index):
                    vampire_index = random.randint(0, len(user_list) - 1)
            if cop == True:
                print "cop is true"
                cop_index = random.randint(0, len(user_list) - 1)
                while cop_index == mafia_index or cop_index == vampire_index or cop_index == healer_index:
                    cop_index = random.randint(0, len(user_list) - 1)
            for usr in user_list:
                if (usr.name != narrator_name):
                    if i == mafia_index:
                        usr.role = 2
                        usr.save()
                    elif i == healer_index:
                        usr.role = 4
                        usr.save()
                    elif cop == True and i == cop_index:
                        usr.role = 6
                        usr.save()
                    elif vampire == True and i == vampire_index:
                        usr.role = 5
                        usr.save()
                    else:
                        usr.role = 3
                        usr.save()
                    i = i + 1
        # 2 mafia
        elif user_list.count() < 10:
            game.mafia_num = 2
            if vampire == True:
                print "vampire is true"
                vampire_index = random.randint(0, len(user_list) - 1)
                while (vampire_index == mafia_index or vampire_index == healer_index):
                    vampire_index = random.randint(0, len(user_list) - 1)
            if cop == True:
                print "cop is true"
                cop_index = random.randint(0, len(user_list) - 1)
                while cop_index == mafia_index or cop_index == vampire_index or cop_index == healer_index:
                    cop_index = random.randint(0, len(user_list) - 1)
            mafia_index_2 = random.randint(0, len(user_list) - 1)
            while mafia_index_2 == mafia_index or mafia_index_2 == vampire_index or mafia_index_2 == cop_index or mafia_index_2 == healer_index:
                mafia_index_2 = random.randint(0, len(user_list) - 1)
            for usr in user_list:
                if (usr.name != narrator_name):
                    if i == mafia_index or i == mafia_index_2:
                        usr.role = 2
                        usr.save()
                    elif i == healer_index:
                        usr.role = 4
                        usr.save()
                    elif cop == True and i == cop_index:
                        usr.role = 6
                        usr.save()
                    elif vampire == True and i == vampire_index:
                        usr.role = 5
                        usr.save()
                    else:
                        usr.role = 3
                        usr.save()
                    i = i + 1

        # 3 mafia
        else:
            game.mafia_num = 3
            if vampire == True:
                print "vampire is true"
                vampire_index = random.randint(0, len(user_list) - 1)
                while (vampire_index == mafia_index or vampire_index == healer_index):
                    vampire_index = random.randint(0, len(user_list) - 1)
            if cop == True:
                print "cop is true"
                cop_index = random.randint(0, len(user_list) - 1)
                while cop_index == mafia_index or cop_index == vampire_index or cop_index == healer_index:
                    cop_index = random.randint(0, len(user_list) - 1)
            mafia_index_2 = random.randint(0, len(user_list) - 1)
            while mafia_index_2 == mafia_index or mafia_index_2 == vampire_index or mafia_index_2 == cop_index \
                    or mafia_index_2 == healer_index:
                mafia_index_2 = random.randint(0, len(user_list) - 1)
            mafia_index_3 = random.randint(0, len(user_list) - 1)
            while mafia_index_3 == mafia_index or mafia_index_3 == vampire_index or mafia_index_3 == cop_index \
                    or mafia_index_3 == healer_index or mafia_index_3 == mafia_index_2:
                mafia_index_3 = random.randint(0, len(user_list) - 1)
            for usr in user_list:
                if (usr.name != narrator_name):
                    if i == mafia_index or i == mafia_index_2 or i == mafia_index_3:
                        usr.role = 2
                        usr.save()
                    elif i == healer_index:
                        usr.role = 4
                        usr.save()
                    elif cop == True and i == cop_index:
                        usr.role = 6
                        usr.save()
                    elif vampire == True and i == vampire_index:
                        usr.role = 5
                        usr.save()
                    else:
                        usr.role = 3
                        usr.save()
                    i = i + 1
        # set all users in session
        for usr in user_list:
            usr.in_game = True
            usr.save()
        # set game in session
        game.in_game = True
        game.save()

        ret['code'] = code
        return JsonResponse(ret)
    else:
        ret = returnfail(ret, 'not POST')
        return JsonResponse(ret)


def leavegame(request):
    ret = {'status': 'success'}
    data = request.body
    jsondata = json.loads(data)
    code = jsondata.get('code')
    ret['code'] = code
    if Game.objects.filter(game_code=code).exists():
        game = Game.objects.get(game_code=code)
        name = jsondata.get('name')
        if game.user_set.filter(name=name).exists():
            user = game.user_set.get(name=name)
            user.in_game = False
        else:
            ret['status'] = 'failed'
            ret['message'] = "user doesn't exist"
    else:
        ret['status'] = 'failed'
        ret['message'] = "game doesn't exist"
    return JsonResponse(ret)


# only for creator
def endround(request):
    ret = {'status': 'success'}
    data = request.body
    jsondata = json.loads(data)
    code = jsondata.get('code')
    ret['code'] = code

    if Game.objects.filter(game_code=code).exists():
        game = Game.objects.get(game_code=code)
        user_list = game.user_set.all()
        game.in_game = False
        for usr in user_list:
            usr.in_game = False
            usr.save()
        game.save()

    else:
        ret['status'] = 'failed'
        ret['message'] = 'game doesnt exist'
    return JsonResponse(ret)


def leavelobby(request):
    ret = {'status': 'success'}
    data = request.body
    jsondata = json.loads(data)
    code = jsondata.get('code')
    if Game.objects.filter(game_code=code).exists():
        game = Game.objects.get(game_code=code)
        name = jsondata.get('name')
        if (game.user_set.get(name=name)):
            user = game.user_set.get(name=name)
            user.delete()

        else:
            ret['status'] = 'failed'
            ret['message'] = "user doesn't exist"
        game.save()
    else:
        ret['status'] = 'failed'
        ret['message'] = "game doesn't exist"
    return JsonResponse(ret)


def getusers(request):
    ret = {'status': 'success'}
    data = request.body
    jsondata = json.loads(data)
    code = jsondata.get('code')
    game = Game.objects.get(game_code=code)
    ret['code'] = code
    users = []
    username = request.session['user']
    if game.user_set.filter(name=username).exists():
        for x in game.user_set.exclude(name=username):
            users.append(x.name)
        ret['users'] = users
    else:
        ret['status'] = 'failed'
        ret['message'] = 'your user has been deleted'
    ret['in_game'] = game.in_game
    return JsonResponse(ret)


def getround(request):
    ret = {'status': 'success'}
    data = request.body
    jsondata = json.loads(data)
    code = jsondata.get('code')
    game = Game.objects.get(game_code=code)
    round = game.round_num
    in_game = game.in_game

    ret['round'] = game.round_num
    ret['round_len'] = game.round_length
    ret['in_game'] = game.in_game
    ret['code'] = game.game_code
    return JsonResponse(ret)


def startround(request):
    ret = {'status': 'success'}
    data = request.body
    jsondata = json.loads(data)
    code = jsondata.get('code')
    game = Game.objects.get(game_code=code)
    game.round_num = game.round_num + 1
    game.save()
    ret['round'] = game.round_num
    ret['code'] = game.game_code
    return JsonResponse(ret)


def randomcode():
    return ''.join(random.choice(string.lowercase) for i in range(5))


def returnfail(ret, message):
    ret['status'] = 'failed'
    ret['message'] = message
    return ret
