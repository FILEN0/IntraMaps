'''Runs the IntraMaps visit scenarios on a temporary copy of the ICEx database.

Run it from the project folder, with the virtual environment active:

    python tests/run_scenarios.py            # about two minutes
    python tests/run_scenarios.py --verbose  # also lists every check

It never touches data/intramaps.db: the seed is loaded into a temporary file with the
functions of helpers/load_demo.py, and the API is called through FastAPI's test client.
It prints four parts:

1. every pair of rooms visited by three profiles, with what the comparison shows;
2. two routes that the report describes, for each profile;
3. the checks of the expected answers of the API;
4. the response time of one route.

The exit code is 1 when a check fails.
'''
# pylint: disable=wrong-import-position,import-error
import datetime
import functools
import json
import math
import sqlite3
import statistics
import sys
import tempfile
import time
from collections import defaultdict
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from helpers import load_demo
from intramaps.api import dependencies
from intramaps.building import opening_hours
from intramaps.building.nodes.pseudo_node import PseudoNode
from intramaps.database.connection_repository import ConnectionRepository
from intramaps.database.database import Database
from intramaps.database.floor_repository import FloorRepository
from intramaps.database.node_repository import NodeRepository
from intramaps.enums.enum_building import EnumConnection, EnumNode
from intramaps.enums.enum_user import EnumAccessibility, EnumGender, EnumRole
from intramaps.main import app
from intramaps.routing.instructions import write_instructions
from intramaps.routing.route import Route
from intramaps.services.connection_service import ConnectionService
from intramaps.services.floor_service import FloorService
from intramaps.services.graph_service import GraphService
from intramaps.services.node_service import NodeService
from intramaps.services.route_service import RouteService
from intramaps.users.anonymous import Anonymous

API = "/api/v1"
RUNS = 50
FORBIDDEN = "você não pode ir a esse destino"
PROFILES = {"no restriction": EnumAccessibility.NONE, "wheelchair": EnumAccessibility.WHEELCHAIR,
            "crutches": EnumAccessibility.CRUTCHES}


# ------------------------------------------------------------------ setup
def build_database(path: Path) -> None:
    '''Loads the ICEx seed into a new database file, with the project's own loader.'''
    seed = json.loads(load_demo.SEED_PATH.read_text(encoding="utf-8"))
    scales = {floor["id"]: floor["meters_per_pixel"] for floor in seed["floors"]}
    database = Database(str(path))
    database.create_schema()
    floors = load_demo.load_floors(seed, FloorRepository(database))
    nodes = load_demo.load_nodes(seed, scales, NodeRepository(database))
    load_demo.load_connections(seed, scales, floors, nodes, ConnectionRepository(database))
    database.close()


def open_shared_database(path: Path) -> Database:
    '''Opens the database for the test client, which uses it from its worker threads.'''
    connect = sqlite3.connect
    sqlite3.connect = functools.partial(connect, check_same_thread=False)
    try:
        return Database(str(path))
    finally:
        sqlite3.connect = connect


class Services:
    '''The services of the API, built on one database, as the dependencies build them.'''

    def __init__(self, database: Database) -> None:
        self.nodes = NodeService(NodeRepository(database))
        self.floors = FloorService(FloorRepository(database))
        self.connections = ConnectionService(ConnectionRepository(database), self.nodes)
        self.routes = RouteService(self.nodes, GraphService(self.connections, self.floors))

    def place_id(self, text: str) -> int:
        '''Returns the id of the place with this number or name.'''
        for place in self.nodes.find_places():
            if text in (getattr(place, "number", None), getattr(place, "name", None)):
                return place.id
        raise LookupError(f"place {text} is not in the seed")

    def keep_in_memory(self) -> None:
        '''Loads nodes, connections and floors once, as the pairwise run asks many routes.'''
        nodes = self.nodes.get_nodes()
        self.nodes.get_nodes = lambda: nodes
        connections = self.connections.get_connections()
        self.connections.get_connections = lambda: connections
        elevations = self.floors.elevations()
        self.floors.elevations = lambda: elevations


