import numpy as np
#things to change: si el otro pasa, y tu envias, te lo quedas directo jaja. 
# hacer que el agente muy simple sepa la accion del otro si se puede. 
class MusEnv:
    def __init__(self, number_of_cards=4):
        self.number_of_cards = number_of_cards
        # self.deck = list(range(1, 41))  # Simplified 40-card deck
        self.deck = np.arange(1,11,1).repeat(self.number_of_cards)
        self.full_card_deck = self.deck.copy()
        # print("GameGenerator initialized with card deck:", self.card_deck)
        self.shuffle_deck()
        self.point_per_bet = 1
        self.turn = 0 # 0 for player, 1 for opponent
        self.mode = "test"  # Can be "train" or "test"
        self.second_chance = False
        self.opponent_second_chance = False
        self.opponent_second_chance_completed = False
    def reset(self):
        self.opponent_action = np.nan
        self.deck = self.full_card_deck.copy()
        self.shuffle_deck()
        self.hand = self._deal_hand()
        self.opponent_hand = self._deal_hand()  # Random, not seen
        if self.mode == "test":
            print("Dealt hand:", self.opponent_hand)
        self.history = []
        self.done = False
        self.turn = np.random.choice([0, 1])  # Randomly choose who starts
        self.second_chance = False
        self.opponent_second_chance = False
        self.opponent_second_chance_completed = False
        return self._get_state()
    def shuffle_deck(self):
        np.random.shuffle(self.deck)

    def step(self, action):
        # action = 0: fold, 1: pass, 2: bet small, 3: bet big
        if self.mode == "test":
            print(f"Action taken by machine: {action}")
            if action == 1:
                print("Machine bet")
            else:
                print("Machine folded")
        reward, self.done = self._resolve_action(action)
        if self.mode == "test":
            
            if reward >0:
                print("Machine wins the round!, machine hand: ", self.hand)
            elif reward < 0:
                print("Human wins the round!, machine hand: ", self.hand)       
        
        return self._get_state(), reward, self.done

    def _deal_hand(self):
        player_hands = np.zeros((self.number_of_cards))
        player_hands = self.deck[:self.number_of_cards]  # Deal 4 cards
        # print("Cards dealt to player:", player_hands)
        self.deck = np.delete(self.deck, np.arange(self.number_of_cards))  # Remove dealt cards
        # print("Remaining card deck after dealing:", self.card_deck)
        return player_hands
    def _opponent_decision(self):
        if not np.isnan(self.opponent_action):
            if not self.opponent_second_chance:
                return self.opponent_action
            if self.opponent_second_chance_completed:
                return self.opponent_action
        
        # print(np.sort(self.opponent_hand)[-1])
        if self.mode == "train":
            if np.sort(self.opponent_hand)[-1] >8:
                opponent_action = 1
            else:
                opponent_action = 0
        elif self.mode == "test":
            opponent_action = int(input("Enter action (0: fold, 1: bet): "))
        self.opponent_action = opponent_action
        if self.opponent_second_chance:
            self.opponent_second_chance_completed = True
        return opponent_action

    def _get_state(self):
        # Simple encoding: sorted cards + encoded history
        
        hand_encoding = np.sort(self.hand)
        hand_encoding = hand_encoding[::-1] #sort from big to small. 
        # state = hand_encoding[0]*1000 + hand_encoding[1]*100 + hand_encoding[2]*10 + hand_encoding[3]
        if self.turn == 1:
            # if self.mode == "test":
            #     # print("Repeat your decision, the code is not perfect yet.")
            if self._opponent_decision() == 1:
                # state += 20000
                opp_state = 2
            elif self._opponent_decision() == 0:
                # state += 0
                opp_state = 0
        else:
            if self.mode == "test":
                print("Machine's turn, please wait.")
            # state +=10000
            opp_state = 1
        state = (tuple(hand_encoding), opp_state)  # Use tuple for state representation
        
        # history_encoding = np.zeros(4)  # Add your own logic here
        return state

    def _resolve_action(self, action):
        # Simplified game outcome logic (can start with random)
        # Return reward, done
        # if self.mode == "test" and self.turn == 1:
            # print("Please repeat the decision, the code is not perfect yet.")
        opponent_action = self._opponent_decision()
        reward = 0
        if action == 0 and opponent_action == 0:
            reward  = self.calculate_round_winner(hands = np.array([self.hand, self.opponent_hand]), bothpass=True)
            return reward, True       
        elif action == 0 and opponent_action == 1 and self.turn == 0:
            if self.second_chance == True:
                reward = -self.point_per_bet // 2
                return reward, True
            return 0, False
            # reward = -self.point_per_bet // 2
        elif action ==0 and opponent_action ==1 and self.turn ==1:
            reward = -self.point_per_bet // 2
            return reward, True
        elif action == 1 and opponent_action == 0 and self.turn ==0:
            reward = self.point_per_bet // 2
            return reward, True
        elif action == 1 and opponent_action == 0 and self.turn ==1:
            opponent_action = self._opponent_decision()
            if self.opponent_second_chance:
                reward  = self.point_per_bet //2 
                return reward, True
            self.opponent_second_chance = True
            return 0, False
            # if opponent_action ==1: 
            #     reward = self.calculate_round_winner(hands = np.array([self.hand, self.opponent_hand]), bothpass=False)
            # else:
            #     reward = self.point_per_bet // 2
            # return reward, True
        elif action == 1 and opponent_action == 1:
            reward = self.calculate_round_winner(hands = np.array([self.hand, self.opponent_hand]), bothpass=False)
            return reward, True

    def calculate_round_winner(self, hands, bothpass = False):
        if bothpass:
            pointperbet = self.point_per_bet // 2
        else:
            pointperbet = self.point_per_bet
        player1_hand = hands[0]
        player2_hand = hands[1]
        card_values = np.arange(1,11,1)
        card_values = card_values[::-1]
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
            reward = pointperbet
        elif player2_score > player1_score:
            reward = -pointperbet
        else:
            # print("It's a tie! Winner is the hand (player 1), fix this later. ")
            reward = 0
        return reward