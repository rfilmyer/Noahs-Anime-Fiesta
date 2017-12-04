library(dplyr)
library(tidyr)

# Animes
animes <- read.csv('data/raw/anime.csv', header = TRUE)
animes$genre <- as.character(animes$genre)
print(head(animes))

# Create file of unique anime ids, for web scraping
unique_ids <- unique(animes$anime_id)

fOut <- file("data/clean/anime_ids.txt")
write.csv(unique_ids, fOut, ncolumns = 1) # one id per line
close(fOut)

# Normalize the data by splitting genres into a separate table
genre_df <- data.frame(id = animes$anime_id, genre = animes$genre, stringsAsFactors=FALSE)
genre_df <- genre_df %>% unnest(genre = strsplit(genre, ","))
genre_df$genre <- trimws(genre_df$genre)
fOut <- file('data/clean/genres.csv')
write.csv(genre_df, fOut, row.names = FALSE)
close(fOut)

# Ratings
ratings <- read.csv('/home/noah/Downloads/anime-recommendations-database/rating.csv', header = TRUE)

# Filter the raw data so that we only keep rows where the user gave the anime a rating
# (MAL ratings are between 1 and 10)
clean_ratings <- ratings %>% filter(1 <= rating & rating <= 10)
fOut <- file('data/raw/no_null_ratings.csv')
write.csv(clean_ratings, fOut, row.names = FALSE)
close(fOut)
