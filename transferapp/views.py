from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotAllowed
import pymongo
import csv
from bson.objectid import ObjectId

# Create your views here.
def index(request):
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    dbs = client.list_database_names()
    if 'project' not in dbs:
        db = client['project']
        transferCollection = db['transfer']
        csv_data = read_csv('./Summer22_FootballTransfers.csv')
        transferCollection.insert_many(csv_data)
    else:
        db = client['project']
        transferCollection = db['transfer']
    olderPlayer = transferCollection.find().sort('age',pymongo.DESCENDING).limit(1)
    YoungerPlayer = transferCollection.find().sort('age',pymongo.ASCENDING).limit(1)
    data = {}
    for player in olderPlayer:
        data['name'] = player.get('name')
        data['age'] = player.get('age')
    youngerPlayerData = {}
    for player in YoungerPlayer:
        youngerPlayerData['name'] = player.get('name')
        youngerPlayerData['age'] = player.get('age')


    #the most club purchase player
    results = transferCollection.aggregate(
        [
            {
                "$group":{"_id":"$new_club","count":{"$sum":1}}
            },
            {
                "$sort":{"count":-1}
            },
            {
                "$limit":1
            }
        ]
    )
    mostClubPurchase = {}
    for club in results:
        mostClubPurchase['new_club'] = club.get('_id')
        mostClubPurchase['count'] = club.get('count')

     #the letest Legua purchase player
    leatestLeguaEnrollPlayer = transferCollection.aggregate(
        [
            {
                "$group":{"_id":"$league_new_club","count":{"$sum":1}}
            },
            {
                "$sort":{"count":1}
            },
            {
                "$limit":1
            }
        ]
    )
    letestLeguaPurchase = {}
    for club in leatestLeguaEnrollPlayer:
        letestLeguaPurchase['new_legua'] = club.get('_id')
        letestLeguaPurchase['count'] = club.get('count')

    topPlayer = transferCollection.find().sort('player_valuje',pymongo.DESCENDING).limit(1)
    topPlayerPrice = {}
    for player in topPlayer:
        topPlayerPrice['name'] = player.get('name')
        topPlayerPrice['player_valuje'] = player.get('player_valuje')

    data = {
        'countAlltransfer' : transferCollection.count_documents({}),
        'olderPlayer' : data,
        'youngerPlayer': youngerPlayerData,
        'mostClubPurchase' : mostClubPurchase,
        'letestLeguaPurchase' : letestLeguaPurchase,
        'topPlayer' :  topPlayerPrice

    }

    return render(request,'index.html',data)


def club(request):
    transferCollection = connect()
    unique_values = transferCollection.distinct('origin_club')
    some_unqiue = unique_values[0:48]
    unqiue_rows = []
    for value in  some_unqiue:
        query = {'origin_club': value}
        unique_row = transferCollection.find_one(query)
        unqiue_rows.append(unique_row)
    data = {
        'result': unqiue_rows
    }

    return render(request, 'club.html',data)

def clubDetalis(request, param):
    transferCollection = connect()
    club_info = transferCollection.find_one({'origin_club':param})
    query = {"$or":[{'origin_club':param},{'new_club':param}]}
    total_transfer = transferCollection.count_documents(query)
    palyer_sold_count = transferCollection.count_documents({'origin_club':param})
    player_bought_count = transferCollection.count_documents({'new_club':param})

    topPlayer = transferCollection.find({'new_club':param}).sort('player_valuje',pymongo.DESCENDING).limit(1)
    topPlayerPrice = {}
    for player in topPlayer:
        topPlayerPrice['name'] = player.get('name')
        topPlayerPrice['player_valuje'] = player.get('player_valuje')

    result = transferCollection.find(query).sort('_id',-1).limit(30)

    data = {
        'club' : club_info,
        'total_transfer': total_transfer,
        'palyer_sold_count': palyer_sold_count,
        'player_bought_count': player_bought_count,
        'topPlayerPrice':topPlayerPrice,
        'result': result

    }
    return render(request, 'clubDetalis.html', data)
def search(request):
    transferCollection = connect()
    keyword = request.GET['club']
    result = transferCollection.find({'origin_club':{"$regex":keyword}})
    data = {
        'result': result
    }
    return render(request, 'search.html',data)


def players(request):
    transferCollection = connect()
    transferCollection.create_index([('name', 1)])
    result = transferCollection.find().hint([('name', 1)]).limit(36)
    data = {
        'result': result
    }
    return render(request, 'players.html', data)

def searchPlayer(request):
    transferCollection = connect()
    keyword = request.GET['player_name']
    result = transferCollection.find({'name':{"$regex":keyword}})
    data = {
        'result': result
    }
    return render(request, 'playersSearch.html',data)

