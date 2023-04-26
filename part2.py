# NB: the names of these files do not correspond to tasks but rather to the order they were used in to accomplish the tasks
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import re

df = pd.read_csv('tv_and_film.csv')

# Task 2- plotting histogram of votes
fig1 = plt.figure()
fig1.add_subplot(df['votes'].plot.hist(bins=25)) # This seemed like a good number of bins for the desired effect- tried with 10, 25, and 50, and this looked best
# plt.yscale('log') This would plot the histogram on a log scale, which could tell us more about the distribution of the tail of the data
fig1.suptitle('Histogram of votes per show')

# print(df['votes'].max()) 
# I thought the histogram looked a bit off, so I just double checked to see if this maximum value that plt was giving me was right
# I then ran SELECT show FROM tvfilms WHERE votes = 1713028; in SQLite to make sure this was sensible, and the film was The Fellowship of the Ring, which did seem reasonable to have that many votes

# Task 3: plotting bar charts of subgenres (text has already been preprocessed using SQL)
genres = [{}, {}, {}]
# Doing this, instead of creating three lists, allows us to match the index of text to the index of the dict in genres, which stops us accidentally going out of range if an entry doesn't have 3 genres

for i in range(len(df)):
    try:
        text = df.iloc[i]['genre'].split(',')
        for j in range(len(text)):
            if text[j] not in genres[j].keys():
                genres[j][text[j]] = 1
            else:
                genres[j][text[j]] += 1
    except AttributeError:
        continue

# Extracting each dict and sorting alphabetically
firstGenre = dict(sorted(genres[0].items()))
secondGenre = dict(sorted(genres[1].items()))
thirdGenre = dict(sorted(genres[2].items()))

fig2, axs = plt.subplots(3)
axs[0].bar(range(len(firstGenre)), list(firstGenre.values()))
axs[0].set_xticks(range(len(firstGenre)))
axs[0].set_xticklabels(list(firstGenre.keys()), rotation=90)
axs[0].set_title('First Genre')
axs[1].bar(range(len(secondGenre)), list(secondGenre.values()))
axs[1].set_xticks(range(len(secondGenre)))
axs[1].set_xticklabels(list(secondGenre.keys()), rotation=90)
axs[1].set_title('Second Genre')
axs[2].bar(range(len(thirdGenre)), list(thirdGenre.values()))
axs[2].set_xticks(range(len(thirdGenre)))
axs[2].set_xticklabels(list(thirdGenre.keys()), rotation=90)
axs[2].set_title('Third Genre')

fig2.suptitle('Occurrences of each genre by position')

plt.subplots_adjust(hspace=1)

# This next bit deals with task 4 and uses the csv created with part3.sql
# part3.sql narrows the df size by removing description and starring from the columns (as these cannot be presented as is in a bar chart)
# The multiple instances of TV shows have been averaged in SQL and one row with these averages for every year will be included
# It seems unbalanced that a TV show that ran for, say, 10 years, would only be represented in one of those years on a bar chart

df2 = pd.read_csv('tv_films_reduced.csv')

# print(len(df)) shows us that it's 6243 rows, which is correct according to what we did in SQL before task 1

# The hyphens and brackets were dealt with in SQL to avoid them being accidentally read as sums in Python
# But we still have to trim other text bits out, as some of the "year" info is like "2016 TV Movie" or "II", so we need to handle anything thats not just four digits
# The code below also handles shows that have date ranges: assuming that a tv show's averages over time are a good representation of its performance, they should be counted in every year they aired
# As such, this code identifies date range entries, and creates new entries for each year using the average values, before dropping the original from the dataframe

new_rows = []
drop_rows = []

for i in range(len(df2)):
    year = re.sub(r"[^0-9]", "", str(df2.iloc[i]['year']))
    if len(year) > 4:
        start_date = int(year[:4])
        end_date = int(year[4:])
        if start_date > 2023 or end_date > 2023:
            drop_rows.append(i) # edge case: some dates may be in the future for future releases, so we need to get rid of those
        while start_date != end_date + 1:
            new_row = {'show':df2.iloc[i]['show'], 'year': start_date, 'genre':df2.iloc[i]['genre'], 'rating':df2.iloc[i]['rating'], 'votes':df2.iloc[i]['votes'], 'runtime':df2.iloc[i]['runtime'], 'gross':df2.iloc[i]['gross']}
            new_rows.append(new_row)
            start_date += 1
        drop_rows.append(i)
    elif len(year) < 4:
        df2.at[i, 'year'] = np.NaN # In case we have an entry like "201" instead of "2014"
    else:
        if int(year) <= 2023:
            df2.at[i, 'year'] = int(year)
        else:
            drop_rows.append(i)

new_entries = pd.DataFrame.from_dict(new_rows)
# print(new_entries.head()) shows us that the new dataframe has formed correctly

df2 = pd.concat([df2, new_entries]) # Quicker to create a list of dicts and concat once than it is to concat each time a new row is created
for i in drop_rows:
    df2.drop([i], axis=0, inplace=True) # Dropping the originals with the 8-long number
df2.reset_index(drop=True, inplace=True)

df2['year'] = pd.to_numeric(df2['year']) # The data entered the df as object, and now it's raw numbers we can turn it into numbers to plot
df2.replace(0, np.nan, inplace=True) # To avoid null values being included in means

