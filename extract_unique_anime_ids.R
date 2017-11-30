animes <- read.csv('data/anime.csv', header = TRUE)

print(head(animes))

unique_ids <- unique(animes$anime_id)

fOut <- file("data/anime_ids.txt")
write(unique_ids, fOut, ncolumns = 1)
close(fOut)
