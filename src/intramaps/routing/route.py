'''Route class definition.'''
from intramaps.building.nodes.node import Node
from intramaps.enums.enum_routing import EnumMovement
from intramaps.routing.route_step import RouteStep

class Route:
    '''A path between two nodes, as consecutive steps.

    Attributes:
        steps: The steps in travel order, each one starting where the previous one ended.
        origin: The node where the route begins.
        destination: The node where the route ends.
        seconds: Time to walk the whole route, in seconds.
        meters: Length of the route in meters, counting the height climbed or descended.
        movements: What to do where each step meets the next one, or None when it does not apply.
    '''

    def __init__(self, steps: tuple[RouteStep, ...]):
        if not steps or not all(isinstance(step, RouteStep) for step in steps):
            raise ValueError("a route must have at least one RouteStep")
        for previous, following in zip(steps, steps[1:]):
            if previous.end != following.start:
                raise ValueError("each step must start where the previous one ended")
        self.__steps = tuple(steps)

    @property
    def steps(self) -> tuple[RouteStep, ...]:
        '''Returns the steps in travel order.'''
        return self.__steps

    @property
    def origin(self) -> Node:
        '''Returns the node where the route begins.'''
        return self.__steps[0].start

    @property
    def destination(self) -> Node:
        '''Returns the node where the route ends.'''
        return self.__steps[-1].end

    @property
    def seconds(self) -> float:
        '''Returns the time to walk the whole route, in seconds.'''
        return sum(step.seconds for step in self.__steps)

    @property
    def meters(self) -> float:
        '''Returns the length of the route in meters, counting the height climbed or descended.'''
        return sum((step.meters or 0.0) + step.rise_m for step in self.__steps)

    @property
    def movements(self) -> tuple[EnumMovement | None, ...]:
        '''Returns what to do where each step meets the next one.

        Only the junctions between steps count, and not the corners inside a step. A movement is
        None next to a step that changes floors (stairs, elevator). A route with n steps has n - 1
        movements.
        '''
        return tuple(arriving.go_to(leaving)
                     for arriving, leaving in zip(self.__steps, self.__steps[1:]))
