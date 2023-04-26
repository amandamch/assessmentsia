--NB: the names of these files do not correspond to tasks but rather to the order they were used in to accomplish the tasks

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

.headers ON
.import --csv --skip 1 C:/~/tv_and_film.csv tvfilms

SELECT * FROM tvfilms LIMIT 10; -- Just to check that the data was imported correctly, but also noticed that there was a lot of whitespace following the genres

SELECT COUNT(show) FROM tvfilms; -- 9999 rows

UPDATE tvfilms
    SET show = TRIM(show);

SELECT show FROM tvfilms WHERE show LIKE ' %' LIMIT 10; -- Ran this before and after, and the update has worked- there are no more whitespace issues in this column

UPDATE tvfilms
    SET genre = TRIM(REPLACE(genre, ', ', ','));
UPDATE tvfilms
    SET genre = REPLACE(genre, CHAR(10), '');
UPDATE tvfilms
    SET genre = REPLACE(genre, CHAR(13), ''); -- These statements could be nested but I find this more readable

SELECT genre FROM tvfilms LIMIT 10; -- Confirming ll whitespace, newlines, and carriage returns removed- this will make splitting the genres easier later

-- Also want to clean the release years a little- I don't want any minuses or brackets to be read as sums or negative values
UPDATE tvfilms
    SET year = REPLACE(year, '(', '');
UPDATE tvfilms
    SET year = REPLACE(year, ')', '');
UPDATE tvfilms
    SET year = REPLACE(year, '-', '');
UPDATE tvfilms
    SET year = REPLACE(year, CHAR(8211), '');
UPDATE tvfilms
    SET year = TRIM(year);
-- I was wondering why the hyphen on my keyboard was only working for some of the dates and not others but I remembered this really arcane piece of knowledge I had from editing an academic article where they wanted the hyphens replaced with en dashes
-- en-dashes and hyphens are identical in most fonts (including the SQL terminal)
-- but SQLite was reading any hyphens following numbers as en dashes and not hyphens (which it reads as a minus), and CHAR(8211) is the only way to access these characters
-- The other thing to deal with is that some columns have "2016 TV Movie" and things, so we need to get rid of anything that's non-numeric, but I can do that with regexes in Python
-- But given en dashes are variably read as minuses and vice versa, it makes sense to get rid of all of them now so we don't have problems later

UPDATE tvfilms
    SET votes = REPLACE(votes, ',', ''); -- To make sure that votes is read by Python as numeric rather than a string

UPDATE tvfilms
    SET gross = REPLACE(gross, '$', '');
UPDATE tvfilms
    SET gross = REPLACE(gross, 'M', ''); -- To be able to read gross as a decimal and not text in Python

SELECT COUNT(DISTINCT show) FROM tvfilms;

-- We have 6423 unique shows, meaning that if we are plotting properties of a show, we need to avoid repeats of a show's telecast, etc.
-- Need to know if I can combine the shows now, or if the genres are different for each instance of the show
SELECT * FROM tvfilms
    WHERE show LIKE 'Avatar%';
-- Title and genre are the same, but the number of votes, rating, and description are different, and it looks like each instance is a rating for a different episode
-- So we won't combine them at the moment, but that's a useful thing to know when looking at the ratings

.mode csv
.output C:/~/tv_and_film.csv

SELECT * FROM tvfilms;

.quit