# Music Genre Categorization

### Music Genre Categorization

Music genre categorization involves grouping musical items based on shared characteristics, facilitating applications such as song recommendation (e.g. Spotify). However, these categories are not always mutually exclusive, and songs can often belong to multiple genres, suggesting that genre definitions can be subjective and broad (e.g. Pop, Rock). As such, research aims to classify music into multiple, fine-grained labels.

Traditional approaches to music genre classification often rely on audio features, employing pattern recognition algorithms to classify feature vectors extracted from short-time recording segments (e.g. Support Vector Machines (SVMs), Nearest-Neighbor (NN) classifiers, Gaussian Mixture Models, and Linear Discriminant Analysis (LDA)). For example, one project classified songs into genre classes using Mel-frequency cepstral coefficients (MFCCs) (Author, Year). The Mel scale discerns the human ear’s response to the Hz scale. The Marsyas 1000 song data set, consisting of ten genres each with 100 songs, was used. The data set was analyzed for 1 and 15 second intervals, segmented into 20ms chunks. Principal Component Analysis (PCA) was applied to reduce dimensionality. Algorithms were run on original mels, normalized mels, PCA basic mels and PCA map eigenvectors. The study focused on {classical, metal, pop}, and {classical, country, metal, pop} genre sets. Euclidean distance and Kullback-Lieber (KL) Divergence were used as distance metrics.

More recently, researchers have explored text-based approaches, utilizing lyrics or album reviews for genre classification. One study treated music as a text-like document, representing it with music symbol lexicons derived from Hidden Markov Model (HMM) clustering (Author, Year). Latent semantic indexing (LSI) was then used for genre classification, similar to text categorization.

Several datasets are used in music genre classification research. The GTZAN dataset is a commonly used dataset for music genre classification (Author, Year). The Million Song Dataset (MSD) is another dataset used for large-scale data mining of music information (Author, Year). One study used a subset of 156,289 songs from the MSD, categorized into 10 genres derived from MusicBrainz tags: classic pop and rock, classical, dance and electronica, folk, hip-hop, jazz, metal, pop, rock and indie, and soul and reggae (Author, Year). The MuMu dataset contains 31k albums classified into 250 genre classes (Author, Year). Amazon's music genre taxonomy has 27 genres in the first level and almost 500 overall (Author, Year).


## References

1. SOURCE: FauciCastSchulze-MusicGenreClassification.pdf
2. SOURCE: FauciCastSchulze-MusicGenreClassification.pdf
3. SOURCE: qibin2006_mmsp.pdf
4. SOURCE: qibin2006_mmsp.pdf
5. SOURCE: report003.pdf
6. SOURCE: report003.pdf
7. SOURCE: FINAL.pdf
8. SOURCE: FINAL.pdf
9. SOURCE: ismir2017.pdf
10. SOURCE: ismir2017.pdf
