library(dplyr)
library(tidyr)

# Animes
animes <- read.csv('data/raw/anime.csv', header = TRUE, stringsAsFactors = FALSE)
print(head(animes))

# There are two rows with different ids, but the same name. This seems to be a mistake
# in the data collection phase, so we'll remove them.
animes <- animes[!duplicated(animes$name),]

# Turn episodes column into an int column, and the "Unknown" values into NA values
animes$episodes[animes$episodes == "Unknown"] <- NA
animes$episodes <- as.numeric(animes$episodes)

# Create file of unique anime ids, for web scraping
unique_ids <- unique(animes$anime_id)

fOut <- file("data/clean/anime_ids.txt")
write.csv(unique_ids, fOut, row.names = FALSE) # one id per line
close(fOut)

# Normalize the data by splitting genres into a separate table
genre_df <- data.frame(anime_id = animes$anime_id, genre = animes$genre, stringsAsFactors=FALSE)
genre_df <- genre_df %>% unnest(genre = strsplit(genre, ","))
genre_df$genre <- trimws(genre_df$genre)
fOut <- file('data/clean/genres.csv')
write.csv(genre_df, fOut, row.names = FALSE)
close(fOut)

# Print out the animes table left over
animes$genre <- NULL
fOut <- file('data/clean/animes.csv')
write.csv(animes, fOut, row.names = FALSE)
close(fOut)

# Ratings
ratings <- read.csv('/home/noah/Downloads/anime-recommendations-database/rating.csv', header = TRUE)

# Filter the raw data so that we only keep rows where the user gave the anime a rating
# (MAL ratings are between 1 and 10)
clean_ratings <- ratings %>% filter(1 <= rating & rating <= 10)
fOut <- file('data/raw/no_null_ratings.csv')
write.csv(clean_ratings, fOut, row.names = FALSE)
close(fOut)
