
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'esrb') THEN
    CREATE TYPE esrb AS ENUM (
      'Early Childhood',
      'Everyone',
      'Everyone 10+',
      'Teen',
      'Mature 17+',
      'Adults Only 18+',
      'Rating Pending'
    );
  END IF;
END$$;


CREATE TABLE "user" (
    user_UUID uuid NOT NULL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    total_playtime INT NOT NULL CHECK (total_playtime >= 0) DEFAULT 0,
    creation_date DATE NOT NULL DEFAULT CURRENT_DATE,  
    last_access_date DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE collection(
    collection_UUID uuid NOT NULL PRIMARY KEY,
    user_UUID uuid NOT NULL REFERENCES "user"(user_UUID) ON DELETE CASCADE,
    collection_name TEXT NOT NULL,
    num_of_games INT NOT NULL DEFAULT 0, 
    total_playtime INT NOT NULL DEFAULT 0,
    UNIQUE(user_UUID, collection_name)
);

CREATE TABLE follows(
    follower_user_UUID uuid NOT NULL REFERENCES "user"(user_UUID) ON DELETE CASCADE,
    followed_user_UUID uuid NOT NULL REFERENCES "user"(user_UUID) ON DELETE CASCADE,
    PRIMARY KEY (follower_user_UUID, followed_user_UUID),
    CHECK (followed_user_UUID != follower_user_UUID)
);

CREATE TABLE platform(
    platform_UUID uuid NOT NULL PRIMARY KEY,
    platform_name TEXT NOT NULL UNIQUE
);

CREATE TABLE owns_platform(
    user_UUID uuid NOT NULL REFERENCES "user"(user_UUID) ON DELETE CASCADE,
    platform_UUID uuid NOT NULL REFERENCES platform(platform_UUID) ON DELETE CASCADE,
    PRIMARY KEY(user_UUID, platform_UUID)
);


CREATE TABLE game(
    game_UUID uuid NOT NULL PRIMARY KEY,
    title TEXT NOT NULL UNIQUE,
    game_description TEXT,
    total_user_rating FLOAT NOT NULL DEFAULT 1.0 CHECK(total_user_rating >= 1 AND total_user_rating <= 5),
    esrb_rating esrb NOT NULL,
    num_of_players INT NOT NULL DEFAULT 0
);

CREATE TABLE collection_contains(
    collection_UUID uuid NOT NULL,
    game_UUID uuid NOT NULL,
    FOREIGN KEY (collection_UUID) REFERENCES "collection"(collection_UUID) ON DELETE CASCADE,
    FOREIGN KEY (game_UUID) REFERENCES game(game_UUID) ON DELETE CASCADE,
    PRIMARY KEY (collection_UUID, game_UUID)
);

CREATE TABLE game_release(
    game_UUID uuid NOT NULL,
    platform_UUID uuid NOT NULL,
    release_date DATE NOT NULL DEFAULT CURRENT_DATE,
    price NUMERIC(10, 2) NOT NULL DEFAULT 0.00 CHECK (price >= 0),
    FOREIGN KEY (platform_UUID) REFERENCES platform(platform_UUID) ON DELETE CASCADE,
    FOREIGN KEY (game_UUID) REFERENCES game(game_UUID) ON DELETE CASCADE,
    PRIMARY KEY (game_UUID, platform_UUID)
);


CREATE TABLE genre(
    genre_UUID uuid NOT NULL PRIMARY KEY,
    genre_name TEXT NOT NULL UNIQUE
);

CREATE TABLE game_fits_in_genre(
    game_UUID uuid NOT NULL,
    genre_UUID uuid NOT NULL,

    FOREIGN KEY (genre_UUID) REFERENCES genre(genre_UUID) ON DELETE CASCADE,
    FOREIGN KEY (game_UUID) REFERENCES game(game_UUID) ON DELETE CASCADE,
    PRIMARY KEY (game_UUID, genre_UUID)
);

CREATE TABLE contributor(
    contributor_UUID uuid NOT NULL PRIMARY KEY,
    contributor_name TEXT NOT NULL UNIQUE
);

CREATE TABLE publishes(
    contributor_UUID uuid NOT NULL,
    game_UUID uuid NOT NULL,
    FOREIGN KEY (contributor_UUID) REFERENCES contributor(contributor_UUID) ON DELETE CASCADE,
    FOREIGN KEY (game_UUID) REFERENCES game(game_UUID) ON DELETE CASCADE,
    PRIMARY KEY (contributor_UUID, game_UUID)
);

CREATE TABLE develops(
    contributor_UUID uuid NOT NULL,
    game_UUID uuid NOT NULL,
    FOREIGN KEY (contributor_UUID) REFERENCES contributor(contributor_UUID) ON DELETE CASCADE,
    FOREIGN KEY (game_UUID) REFERENCES game(game_UUID) ON DELETE CASCADE,
    PRIMARY KEY (contributor_UUID, game_UUID)
);

CREATE TABLE user_owns_game(
    user_UUID uuid NOT NULL,
    game_UUID uuid NOT NULL,
    rating INT NOT NULL CHECK(rating >= 1 AND rating <=5),
    
    FOREIGN KEY (user_UUID) REFERENCES "user"(user_UUID) ON DELETE CASCADE,
    FOREIGN KEY (game_UUID) REFERENCES game(game_UUID) ON DELETE CASCADE,
    PRIMARY KEY (user_UUID, game_UUID)
);

CREATE TABLE user_plays(
    user_UUID uuid NOT NULL,
    game_UUID uuid NOT NULL,
    played_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    time_played INT NOT NULL DEFAULT 0 CHECK (time_played >= 0),

    FOREIGN KEY (user_UUID) REFERENCES "user"(user_UUID) ON DELETE CASCADE,
    FOREIGN KEY (game_UUID) REFERENCES game(game_UUID) ON DELETE CASCADE,
    PRIMARY KEY (user_UUID, game_UUID, played_at)
);



CREATE VIEW game_listing AS SELECT
    g.game_uuid,
    g.title,
    g.game_description,
    g.esrb_rating,
    g.total_user_rating,
    g.num_of_players,
    MIN(gr.release_date) AS first_release_date,
    EXTRACT(YEAR FROM MIN(gr.release_date))::INT AS release_year,
    MIN(gr.price) AS min_price,
    MAX(gr.price) AS max_price,

    ARRAY_AGG(DISTINCT p.platform_name) AS platforms,
    ARRAY_AGG(DISTINCT ge.genre_name) AS genres,
    ARRAY_AGG(DISTINCT devc.contributor_name) AS developers,
    ARRAY_AGG(DISTINCT pubc.contributor_name) AS publishers,

    (SELECT SUM(up.time_played) FROM user_plays AS up    
    WHERE up.game_uuid = g.game_uuid) AS total_playtime_minutes

    FROM game g
    LEFT JOIN game_release AS gr ON gr.game_uuid = g.game_uuid
    LEFT JOIN platform AS p ON p.platform_uuid = gr.platform_uuid
    LEFT JOIN game_fits_in_genre AS gf ON gf.game_uuid = g.game_uuid
    LEFT JOIN genre AS ge ON ge.genre_uuid = gf.genre_uuid
    LEFT JOIN develops AS d ON d.game_uuid = g.game_uuid
    LEFT JOIN contributor AS devc ON devc.contributor_uuid = d.contributor_uuid
    LEFT JOIN publishes AS pub ON pub.game_uuid = g.game_uuid
    LEFT JOIN contributor AS pubc ON pubc.contributor_uuid = pub.contributor_uuid
    GROUP BY g.game_uuid, g.title, g.game_description, g.esrb_rating, g.total_user_rating, g.num_of_players;
