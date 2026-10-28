CREATE TABLE IF NOT EXISTS floors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level INTEGER NOT NULL,
    building TEXT NOT NULL,
    elevation_m REAL NOT NULL,
    image_path TEXT NOT NULL,
    width_px INTEGER NOT NULL
        CHECK (width_px > 0),
    height_px INTEGER NOT NULL
        CHECK (height_px > 0),
    meters_per_pixel REAL NOT NULL
        CHECK (meters_per_pixel > 0)
);

CREATE TABLE IF NOT EXISTS nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    floor_id INTEGER NOT NULL
        REFERENCES floors(id),
    name TEXT,
    number TEXT,
    type INTEGER NOT NULL
        CHECK (type BETWEEN 1 AND 12),
    x REAL NOT NULL
        CHECK (x >= 0),
    y REAL NOT NULL
        CHECK (y >= 0),
    facing REAL
        CHECK (facing >= 0 AND facing < 360),
    opens_at TEXT,
    closes_at TEXT,
    gender_restriction INTEGER NOT NULL DEFAULT 0
        CHECK (gender_restriction BETWEEN 0 AND 3),
    role_restriction INTEGER NOT NULL DEFAULT 0
        CHECK (role_restriction BETWEEN 0 AND 2),
    status INTEGER NOT NULL DEFAULT 0
        CHECK (status BETWEEN 0 AND 2),

    CHECK (gender_restriction = 0 OR type = 2),
    CHECK (type <> 1 OR name IS NOT NULL OR number IS NOT NULL),
    CHECK ((opens_at IS NULL) = (closes_at IS NULL)),
    CHECK (opens_at IS NULL OR type IN (5, 6)),
    CHECK ((type IN (10, 12)) = (facing IS NOT NULL))
);

CREATE TABLE IF NOT EXISTS connections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type INTEGER NOT NULL
        CHECK (type BETWEEN 0 AND 3),
    node_a_id INTEGER NOT NULL
        REFERENCES nodes(id),
    node_b_id INTEGER NOT NULL
        REFERENCES nodes(id),
    status INTEGER NOT NULL DEFAULT 0
        CHECK (status BETWEEN 0 AND 2),
    accessible INTEGER NOT NULL
        CHECK (accessible IN (0, 1)),
    rise_m REAL NOT NULL DEFAULT 0
        CHECK (rise_m >= 0),
    wait_time_s REAL NOT NULL DEFAULT 0
        CHECK (wait_time_s >= 0),

    CHECK (node_a_id < node_b_id),
    UNIQUE (node_a_id, node_b_id)
);

CREATE TABLE IF NOT EXISTS connection_children (
    node_id INTEGER PRIMARY KEY
        REFERENCES nodes(id) ON DELETE CASCADE,
    connection_id INTEGER NOT NULL
        REFERENCES connections(id) ON DELETE CASCADE,
    position REAL NOT NULL
        CHECK (position BETWEEN 0 AND 1)
);

CREATE TABLE IF NOT EXISTS connection_waypoints (
    connection_id INTEGER NOT NULL
        REFERENCES connections(id) ON DELETE CASCADE,
    waypoint_order INTEGER NOT NULL
        CHECK (waypoint_order >= 1),
    x REAL NOT NULL CHECK (x >= 0),
    y REAL NOT NULL CHECK (y >= 0),

    PRIMARY KEY (connection_id, waypoint_order)
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    gender INTEGER NOT NULL DEFAULT 0
        CHECK (gender BETWEEN 0 AND 3),
    role INTEGER NOT NULL DEFAULT 0
        CHECK (role BETWEEN 0 AND 2),
    accessibility INTEGER NOT NULL DEFAULT 0
        CHECK (accessibility BETWEEN 0 AND 2),
    speed REAL NOT NULL DEFAULT 1.4
        CHECK (speed > 0),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL
        REFERENCES users(id) ON DELETE CASCADE,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS favorites (
    user_id INTEGER NOT NULL
        REFERENCES users(id) ON DELETE CASCADE,
    node_id INTEGER NOT NULL
        REFERENCES nodes(id) ON DELETE CASCADE,

    PRIMARY KEY (user_id, node_id)
);

CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL
        REFERENCES users(id) ON DELETE CASCADE,
    node_a_id INTEGER NOT NULL
        REFERENCES nodes(id) ON DELETE CASCADE,
    node_b_id INTEGER NOT NULL
        REFERENCES nodes(id) ON DELETE CASCADE,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK(node_a_id <> node_b_id)
);

CREATE INDEX IF NOT EXISTS idx_connection_children_connection_id
    ON connection_children(connection_id);

CREATE INDEX IF NOT EXISTS idx_sessions_user_id
    ON sessions(user_id);

CREATE INDEX IF NOT EXISTS idx_favorites_node_id
    ON favorites(node_id);

CREATE INDEX IF NOT EXISTS idx_history_user_id
    ON history(user_id);

CREATE INDEX IF NOT EXISTS idx_nodes_floor_id
    ON nodes(floor_id);

CREATE INDEX IF NOT EXISTS idx_connections_node_b_id
    ON connections(node_b_id);
