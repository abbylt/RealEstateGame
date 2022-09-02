# Author: Abby Thornton
# GitHub username: abbylt
# Date: 05/30/2022
# Description: The back end framework for a board game where the players move around a board buying property and paying
# rent to one another. Classes include RealEstateGame, Player, and GameSpace.

class RealEstateGame:
    """
    Runs the game itself
    Communicates with Player and Property classes
    ____________
    Attributes
    ____________
    self._active_players: Dictionary of Player objects representing players in the game; initialized to an empty
                    dictionary
    self._game_board: List of GameSpaces representing the game spaces on the board; initialized to an empty list
    ________
    Methods
    ________
    init:           Creates an instance of the RealEstateGame class
    create_spaces:  Initializes the game board
    create_player:  Initializes a new player
    get_player_account_balance: Returns the player's current account balance
    get_player_current_position: Returns the player's current position on the game board
    buy_space:      Player buys the game space they are currently on, if possible
    move_player:    Moves the player around the board a number of spaces as indicated by the parameter, as long as they
                    are active. If the player passes GO, they collect money. If they land on a space owned by another
                    player, they pay as much rent as possible. If their balance is zero at the end of their turn, they
                    lose the game.
    movement:       Move the player around the board a number of spaces equal to spaces_to_move parameter2
    pass_go:        Player receives the amount of money indicated by the GO space
    pay_rent:       Player pays as much rent to the game space owner as their account balance will allow.
    lose_game:      Player is removed as owner from all properties owned
    check_game_over: Evaluates the list of active players. If there is only one, then that player is returned as winner.
    get_list_of_player_owned_spaces: List of game spaces owned by the player
    """
    def __init__(self):
        """
        Create an instance of the RealEstateGame class
        """
        self._game_board = []
        self._players = {}

    def create_spaces(self, go_money, rent_list):
        """
        Add 25 spaces to the self._game_board list with each a dictionary with the key being a number between 0 and 24
        and the value a GameSpace class instance
        :param go_money: the amount of money players will receive for landing on or passing the GO space
        :param rent_list: a list of integers that will be assigned as the rent amounts for each of the game spaces,
        except the GO space, which has the amount the players will receive for landing on/passing GO
        """
        self._game_board.append({0: GameSpace('GO', go_money)})
        game_space_indices = range(1, 25)
        for num, rent in zip(game_space_indices, rent_list):
            self._game_board.append({num: GameSpace(num, rent)})

    def create_player(self, player_name, starting_account_balance):
        """
        Add a new player to the self._active_players dictionary where the key is player_name and the value is
        a Player class instance
        :param player_name: name of player
        :param starting_account_balance: integer representing the starting account balance for the player
        :return: prints an error message if the player name is already in use
        """
        if player_name in self._players:
            print("Player was not added to the game as this name is already in use.")
            return
        self._players[player_name] = Player(player_name, starting_account_balance)

    def get_player_account_balance(self, player_name):
        """
        Return the player's current account balance
        :param player_name: name of player
        :return: current account balance for player_name
        """
        player_obj = self._players[player_name]
        return player_obj.get_current_account_balance()

    def get_player_current_position(self, player_name):
        """
        Return the player's current position on the game board
        :param player_name: name of player
        :return: integer representing the game space player_name is current on
        """
        player_obj = self._players[player_name]
        return player_obj.get_location()

    def buy_space(self, player_name):
        """
        If the player is active, the space is unowned/not the GO space, and the player's account balance is greater
        than the space's purchase price, the player buys the space:
            Purchase price is deducted from the player's account balance
            The name of space is added to player's list of owned spaces
            The player's name added as the game space's owner
        :param player_name: name of player
        :return: True if the player was able to buy the space, False if not
        """
        player_obj = self._players[player_name]
        player_acct_bal = player_obj.get_current_account_balance()
        current_space = self._game_board[player_obj.get_location()][player_obj.get_location()]
        current_space_owner = current_space.get_game_space_owner()
        purchase_price = current_space.get_purchase_price()
        space_name = current_space.get_game_space_name()

        # check if the player is inactive, the space is owned, the space is GO, or the player's account balance is less
        # than or equal to the space's purchase price
        if self.get_player_account_balance(player_name) == 0 or current_space_owner is not None or space_name == 'GO' \
                or player_acct_bal <= purchase_price:
            return False

        # initiate the purchase
        player_obj.withdraw(purchase_price)  # pay purchase price
        player_obj.buy_game_space(space_name)  # add space name to player's list of owned spaces
        current_space.set_game_space_owner(player_name)  # add player name as space's owner
        return True

    def move_player(self, player_name, spaces_to_move):
        """
        Move the player around the board a number of spaces equal to spaces_to_move parameter, if they are active.
        Increase player account balance by designated amount if player passes or lands on GO.
        Determine ownership of space landed on if it is not GO, and pay rent if owned.
        Player loses game if their account balance is zero at the end of the turn.
        :param player_name: name of player
        :param spaces_to_move: integer representing the number of spaces the player should advance around the game board
        """
        # check if player is inactive
        if self.get_player_account_balance(player_name) == 0:
            return

        # move player to new position, pay out if pass/land on GO
        self.movement(player_name, spaces_to_move)

        # check ownership of new location and pay rent, if needed
        self.pay_rent(player_name)

    def movement(self, player_name, spaces_to_move):
        """
        Move the player around the board a number of spaces equal to spaces_to_move parameter
        :param player_name: name of player
        :param spaces_to_move: integer representing the number of spaces the player should advance around the game board
        :return:
        """
        player_obj = self._players[player_name]
        player_location = player_obj.get_location()
        move = player_location + spaces_to_move

        # move player to new position
        if move < len(self._game_board) - 1:
            player_obj.set_location(move)
        else:
            new_location = move % len(self._game_board)
            player_obj.set_location(new_location)
            self.pass_go(player_name)

    def pass_go(self, player_name):
        """
        Increase the account balance of player_name by the amount associated with the GO space
        :param player_name: name of player
        """
        go_price = self._game_board[0][0].get_rent()
        player_obj = self._players[player_name]
        player_obj.deposit(go_price)

    def pay_rent(self, player_name):
        """
        Player_name pays rent to the owner of the game space they are currently located on
        If rent is greater than player_name's account balance, they pay as much as possible and lose the game
        :param player_name: name of player
        """
        player = self._players[player_name]
        bal = self.get_player_account_balance(player_name)
        location_obj = self._game_board[self.get_player_current_position(player_name)][self.get_player_current_position(player_name)]
        rent = location_obj.get_rent()
        owner = location_obj.get_game_space_owner()

        if owner is None or owner == 'GO':
            return

        owner_obj = self._players[owner]

        # compare rent to player account balance
        if rent < bal:
            player.withdraw(rent)
            owner_obj.deposit(rent)
            return
        player.withdraw(bal)
        owner_obj.deposit(bal)
        self.lose_game(player_name)

    def lose_game(self, player_name):
        """
        Player_name is removed as owner from all properties owned
        :param player_name:
        """
        player_obj = self._players[player_name]
        owned_spaces = player_obj.get_owned_game_spaces()

        # remove player name from games spaces in player's owned spaces list
        for space_name in owned_spaces:
            space_obj = self._game_board[space_name][space_name]
            space_obj.remove_game_space_owner()

        # remove games spaces from player's list of owned spaces
        player_obj.clear_owned_game_spaces()

    def check_game_over(self):
        """
        Evaluates the players list to see how many players are there
        :return: the name of the player if there is only one in the list, otherwise an empty string
        """
        counter = 0
        winner = None
        for dict_entry in self._players:
            player_obj = self._players[dict_entry]
            if player_obj.get_current_account_balance() == 0:
                counter += 1
            else:
                winner = player_obj.get_player_name()
        return winner if counter == 1 else ""

    def get_list_of_player_owned_spaces(self, player_name):
        """
        List of game spaces owned by the player
        :param player_name: name of player
        :return: a list of the names of the game spaces owned by the player
        """
        player_obj = self._players[player_name]
        return player_obj.get_owned_game_spaces()