def transfer(request):
    transferCollection = connect()
    result = transferCollection.find().sort('_id',-1).limit(30)
    data = {
        'result': result
    }
    return render(request, 'transfer.html',data)

def addTransfer(request):
    transferCollection = connect()
    origin_clubs = sorted(transferCollection.distinct('origin_club'))
    positions = sorted(transferCollection.distinct('position'))
    leagues_origin_club = sorted(transferCollection.distinct('league_origin_club'))
    countries_origin_club = sorted(transferCollection.distinct('country_origin_club'))
    new_clubs = sorted(transferCollection.distinct('new_club'))
    leagues_new_club = sorted(transferCollection.distinct('league_new_club'))
    countries_new_club=sorted(transferCollection.distinct('country_new_club'))

    context = {
        'origin_clubs': origin_clubs,
        'positions':positions,
        'leagues_origin_club':leagues_origin_club,
        'countries_origin_club':countries_origin_club,
        'new_clubs':new_clubs,
        'leagues_new_club':leagues_new_club,
        'countries_new_club':countries_new_club
        }
    if request.method == 'POST':
        name = request.POST.get('name')
        position = request.POST.get('position')
        age = request.POST.get('age')
        origin_club = request.POST.get('origin_club')
        league_origin_club = request.POST.get('league_origin_club')
        country_origin_club = request.POST.get('country_origin_club')
        new_club = request.POST.get('new_club')
        league_new_club = request.POST.get('league_new_club')
        country_new_club = request.POST.get('country_new_club')
        player_valuje = request.POST.get('player_valuje')

        # Insert the transfer data into the "transfers" collection
        transfer = {
            'name': name,
            'position': position,
            'age': age,
            'origin_club': origin_club,
            'league_origin_club': league_origin_club,
            'country_origin_club': country_origin_club,
            'new_club':new_club,
            'league_new_club': league_new_club,
            'country_new_club': country_new_club,
            'player_valuje': player_valuje
        }
        transferCollection.insert_one(transfer)
        return redirect('transfer')

def editTransfer(request):
        transferCollection = connect()
        player_name = request.POST['player_name']

        name = request.POST.get('name')
        position = request.POST.get('position')
        age = request.POST.get('age')
        origin_club = request.POST.get('origin_club')
        league_origin_club = request.POST.get('league_origin_club')
        country_origin_club = request.POST.get('country_origin_club')
        new_club = request.POST.get('new_club')
        league_new_club = request.POST.get('league_new_club')
        country_new_club = request.POST.get('country_new_club')
        player_valuje = request.POST.get('player_valuje')

        transfer = {
            'name': name,
            'position': position,
            'age': age,
            'origin_club': origin_club,
            'league_origin_club': league_origin_club,
            'country_origin_club': country_origin_club,
            'new_club':new_club,
            'league_new_club': league_new_club,
            'country_new_club': country_new_club,
            'player_valuje': player_valuje
        }
        filter_up = {'name':player_name}
        update = {"$set": transfer}
        transferCollection.update_one(filter_up, update)
        return redirect('transfer')




def updateTransfer(request):
    transferCollection = connect()
    player_name = request.POST['player_name']
    origin_clubs = sorted(transferCollection.distinct('origin_club'))
    positions = sorted(transferCollection.distinct('position'))
    leagues_origin_club = sorted(transferCollection.distinct('league_origin_club'))
    countries_origin_club = sorted(transferCollection.distinct('country_origin_club'))
    new_clubs = sorted(transferCollection.distinct('new_club'))
    leagues_new_club = sorted(transferCollection.distinct('league_new_club'))
    countries_new_club=sorted(transferCollection.distinct('country_new_club'))

    if(player_name):
        result = transferCollection.find_one({'name':player_name})
        data = {
            'result' : result,
            'origin_clubs': origin_clubs,
            'positions':positions,
            'leagues_origin_club':leagues_origin_club,
            'countries_origin_club':countries_origin_club,
            'new_clubs':new_clubs,
            'leagues_new_club':leagues_new_club,
            'countries_new_club':countries_new_club
        }
    return render(request,'updateTransfer.html',data)


def deleteTransfer(request):
    transferCollection = connect()
    player_name = request.POST['player_name']
    if(player_name):
        transferCollection.delete_one({'name':player_name})
        return redirect('transfer')



def deleteAllTransfers(request):
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    client.drop_database('project')
    return redirect('transfer')


def read_csv(file_path):
    data = []
    with open(file_path, 'r+') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            data.append(row)
        return data

def connect():
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['project']
    return db['transfer']
