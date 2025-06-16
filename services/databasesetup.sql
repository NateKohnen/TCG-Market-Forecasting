# Script to create the model of the pokemon tcg database. Run each line of code in order
# for the database to be set up properly.

CREATE DATABASE pokemonTCG;

USE pokemonTCG;

CREATE TABLE sets (
    set_id VARCHAR(20) PRIMARY KEY,
    set_name VARCHAR(100) UNIQUE,
    series VARCHAR(100),
    release_date DATE,
    symbol VARCHAR(255),
    logo VARCHAR(255),
    total_cards INT
);

SELECT * FROM sets;


CREATE TABLE cards (
	card_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100),
    set_id VARCHAR(20),
    rarity VARCHAR(100),
    number INT, 
    small_image VARCHAR(255),
    big_image VARCHAR(255),
    supertype VARCHAR(100),
    tcgplayer_link VARCHAR(255),
    FOREIGN KEY (set_id) REFERENCES sets(set_id)
);

SELECT * FROM cards;

SELECT c.card_id 
            FROM cards c
            WHERE set_id = 'sv1' AND
               c.rarity IN ('Rare Secret', 'Hyper Rare', 'Rare Rainbow', 'Rare Ultra', 
                               'Rare Shiny', 'Shiny Ultra Rare', 'Special Illustration Rare', 
                               'Illustration Rare', 'Trainer Gallery Rare Holo');


# Could be irrelevant now, however will keep in case of future use.
CREATE TABLE tcgplayer_prices (
	listing_id INT AUTO_INCREMENT PRIMARY KEY,
    card_id VARCHAR(20),
    datetime DATETIME,
    low_price DECIMAL(10,2),
    mid_price DECIMAL(10,2),
    high_price DECIMAL(10,2),
    market_price DECIMAL(10,2),
    UNIQUE (card_id, datetime),
    FOREIGN KEY (card_id) REFERENCES cards(card_id)
);

# Still useful for when we want to scrape Ebay listings, regardless of grade or raw.
CREATE TABLE ebay_listings (
	listing_id INT AUTO_INCREMENT PRIMARY KEY,
    card_id VARCHAR(20),
    listing_date DATE,
    title VARCHAR(255),
    listing_price DECIMAL(10,2),
    grade INT,
    url VARCHAR(255),
    isActive BOOLEAN,
    UNIQUE (card_id, listing_date, url),
    FOREIGN KEY (card_id) REFERENCES cards(card_id)
);

CREATE TABLE tcgplayer_sales (
	sale_id INT AUTO_INCREMENT PRIMARY  KEY,
    card_id VARCHAR(20),
    sale_date DATE, 
    sale_price DECIMAL(10,2),
    FOREIGN KEY (card_id) REFERENCES cards(card_id)
);

# establishes relationship between a card and its subtypes. A card can have 1 -> N subtypes.
CREATE TABLE card_subtypes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    card_id VARCHAR(20),
    subtype VARCHAR(100),
    FOREIGN KEY (card_id) REFERENCES cards(card_id)
);

CREATE TABLE tcgplayer_weekly_sales(
	listing_id INT AUTO_INCREMENT PRIMARY KEY,
    card_id VARCHAR(20),
    week DATE,
    num_sold INT,
    min_price  DECIMAL(10, 2),
    max_price DECIMAL(10, 2),	
    week_avg DECIMAL(10, 2),
    UNIQUE(card_id, week),
    FOREIGN KEY (card_id) REFERENCES cards(card_id)
);

DROP TABLE tcgplayer_weekly_sales;
SELECT * FROM tcgplayer_weekly_sales;


# USEFUL QUERIES

SELECT set_id FROM sets WHERE release_date >= '2023-03-23';

# Query to view all card's subtypes.
SELECT c.name, s.subtype, c.card_id FROM cards AS c JOIN card_subtypes AS s ON c.card_id = s.card_id;

# Return all cards of a higher rarity in between 2 certain dates you may specify. 
SELECT c.card_id 
            FROM cards c
            JOIN sets s ON c.set_id = s.set_id 
            WHERE s.release_date >= '2023-03-20' AND
               c.rarity IN ('Rare Secret', 'Hyper Rare', 'Rare Rainbow', 'Rare Ultra', 
                               'Rare Shiny', 'Shiny Ultra Rare', 'Special Illustration Rare', 
                               'Illustration Rare', 'Trainer Gallery Rare Holo');
                               
# Takes a card, displays the set its from as well as its id, and shows the market price compared to the average psa 10 sale.
# FUTURE PROOFING: Have the reference to the ebay-listings table take only the most recent N sales.                   
SELECT 
    c.name,
    s.set_name,
    e.card_id,
    t.market_price,
    ROUND(AVG(e.listing_price), 2) AS mean_price,
    ROUND(STDDEV(e.listing_price), 2) AS price_stdev,
    COUNT(e.listing_price) AS listing_count
FROM 
    ebay_listings e
-- Join cards and sets tables
JOIN 
    cards c ON e.card_id = c.card_id
JOIN 
    sets s ON c.set_id = s.set_id

-- Join tcgplayer_prices table using latest date
JOIN 
    tcgplayer_prices t 
    ON e.card_id = t.card_id
    AND t.datetime = (
        SELECT MAX(datetime)
        FROM tcgplayer_prices
        WHERE card_id = e.card_id
    )
GROUP BY 
    e.card_id, t.market_price
ORDER BY 
    mean_price DESC;
    
SELECT * FROM cards;
