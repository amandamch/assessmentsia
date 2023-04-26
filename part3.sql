-- NB: the names of these files do not correspond to tasks but rather to the order they were used in to accomplish the tasks

CREATE TABLE tvfilms (
    show TEXT,
    year TEXT,
    genre TEXT,
    rating INTEGER,
    description TEXT,
    stars INTEGER,
    votes INTEGER,
    runtime INTEGER,
    gross TEXT
);

.import --csv --skip 1 C:/~/tv_and_film.csv tvfilms 
-- This is the version that I cleaned up for the first tasks
.mode csv
.headers ON
.output C:/~/tv_films_reduced.csv

-- Grouping shows into single instances with rounded ratings, votes, and runtimes
SELECT show, year, genre, ROUND(AVG(rating), 2) AS rating, ROUND(AVG(votes), 2) AS votes, ROUND(AVG(runtime), 2) AS runtime, gross FROM tvfilms
    GROUP BY show;