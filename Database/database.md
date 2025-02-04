```mermaid
erDiagram
    Ratings {
        int RatingID
        int UserID
        int MovieID
        int Rating
        int Timestamp
    }


    Movies {
        int MovieID
        string Title
        string Genres
        int Year
    }

    Movies only one to zero or more Ratings : ""

    
```