# Grouping things I want to plot by year
ratings = df2.groupby(['year'])['rating'].mean()
runtime = df2.groupby(['year'])['runtime'].mean()
votes = df2.groupby(['year'])['votes'].mean()
gross = df2.groupby(['year'])['gross'].mean()

# Things I want to plot:
# - Average rating by year
# - Average runtime by year
# - Average votes by year
# - Average gross by year

# However, none of these are appropriately represented by a bar chart, as they show change over time
# The task asks to plot bar charts "that plot properties of the show based on year of telecast" but to me this is time series data that needs plotting as such
# I have the data for genre organised so I will plot this as a separate bar chart- the first four I will provide code for both line graph (commented out) and bar chart
# Other properties of the show that are non-numeric could be presented in tables, such as most popular first genre in each year, or most popular actor/director in each year

fig3, axs = plt.subplots(2, 2)
#axs[0, 0].plot(ratings)
axs[0, 0].bar(ratings.index, ratings)
axs[0, 0].set_title('Average Rating by Year')
#axs[0, 1].plot(runtime)
axs[0, 1].bar(runtime.index, runtime)
axs[0, 1].set_title('Average Runtime by Year')
#axs[1, 0].plot(votes)
axs[1, 0].bar(votes.index, votes)
axs[1, 0].set_title('Average Number of Votes by Year')
#axs[1, 1].plot(gross)
axs[1, 1].bar(gross.index, gross)
axs[1, 1].set_title('Gross ($M) by Year')

fig3.suptitle('Properties of Shows based on Year of Telecast')

#plt.show()

# There are several things that can be done to explore missing data. We'll use the cleaned dataset for this (not cleaned and condensed), as null values are still there in full
# First, how many missing items are there in the whole dataframe?
allEmpties = df.isnull().sum().sum()
print(f'{allEmpties} empty values in table') # 16861 empty values


# Next, how much missing data is there per column? My prediction based on the charts from the previous task is that gross will have the most missing values
for column in df:
    empties = df[column].isnull().sum().sum()
    print(f'{column}: {empties} empty values')
# Gross has 9539 missing values, which is much more than the others. Of 9999 rows, that means only 460 have a gross value, so it probably isn't very reliable to base explorations on
# Show: 0, year: 644, genre: 80, rating: 1820, description: 0, stars: 0, votes: 1820, runtime 2958, gross: 9539

votesAndRating = 0
for i in range(len(df)):
    if pd.isna(df.iloc[i]['rating']) and pd.isna(df.iloc[i]['votes']):
        votesAndRating += 1
print(f"There are {votesAndRating} entries missing both their votes and rating")

suspectedFilms = 0
filmNoGross = 0
missingvotes = {}
missinggenres = {}

for i in range(len(df)):
    if df.iloc[i]['runtime'] > 80: # Assuming most films will be over 1h20 long and few TV episodes are, as a very rough and ready estimate
        suspectedFilms += 1
        if pd.isna(df.iloc[i]['gross']):
            filmNoGross += 1

filmsGross = suspectedFilms - filmNoGross
print(f"There are {suspectedFilms} entries that are over 80 minutes and could be films. Of those, {filmNoGross} are missing a gross and {filmsGross} have an entry.")
# We know that there are only 460 entries with a gross (and 439 have been found here), so it seems that gross only applies to films, and if the other values have a missing runtime, we can still assume they are films

# It would be useful to know if missing genres is a result of record keeping on previous years, as well as if there is a correspondence between years and missing votes
for i in range(len(df2)):
    year = df2.iloc[i]['year']
    if pd.isna(year) == False:
        year = int(year)
        if pd.isna(df.iloc[i]['votes']):
            if year not in missingvotes.keys():
                missingvotes[year] = 1
            else:
                missingvotes[year] += 1
        if pd.isna(df.iloc[i]['genre']):
            if year not in missinggenres.keys():
                missinggenres[year] = 1
            else:
                missinggenres[year] += 1

# Sorting by year to see if there is a trend:
missGenresList = list(missinggenres.keys())
missGenresList.sort()
missinggenres = {i: missinggenres[i] for i in missGenresList}
missVotesList = list(missingvotes.keys())
missVotesList.sort()
missingvotes = {i: missingvotes[i] for i in missVotesList}

fig4, axs = plt.subplots(2)
axs[0].bar(range(len(missinggenres)), list(missinggenres.values()))
axs[0].set_xticks(range(len(missinggenres)))
axs[0].set_xticklabels(list(missinggenres.keys()), rotation=90)
axs[0].set_title('Shows with Missing Genres by Year')
axs[1].bar(range(len(missingvotes)), list(missingvotes.values()))
axs[1].set_xticks(range(len(missingvotes)))
axs[1].set_xticklabels(list(missingvotes.keys()), rotation=90)
axs[1].set_title('Shows with Missing Votes by Year')
fig4.suptitle('Missing Values by Year')
plt.subplots_adjust(hspace=1)

shows = df2.groupby(['year'])['show'].count()
fig5, ax = plt.subplots()
ax.bar(shows.index, shows)
ax.set_title('Number of Shows per Year')

plt.show()