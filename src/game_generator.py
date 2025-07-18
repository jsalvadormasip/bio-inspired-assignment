import numpy as np
#only the grande mode for now. 
class GameGenerator:
    def __init__(self, winscore = 30, point_per_bet = 2):
        self.card_deck = np.array(['1', '2', '3', '4', '5', '6', '7', '10', '11', '12']).repeat(4)
        self.full_card_deck = self.card_deck.copy()
        print("GameGenerator initialized with card deck:", self.card_deck)
        self.shuffle_deck()
        print("Card deck shuffled:", self.card_deck)
        self.player_hands = np.empty((2, 4), dtype='<U2')
        print("Player hands initialized:", self.player_hands)
        self.deal_cards()
        self.winscore = winscore
        self.point_per_bet = point_per_bet
        self.player_scores = np.zeros(2, dtype=int)
        self.play_game()
    def shuffle_deck(self):
        np.random.shuffle(self.card_deck)
        
    def deal_cards(self):
        for i in range(2):
            for j in range(4):
                self.player_hands[i,j] = self.card_deck[i * 4 + j]
        print("Cards dealt to players:", self.player_hands)
        self.card_deck = np.delete(self.card_deck, np.arange(8))  # Remove dealt cards
        print("Remaining card deck after dealing:", self.card_deck)
    
    def play_game(self):
        round_number = 1
        while np.all(self.player_scores < self.winscore):
            actions = np.empty(2, dtype='<U4')
            player_order = [0,1]
            if round_number % 2 == 0:
                player_order.reverse()
            for player in player_order:
                print(f"Player {player + 1}'s turn. Your hand: {self.player_hands[player]}")
                action = input("Do you want to 'Bet' or 'Pass'? ").strip().lower()
                
                while action not in ['bet', 'pass']:
                    action = input("Invalid input. Please enter 'Bet' or 'Pass': ").strip().lower()
                actions[player] = action
                print(f"Player {player + 1} chose to {action.capitalize()}.")
            if np.all(actions == 'bet'):
                print("Both players bet. Calculating scores...")
                self.calculate_round_winner(hands = self.player_hands)
                # Here you can implement the logic for betting
            elif actions[player_order[0]] == 'bet' and actions[player_order[1]] == 'pass':
                print(f"Player {player_order[0] + 1} bets, Player {player_order[1] + 1} passes. Player {player_order[0] + 1} wins half a round worth of points!")
                self.player_scores[player_order[0]] += self.point_per_bet // 2
            
            # uncomment this if pass-bet confirm logic is needed (e.g. for when betting can be increased)
            # and then comment the elif below
            
            # elif actions[player_order[0]] == 'pass' and actions[player_order[1]] == 'bet':
            #     print(f"Player {player_order[0] + 1} passes, Player {player_order[1] + 1} bets. Player {player_order[0] +1} do you want to bet too? (yes/no)")
            #     response = input().strip().lower()
            #     while response not in ['yes', 'no']:
            #         response = input("Invalid input. Please enter 'yes' or 'no': ").strip().lower()
            #     if response == 'yes':
            #         self.calculate_round_winner(hands=self.player_hands)
            #     else:
            #         print(f"Player {player_order[0] + 1} passes. Player {player_order[1] + 1} wins half a round worth of points!")
            #         self.player_scores[player_order[1]] += self.point_per_bet // 2
            
            elif actions[player_order[1]] == 'bet' and actions[player_order[0]] == 'pass':
                print(f"Player {player_order[1] + 1} bets, Player {player_order[0] + 1} passes. Player {player_order[1] + 1} wins half a round worth of points!")
                self.player_scores[player_order[1]] += self.point_per_bet // 2
            else: #both players passed
                print("Both players passed. Half a round worth of points awarded to better hand. ")
                self.calculate_round_winner(hands=self.player_hands, bothpass=True)
            print("Current scores:", self.player_scores)
            self.card_deck = self.full_card_deck.copy()  # Reset the deck for the next round
            self.shuffle_deck()
            self.deal_cards()
            round_number += 1
        print("Game over! Final scores:", self.player_scores)
    def calculate_round_winner(self, hands, bothpass = False):
        if bothpass:
            pointperbet = self.point_per_bet // 2
        else:
            pointperbet = self.point_per_bet
        player1_hand = hands[0]
        player2_hand = hands[1]
        card_values = ['12', '11', '10', '7', '6', '5', '4', '3', '2', '1']
        player1_score = 0
        player2_score = 0
        for value in card_values:
            count1 = np.count_nonzero(player1_hand == value)
            count2 = np.count_nonzero(player2_hand == value)
            if count1 > count2:
                player1_score = 1
                player2_score = 0
                break
            elif count2 > count1:
                player1_score = 0
                player2_score = 1
                break
        # If all counts are equal, scores remain 0 (tie)
        if player1_score > player2_score:
            print("Player 1 wins the round!")
            self.player_scores[0] += pointperbet
        elif player2_score > player1_score:
            print("Player 2 wins the round!")
            self.player_scores[1] += pointperbet
        else:
            print("It's a tie! Winner is the hand (player 1), fix this later. ")
            self.player_scores[0] += pointperbet