@contextmanager
def clock(hour: int, minute: int = 0):
    '''Fixes the time that the opening hours compare with.'''
    real = opening_hours.datetime

    class FixedTime(datetime.datetime):
        '''A datetime whose now() is always the fixed time.'''

        @classmethod
        def now(cls, tz=None):
            return cls(2026, 11, 12, hour, minute)

    opening_hours.datetime = FixedTime
    try:
        yield
    finally:
        opening_hours.datetime = real


def profile(accessibility=EnumAccessibility.NONE, gender=EnumGender.NONE,
            role=EnumRole.STUDENT, speed=1.4) -> Anonymous:
    '''Returns the profile of a visitor without login.'''
    return Anonymous(gender, accessibility, role, speed)


def label(node) -> str:
    '''Returns the number or name of a place.'''
    return getattr(node, "number", None) or getattr(node, "name", None) or f"node {node.id}"


# ------------------------------------------------------------------ 1. pair by pair
def nearest_place(services: Services, node) -> str:
    '''Names the place closest to a node of the same floor, to locate stairs in the output.'''
    same_floor = [place for place in services.nodes.find_places()
                  if place.coordinates.floor_id == node.coordinates.floor_id]
    closest = min(same_floor, key=lambda place: math.dist(
        (place.coordinates.x, place.coordinates.y), (node.coordinates.x, node.coordinates.y)))
    return label(closest)


def visit_all_pairs(services: Services) -> None:  # pylint: disable=too-many-locals
    '''Asks the route of every pair of rooms for every profile and prints what it shows.'''
    rooms = sorted(services.nodes.find_places(node_type=EnumNode.ROOM), key=lambda room: room.id)
    pairs = [(a, b) for i, a in enumerate(rooms) for b in rooms[i + 1:]]
    users = {name: profile(accessibility) for name, accessibility in PROFILES.items()}
    start = time.perf_counter()
    trips = []
    for origin, destination in pairs:
        routes = {name: services.routes.find_route(origin.id, destination.id, user)
                  for name, user in users.items()}
        trips.append((origin, destination, routes))
    elapsed = time.perf_counter() - start
    count = len(pairs) * len(users)
    print(f"\n1. Visits pair by pair: {len(rooms)} rooms, {len(pairs)} pairs, "
          f"{len(users)} profiles")
    print(f"  {count} routes in {elapsed:.0f} s, {1000 * elapsed / count:.1f} ms per route"
          " (data kept in memory)")

    by_stairs, detours, extra_by_stairs = 0, [], defaultdict(float)
    for origin, destination, routes in trips:
        free, wheel = routes["no restriction"], routes["wheelchair"]
        stairs = [step.connection for step in free.steps
                  if step.connection.type == EnumConnection.STAIRS]
        if not stairs:
            continue
        by_stairs += 1
        extra = wheel.meters - free.meters
        detours.append((extra / free.meters, extra, origin, destination))
        for connection in stairs:
            extra_by_stairs[connection] += extra / len(stairs)
    print(f"  {100 * by_stairs / len(pairs):.0f}% of the pairs use stairs without restriction;"
          " a wheelchair has to go another way in all of them")
    print(f"  extra distance for a wheelchair in those pairs: median "
          f"{statistics.median(d[1] for d in detours):.0f} m "
          f"(+{100 * statistics.median(d[0] for d in detours):.0f}%)")
    for name in ("wheelchair", "crutches"):
        ratio = statistics.median(r[name].seconds / r["no restriction"].seconds for *_, r in trips)
        print(f"  {name}: the median trip takes {ratio:.2f}x the time without restriction")
    total = sum(extra_by_stairs.values())
    print("  stairs that cause most of the extra distance:")
    for connection, extra in sorted(extra_by_stairs.items(), key=lambda item: -item[1])[:3]:
        print(f"    stairs {connection.id} near {nearest_place(services, connection.node_a)}: "
              f"{100 * extra / total:.0f}% of all the extra distance")
    print("  largest detours:")
    for share, extra, origin, destination in sorted(detours, key=lambda d: -d[0])[:3]:
        print(f"    {label(origin)} -> {label(destination)}: +{extra:.0f} m (+{100 * share:.0f}%)")


