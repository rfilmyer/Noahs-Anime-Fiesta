library(dplyr)

# Animes
animes <- read.csv('data/raw/anime.csv', header = TRUE)

print(head(animes))

# Create file of unique anime ids, for web scraping
unique_ids <- unique(animes$anime_id)

fOut <- file("data/clean/anime_ids.txt")
write(unique_ids, fOut, ncolumns = 1) # one id per line
close(fOut)

# Normalize the data by splitting genres into a separate table
genres <- data.frame()

# Ratings
ratings <- read.csv('/home/noah/Downloads/anime-recommendations-database/rating.csv', header = TRUE)

# Filter the raw data so that we only keep rows where the user gave the anime a rating
# (MAL ratings are between 1 and 10)
clean_ratings <- ratings %>% 
fOut <- file('/home/noah/Downloads/anime-recommendations-database/clean_ratings.csv')
write(ratings_clean, fOut, ncolumns = length(ratings))
close(fOut)