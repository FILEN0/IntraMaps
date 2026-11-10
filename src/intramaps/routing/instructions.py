'''The instructions of a route, told in words.'''
from intramaps.building.nodes.node import Node
from intramaps.enums.enum_building import EnumConnection, EnumNode
from intramaps.enums.enum_routing import EnumMovement
from intramaps.routing.route import Route
from intramaps.routing.route_step import RouteStep, node_label

TURNS = {
    EnumMovement.STRAIGHT: "continue em frente",
    EnumMovement.SLIGHT_RIGHT: "vire levemente à direita",
    EnumMovement.RIGHT: "vire à direita",
    EnumMovement.SHARP_RIGHT: "faça uma curva fechada à direita",
    EnumMovement.SLIGHT_LEFT: "vire levemente à esquerda",
    EnumMovement.LEFT: "vire à esquerda",
    EnumMovement.SHARP_LEFT: "faça uma curva fechada à esquerda",
    EnumMovement.BACK: "dê meia-volta",
}
PASSAGES = {
    EnumConnection.STAIRS: "a escada",
    EnumConnection.ELEVATOR: "o elevador",
    EnumConnection.RAMP: "a rampa",
}
CLIMBS = {
    (EnumConnection.STAIRS, True): "Suba a escada",
    (EnumConnection.STAIRS, False): "Desça a escada",
    (EnumConnection.ELEVATOR, True): "Pegue o elevador para subir",
    (EnumConnection.ELEVATOR, False): "Pegue o elevador para descer",
    (EnumConnection.RAMP, True): "Suba a rampa",
    (EnumConnection.RAMP, False): "Desça a rampa",
}
PLACES = {
    EnumNode.ROOM: ("a", "sala"),
    EnumNode.WASHROOM: ("o", "sanitário"),
    EnumNode.STUDY_SPACE: ("o", "espaço de estudo"),
    EnumNode.PHOTO_SPOT: ("o", "ponto de foto"),
    EnumNode.CAFETERIA: ("a", "cantina"),
    EnumNode.BUILDING_EXIT: ("a", "saída"),
    EnumNode.DRINKING_FOUNTAIN: ("o", "bebedouro"),
    EnumNode.BICYCLE_PARKING: ("o", "bicicletário"),
}


def write_instructions(route: Route) -> list[str]:
    '''Tells a route in words.

    The steps that go straight on are told together with the step after them, in one sentence
    with the sum of their lengths.

    Args:
        route: The route to tell.

    Returns:
        The sentences in Portuguese, in travel order.
    '''
    movements = (*route.movements, None)
    followings = (*route.steps[1:], None)
    instructions = []
    meters = 0.0
    for step, movement, following in zip(route.steps, movements, followings):
        meters += step.meters or 0.0
        if movement == EnumMovement.STRAIGHT and not step.changes_floor:
            continue
        instructions.append(_sentence(step, meters, movement, following))
        meters = 0.0
    return instructions


def _sentence(step: RouteStep, meters: float, movement: EnumMovement | None,
              following: RouteStep | None) -> str:
    '''Tells how to walk a step, together with the steps that go straight on before it.

    Args:
        step: The step to tell.
        meters: The length to tell, in meters.
        movement: What to do where the step ends, or None when it does not apply.
        following: The step that comes next, or None for the last step.

    Returns:
        The sentence in Portuguese.
    '''
    if step.changes_floor:
        text = CLIMBS[(step.connection.type, step.rise_m > 0)]
        if movement in TURNS:
            return f"{text} e, ao sair, {TURNS[movement]}."
        return f"{text}."
    text = f"Siga por {max(round(meters), 1)} m"
    if following is None:
        return f"{text} até {_place(step.end)}."
    if movement in (EnumMovement.UP, EnumMovement.DOWN):
        return f"{text} até {PASSAGES[following.connection.type]}."
    if movement in TURNS:
        return f"{text} e {TURNS[movement]}."
    return f"{text}."


def _place(node: Node) -> str:
    '''Names a place with its article, like "a sala 1006" or "a Cantina".'''
    article, noun = PLACES[node.type]
    if node.type == EnumNode.ROOM:
        return f"{article} {noun} {node_label(node)}"
    name = getattr(node, "name", None)
    return f"{article} {name}" if name else f"{article} {noun}"