# ------------------------------------------------------------------ 2. examples
def passages(route: Route) -> str:
    '''Names the stairs and elevators of a route.'''
    kinds = {EnumConnection.STAIRS: "stairs", EnumConnection.ELEVATOR: "elevator"}
    found = [kinds[step.connection.type] for step in route.steps if step.connection.type in kinds]
    return ", ".join(found) or "corridors only"


def compare(services: Services, origin: str, destination: str) -> None:
    '''Prints the same route for each profile, with the instructions of the wheelchair.'''
    origin_id, destination_id = services.place_id(origin), services.place_id(destination)
    routes = {name: services.routes.find_route(origin_id, destination_id, profile(accessibility))
              for name, accessibility in PROFILES.items()}
    base = routes["no restriction"]
    print(f"\n  {origin} -> {destination}")
    for name, route in routes.items():
        extra = ""
        if route is not base:
            extra = (f"  ({route.seconds / base.seconds:.2f}x the time, "
                     f"{100 * (route.meters / base.meters - 1):+.0f}% distance)")
        print(f"    {name:15s} {route.seconds:6.1f} s {route.meters:6.1f} m  "
              f"{passages(route)}{extra}")
    for line in write_instructions(routes["wheelchair"]):
        print(f"      {line}")


def nearest_by_type(report, services: Services) -> None:
    '''Asks the nearest place of every type from room 1001, for each profile.'''
    origin = services.place_id("1001")
    print("\n  nearest place of each type from room 1001, in seconds, female profile")
    print(f"    {'type':18s} {'places':>6s}  " + "  ".join(f"{name:>14s}" for name in PROFILES))
    kinds = (EnumNode.WASHROOM, EnumNode.CAFETERIA, EnumNode.BUILDING_EXIT, EnumNode.STUDY_SPACE,
             EnumNode.PHOTO_SPOT, EnumNode.DRINKING_FOUNTAIN, EnumNode.BICYCLE_PARKING)
    for kind in kinds:
        count = len(services.nodes.find_places(node_type=kind))
        cells = []
        for accessibility in PROFILES.values():
            try:
                user = profile(accessibility, EnumGender.FEMALE)
                route = services.routes.find_nearest_route(origin, kind, user)
                cells.append(f"{route.seconds:14.1f}")
            except LookupError:
                cells.append(f"{'none':>14s}")
        print(f"    {kind.name.lower():18s} {count:6d}  " + "  ".join(cells))
        reachable = count == 0 or "none" not in cells[0]
        report.check(f"{kind.name.lower()} reachable from 1001", reachable)


# ------------------------------------------------------------------ 3. checks
class Report:  # pylint: disable=too-few-public-methods
    '''Counts the checks and prints the failed ones, or all of them when verbose.'''

    def __init__(self, verbose: bool) -> None:
        self.verbose = verbose
        self.failures = 0
        self.total = 0

    def check(self, description: str, ok: bool, note: str = "") -> None:
        '''Records one result.'''
        self.total += 1
        self.failures += not ok
        if self.verbose or not ok:
            print(f"  {'PASS' if ok else 'FAIL'}  {description:42s} {note}")


def expect(report: Report, client: TestClient, case: tuple, **options):
    '''Calls the API and checks the status code and, when given, the detail message.

    Args:
        case: (description, method, path, expected status, expected detail or None).
        options: Extra arguments for the request, like params, json or headers.

    Returns:
        The JSON body of the answer, or None when it is not JSON.
    '''
    description, method, path, status, detail = case
    response = client.request(method, API + path, **options)
    try:
        body = response.json()
    except ValueError:
        body = None
    got = body.get("detail") if isinstance(body, dict) else None
    ok = response.status_code == status and (detail is None or got == detail)
    note = f"[{response.status_code}]" + (f" {got}" if isinstance(got, str) else "")
    report.check(description, ok, note)
    return body