class Player:
    """
    Creates an instance of a player
    ___________
    Attributes
    ___________
    self._player_name: name of player; initialized to player_name parameter
    self._account_balance: integer representing the player's current account balance; initialized to
                            starting_account_balance parameter
    self._current_location: the name of the game space the player is currently located on; initialized to "GO"
    self._owned_game_spaces: a list of the names of the game spaces owned by the player; initialized to an empty list
    _________
    Methods
    _________
    init: Create an instance of the Player class
    get_player_name: Returns the player's name
    get_current_account_balance: Returns the current account balance for the player
    deposit: Increment the player's account balance
    withdraw: Decrement the player's account balance
    set_location: Change the player's current location to game_space_name
    get_location: Return the name of the game space the player is located on
    buy_game_space: Add game_space_name to the player's list of owned game spaces
    clear_owned_game_spaces: Reset self._owned_game_spaces to an empty list
    """
    def __init__(self, player_name, starting_account_balance):
        """
        Create an instance of the player class
        :param player_name: name of the player
        :param starting_account_balance: the player's starting account balance
        """
        self._player_name = player_name
        self._account_balance = starting_account_balance
        self._current_location = "GO"
        self._owned_game_spaces = []

    def get_player_name(self):
        """
        Returns the player's name
        :return: the player's name
        """
        return self._player_name

    def get_current_account_balance(self):
        """
        Returns the current account balance for the player
        :return: the current account balance for the player
        """
        return self._account_balance

    def deposit(self, amount):
        """
        Increment the player's account balance
        :param amount: amount to increment
        """
        self._account_balance += amount

    def withdraw(self, amount):
        """
        Decrement the player's account balance
        :param amount: amount to decrement
        """
        self._account_balance -= amount

    def set_location(self, game_space_name):
        """
        Change the player's current location to game_space_name
        :param game_space_name: the name of a game space
        """
        self._current_location = game_space_name

    def get_location(self):
        """
        Return the name of the game space the player is located on
        :return: the name of the game space the player is located on
        """
        if self._current_location == "GO":
            return 0
        return self._current_location

    def get_owned_game_spaces(self):
        """
        Return a list of the game spaces the player currently owns
        :return: a list of the game spaces the player currently owns
        """
        return self._owned_game_spaces

    def buy_game_space(self, game_space_name):
        """
        Add game_space_name to the player's list of owned game spaces
        :param game_space_name: name of a game space
        """
        self._owned_game_spaces.append(game_space_name)

    def clear_owned_game_spaces(self):
        """
        Reset self._owned_game_spaces to an empty list
        """
        self._owned_game_spaces = []


