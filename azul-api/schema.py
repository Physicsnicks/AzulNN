import graphene
from azul import Game

g1 = Game(4)


class PlayerNode(graphene.ObjectType):
    pid = graphene.Int()
    name = graphene.String()
    score = graphene.Int()
    garage = graphene.List(graphene.List(graphene.Int))
    wall = graphene.List(graphene.List(graphene.Int))
    floor = graphene.List(graphene.List(graphene.Int))


def resolve_player(root, args, pid):
    return PlayerNode(
        pid=pid,
        name=g1.playArray[pid].name,
        score=g1.playArray[pid].score,
        garage=g1.playArray[pid].board.garage,
        wall=g1.playArray[pid].board.wall,
        floor=g1.playArray[pid].board.floor,
           )


class GameNode(graphene.ObjectType):
    whosturn = graphene.Int()
    gameover = graphene.Int()
    factDisps = graphene.List(graphene.List(graphene.Int))


def resolve_gamestate(self, info):
    return GameNode(
        whosturn=g1.playersTurn,
        gameover=g1.gameWinner,
        factDisps=[disp for disp in g1.fact.factDisps],
    )


class Query(graphene.ObjectType):
    hello = graphene.String(name=graphene.String(default_value="Luke Skywalker"))

    game = graphene.Field(
        GameNode,
        resolver=resolve_gamestate)

    player = graphene.Field(
        PlayerNode,
        resolver=resolve_player,
        pid=graphene.Argument(graphene.Int, required=True),
        )

    def resolve_hello(self, info, name):
        return f'Hello {name}'


schema = graphene.Schema(query=Query)