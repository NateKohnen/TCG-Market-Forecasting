class Card:
    def __init__(self, card_id, connection):
        self.card_id = card_id
        self.name = ""
        self.set_name = ""
        self.number = ""
        self.rarity = ""
        self.tcgplayer_link = ""
        self.load_card_data(connection)

    def load_card_data(self, connection):
        cursor = connection.cursor()

        query = """
        SELECT c.name, s.set_name, c.number, c.rarity, c.tcgplayer_link FROM cards AS c JOIN sets AS s ON c.set_id = s.set_id WHERE c.card_id = %s;
        """

        cursor.execute(query, (self.card_id,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            (self.name,
             self.set_name,
             self.number,
             self.rarity,
             self.tcgplayer_link) = result

        else:
            self.name, self.set_name, self.number, self.rarity, self.tcgplayer_link = None, None, None, None
            

   

    def create_search_query(self):
        search = (self.set_name + "+" + self.name + "+" + self.rarity + "+" + self.number).replace(" ", "+")
        url = "https://www.tcgplayer.com/search/all/product?productLineName=pokemon&q=" + search + "&view=grid&ProductTypeName=Cards&page=1"
        return url

    def keywords(self):
        return [self.name, self.rarity, self.number, self.set_name]
    def __repr__(self):
        return f"Card({self.name}, {self.rarity}, {self.card_id}, {self.set_name}, {self.number})"
