animes <- read.csv('data/anime.csv', header = TRUE)

print(head(animes))

unique_ids <- unique(animes$anime_id)

fOut <- file("data/output.txt")
writeLines(unique_ids, fOut)
close(fOut)