def check_routes(report: Report, client: TestClient, services: Services) -> None:
    '''Checks the answers of the route and place routes, at the hours that matter.'''
    room, upstairs = services.place_id("1001"), services.place_id("2021")
    staff_only = services.place_id("Sanitário Feminino (esquerda)")
    female = services.place_id("Sanitário Feminino (centro)")
    cafeteria = services.place_id("Cantina")
    corridor_end = next(node.id for node in services.nodes.get_nodes().values()
                        if isinstance(node, PseudoNode))
    route = f"/routes/{room}/to"
    with clock(12):
        expect(report, client, ("route between two rooms", "GET", f"{route}/{upstairs}", 200, None))
        expect(report, client, ("same origin and destination", "GET", f"{route}/{room}", 400,
                                "origem e destino são o mesmo lugar"))
        expect(report, client, ("place that does not exist", "GET", f"{route}/99999", 404,
                                "lugar 99999 não encontrado"))
        expect(report, client, ("corridor end is not a place", "GET", f"{route}/{corridor_end}",
                                404, f"lugar {corridor_end} não encontrado"))
        expect(report, client, ("staff washroom, student", "GET", f"{route}/{staff_only}", 401,
                                FORBIDDEN), params={"gender": "female"})
        expect(report, client, ("staff washroom, staff", "GET", f"{route}/{staff_only}", 200, None),
               params={"gender": "female", "role": "staff"})
        expect(report, client, ("female washroom, male profile", "GET", f"{route}/{female}", 401,
                                FORBIDDEN), params={"gender": "male"})
        expect(report, client, ("cafeteria open at 12:00", "GET", f"{route}/{cafeteria}", 200,
                                None))
        expect(report, client, ("invalid speed in the query", "GET", f"{route}/{upstairs}", 422,
                                None), params={"speed": 0})
        expect(report, client, ("floor that does not exist", "GET", "/places", 400,
                                "andar 9 não existe"), params={"floor": 9})
    with clock(19):
        expect(report, client, ("cafeteria closed at 19:00", "GET", f"{route}/{cafeteria}", 401,
                                FORBIDDEN))
        expect(report, client, ("nearest cafeteria at 19:00", "GET",
                                f"/routes/{room}/nearest/cafeteria", 404,
                                f"nenhum lugar do tipo cafeteria alcançável a partir de {room}"))
    with clock(23, 30):
        no_exit = f"nenhum lugar do tipo building-exit alcançável a partir de {room}"
        expect(report, client, ("nearest exit at 23:30, student", "GET",
                                f"/routes/{room}/nearest/building-exit", 404, no_exit))
        expect(report, client, ("nearest exit at 23:30, staff", "GET",
                                f"/routes/{room}/nearest/building-exit", 200, None),
               params={"role": "staff"})


def check_users(report: Report, client: TestClient, services: Services) -> None:
    '''Checks the account, login, history and favorites routes.'''
    room, upstairs = services.place_id("1001"), services.place_id("2021")
    account = {"username": "ana_silva", "password": "senha123"}
    expect(report, client, ("profile without token", "GET", "/users/me", 401,
                            "autenticação necessária"))
    expect(report, client, ("invalid token", "GET", "/users/me", 401,
                            "token inválido ou expirado"), headers={"Authorization": "Bearer abc"})
    expect(report, client, ("new account", "POST", "/users", 201, None), json=account)
    expect(report, client, ("repeated username", "POST", "/users", 400, "username já existe"),
           json=account)
    expect(report, client, ("password without a digit", "POST", "/users", 400,
                            "a senha precisa de ao menos uma letra e um número"),
           json={"username": "bia", "password": "abcdefg"})
    expect(report, client, ("speed above 10 m/s", "POST", "/users", 422, None),
           json={"username": "caio", "password": "senha123", "speed": 20})
    expect(report, client, ("wrong password", "POST", "/users/login", 401,
                            "usuário ou senha inválidos"),
           json={"username": "ana_silva", "password": "errada1"})
    login = expect(report, client, ("login", "POST", "/users/login", 200, None), json=account)
    auth = {"Authorization": f"Bearer {login['token']}"}
    expect(report, client, ("update without fields", "PATCH", "/users/me", 400,
                            "informe ao menos um campo"), json={}, headers=auth)
    expect(report, client, ("maintenance list for a student", "GET", "/places/maintenance", 401,
                            "acesso restrito ao papel staff"), headers=auth)
    with clock(12):
        expect(report, client, ("route of a logged-in user", "GET",
                                f"/routes/{room}/to/{upstairs}", 200, None), headers=auth)
    history = expect(report, client, ("history", "GET", "/users/me/history", 200, None),
                     headers=auth)
    report.check("the route went to the history", isinstance(history, list) and len(history) == 1)
    expect(report, client, ("history item that does not exist", "DELETE",
                            "/users/me/history/999", 404, "item 999 do histórico não encontrado"),
           headers=auth)
    expect(report, client, ("favorite place that does not exist", "PUT",
                            "/users/me/favorites/99999", 404, "lugar 99999 não encontrado"),
           headers=auth)
    expect(report, client, ("floors", "GET", "/floors", 200, None))
    response = client.get(f"{API}/floors/1/plan")
    report.check("plan of floor 1", response.status_code == 200
                 and response.headers["content-type"] == "image/png")