class GameSpace:
    """
    Creates an instance of a space on a game board
    ___________
    Attributes
    ___________
    self._game_space_name: the name of the game space; initialized to game_space_name parameter
    self._rent: the rent price for the game space; initialized to rent parameter
    self._purchase_price: the purchase price for the game space; initialized to 5 times the rent parameter
    self._game_space_owner: the name of the player who has purchased the game space; initialized to None
    _________
    Methods
    _________
    init: Create an instance of the GameSpace class
    get_game_space_name: Return the name of the game space
    get_rent: Returns the rent price of the game space
    get_purchase_price: Returns the purchase price of the game space
    get_game_space_owner: Returns the player name of the owner of the game space
    set_game_space_owner: Sets the player_name parameter as the owner of the game space
    remove_game_space_owner: Sets the game space owner to None
    """
    def __init__(self, game_space_name, rent):
        """
        Create an instance of the GameSpace class
        :param game_space_name: the name of the game space
        :param rent: the purchase/rent price for the game space
        """
        self._game_space_name = game_space_name
        self._rent = rent
        self._purchase_price = rent * 5
        self._game_space_owner = None

    def get_game_space_name(self):
        """
        Return the name of the game space
        :return: the name of the game space
        """
        return self._game_space_name

    def get_rent(self):
        """
        Returns the rent price of the game space
        :return: the rent price of the game space
        """
        return self._rent

    def get_purchase_price(self):
        """
        Returns the purchase price of the game space
        :return: the purchase price of the game space
        """
        return self._purchase_price

    def get_game_space_owner(self):
        """
        Returns the player name of the owner of the game space
        :return: the player name of the owner of the game space
        """
        return self._game_space_owner

    def set_game_space_owner(self, player_name):
        """
        Sets the player_name parameter as the owner of the game space
        :param player_name: name of the player
        """
        self._game_space_owner = player_name

    def remove_game_space_owner(self):
        """
        Sets the game space owner to None
        """
        self._game_space_owner = None
