# The first assessment document was missing task 6 and the instruction to present findings in PowerPoint format
# This code relates specifically to performing task 6, the Poisson Regression
# And findings will be presented in a PowerPoint presentation rather than a Word document

import pandas as pd
import numpy as np
import statsmodels.api as sm
import re
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

# Although I cleaned the years for tv_films_reduced.csv, that is not an appropriate dataset to use now, since the average votes for episodes of a TV show are not necessarily integers
# Therefore I need to clean the tv_and_film dataset as I did for tv_films_reduced
# This time I will treat date ranges by start year rather than creating new rows for every year in the date range

df = pd.read_csv('tv_and_film.csv')

drop_rows = []

# Below is roughly the same as in part.py, except that it doesn't create new rows for date ranges
for i in range(len(df)):
    year = re.sub(r"[^0-9]", "", str(df.iloc[i]['year'])) # Remove non-numeric characters
    if len(year) > 4:
        start_date = int(year[:4])
        if start_date <= 2023: # Avoid future releases
            df.at[i, 'year'] = start_date
        else:
            drop_rows.append(i) # Remove future releases
    elif len(year) < 4:
        df.at[i, 'year'] = np.NaN # In case we have an entry like "201" instead of "2014"
    else:
        if int(year) <= 2023:
            df.at[i, 'year'] = int(year)
        else:
            drop_rows.append(i) # Remove future releases

if len(drop_rows) != 0: # This time, we only need to run this code if there are future releases to drop
    for i in drop_rows:
        df.drop([i], axis=0, inplace=True)
    df.reset_index(drop=True, inplace=True)

df['year'] = pd.to_numeric(df['year']) # Making sure all our years are now numeric
df.replace(0, np.nan, inplace=True) # Replacing 0 votes with null, just in case

# The dependent variable is Votes, and I would like to explore the following as independent variables
# - Year
# - Rating
# - Runtime
# - Gross

df = df.drop(columns=['show', 'stars', 'description', 'genre']) # Dropping the text from the df

# One consideration is that Gross is missing loads of values, so if we drop rows with a null, that would reduce the valid data to 460, which is very small!
# I decided to run the model without Gross as an independent variable for the moment, to keep the dataset a reasonable size
# The first issue that encountered was an overflow error in the np.exp function. After a lot of thinking, I realised I could scale the variables so they were on similar scales
# The overflow error made everything 0.000 p-value and Pseudo R-squ was -inf, which can't be right!
# Votes is in the hundreds of thousands or millions, rating is 1-5, runtime is in the tens or hundreds, etc.

scaler = MinMaxScaler()
column_list = ['year', 'rating', 'votes', 'runtime', 'gross']

scaled_df = scaler.fit_transform(df.to_numpy())
scaled_df = pd.DataFrame(scaled_df, columns=[column_list])

y = scaled_df['votes'] # Just the votes column
X = scaled_df[['year','rating', 'runtime', 'gross']]

model = sm.GLM(y, X, missing='drop', family=sm.families.Poisson())
result = model.fit()
print(result.summary())
print('')

# Removing gross so that we can run the regression on more than 445 observations!
X2 = scaled_df[['year','rating', 'runtime']]
model2 = sm.GLM(y, X2, missing='drop', family=sm.families.Poisson())
result2 = model2.fit()
print(result2.summary())

# Decided that the one without gross was more representative of the whole dataset, so am going to go with that one
bins = []
for i in range(20):
    bins.append(i*10)

runtime = df.groupby(['runtime'])['votes'].mean()
fig, ax = plt.subplots()
ax.bar(runtime.index, runtime)
ax.set_xticks(bins)
ax.set_xlim(0, 190)
ax.set_title('Number of Votes According to Runtime of Show')
ax.set_xlabel('Runtime (Minutes)')
ax.set_ylabel('Number of Votes')
plt.show()
# It's not a pretty bar chart but it does show the distribution of votes according to runtime- average number of votes is highest around 180 minutes, increasing exponentially(?) from 0 to that point

# Note: I thought of trying the genre as a dummy variable (code below), like in the logistic regression in the first interview, but I realised that the Poisson Regression doesn't work with zeroes
# A quick google search suggested a zero-inflated Poisson regression may work, but (while maybe doable) it is beyond the scope of the exercise.

# Setting all genres just to be equal to the first genre in the list, and skipping the null values
#for i in range(len(df)):
    #try:
        #df.at[i, 'genre'] = df.iloc[i]['genre'].split(',')[0]
    #except AttributeError:
        #continue

# Create dummy variables for each genre and account for nulls:
#df = pd.get_dummies(df, columns=['genre'], drop_first=True, dummy_na=True, dtype=float)

# Adding dummy variables to label columns in the scaled dataframe:
#for column in df:
    #if 'genre' in column:
        #column_list.append(df[column].name)