def check_maintenance(report: Report, database: Database, services: Services) -> None:
    '''Puts a corridor of a route in maintenance: a student goes around it, staff does not.'''
    origin, destination = services.place_id("1001"), services.place_id("1048")
    student, staff = profile(), profile(role=EnumRole.STAFF)
    before = services.routes.find_route(origin, destination, student)
    corridors = [step.connection.id for step in before.steps
                 if step.connection.type == EnumConnection.CORRIDOR]
    closed = corridors[len(corridors) // 2]
    database.execute("UPDATE connections SET status = 1 WHERE id = ?", (closed,))
    try:
        around = services.routes.find_route(origin, destination, student)
        same = services.routes.find_route(origin, destination, staff)
    finally:
        database.execute("UPDATE connections SET status = 0 WHERE id = ?", (closed,))
    report.check("a student goes around a closed corridor",
                 closed not in {step.connection.id for step in around.steps}
                 and around.seconds > before.seconds,
                 f"{before.seconds:.1f} s -> {around.seconds:.1f} s")
    report.check("staff can still walk it", abs(same.seconds - before.seconds) < 1e-9)


# ------------------------------------------------------------------ 4. response time
def median_ms(function) -> float:
    '''Returns the median time of a call, in milliseconds.'''
    function()
    times = []
    for _ in range(RUNS):
        start = time.perf_counter()
        function()
        times.append((time.perf_counter() - start) * 1000)
    return statistics.median(times)


def measure(client: TestClient, path: Path) -> None:
    '''Prints the median response time of one route, reading the database at every request.'''
    database = Database(str(path))
    try:
        services = Services(database)
        origin, destination = services.place_id("1021"), services.place_id("2021")
        user = profile()
        in_services = median_ms(lambda: services.routes.find_route(origin, destination, user))
        through_http = median_ms(lambda: client.get(f"{API}/routes/{origin}/to/{destination}"))
    finally:
        database.close()
    print(f"\n4. Response time of one route, reading the database (median of {RUNS} runs)")
    print(f"  services   {in_services:6.1f} ms")
    print(f"  HTTP       {through_http:6.1f} ms")


# ------------------------------------------------------------------ main
def main() -> int:
    '''Builds the temporary database, runs the four parts and returns the exit code.'''
    report = Report(verbose="--verbose" in sys.argv)
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "intramaps.db"
        build_database(path)
        shared = open_shared_database(path)
        app.dependency_overrides[dependencies.get_db] = lambda: shared
        try:
            with TestClient(app) as client:
                services = Services(shared)
                memory = Services(shared)
                memory.keep_in_memory()
                with clock(12):
                    visit_all_pairs(memory)
                    print("\n2. Two routes for each profile")
                    compare(memory, "1021", "2021")
                    compare(memory, "Cantina", "2038")
                    nearest_by_type(report, memory)
                print("\n3. Expected answers of the API")
                check_routes(report, client, services)
                check_users(report, client, services)
                check_maintenance(report, shared, services)
                print(f"  {report.total - report.failures} of {report.total} checks passed")
                measure(client, path)
        finally:
            app.dependency_overrides.clear()
            shared.close()
    return 1 if report.failures else 0


if __name__ == "__main__":
    sys.exit(main())
