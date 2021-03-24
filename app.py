from flask import Flask, render_template, redirect, url_for, request, jsonify

app = Flask(__name__)

@app.route('/')
def pick_match():
	return render_template('choose_match.html')

# Keep the previous scores here in case of a successful challenge or mistake
previous_scores = {
	'federer_sets': 0,
	'federer_games': 0,
	'federer_points': 0,
	'nadal_sets': 0,
	'nadal_games': 0,
	'nadal_points': 0,
	'winner_decided': 'no'
}

# Store match type here (3 Set, 5 Set, or Wimbledon)
match_type = {
	'num_sets': ''
}

@app.route('/play_tennis/', methods=['POST', 'GET'])
def play_tennis(sets=None):
	# Set number of sets (3, 5, Wimbledon) that we're going to play
	new_sets = request.args.get('sets')
	match_type['num_sets'] = new_sets
	
	# Zero out previous scores when a new match is initiated from the choose match screen.
	# We will not hit this route if we complete a game, and will be able to revise a mistake even if a winner is called.
	for key in previous_scores:
		if key != 'winner_decided':
			previous_scores[key] = 0
	previous_scores['winner_decided'] = 'no'
	return render_template('game_screen.html')

# Reset the scores to the previous scores before the mistake/challenge
@app.route('/redo', methods=['POST', 'GET'])
def redo():
	return jsonify(previous_scores)

# Send a JavaScript alert that we have a winner
@app.route('/alert_winner')
def alert_winner():
	previous_scores['winner_decided'] = 'yes'
	return jsonify(previous_scores)

# Assign a point to the correct player and return the correct sets, games, and points for each player
@app.route('/point', methods=['POST', 'GET'])
def point():

	# Get the player who scored and their sets/games/points
	player = request.form['player']
	player_sets = int(request.form['player_sets'])
	player_games = int(request.form['player_games'])
	player_points = request.form['player_points']
	
	# Get the opponent and their sets/games/points
	opponent = request.form['opponent']
	opponent_sets = int(request.form['opponent_sets'])
	opponent_games = int(request.form['opponent_games'])
	opponent_points = request.form['opponent_points']

	# Set previous score to the current score before we add to it
	if player == 'federer':
		# Set player previous points
		previous_scores['federer_sets'] = player_sets
		previous_scores['federer_games'] = player_games
		previous_scores['federer_points'] = player_points

		# Set opponent previous points
		previous_scores['nadal_sets'] = opponent_sets
		previous_scores['nadal_games'] = opponent_games
		previous_scores['nadal_points'] = opponent_points
	# player is nadal
	else:
		# Set player previous points
		previous_scores['federer_sets'] = opponent_sets
		previous_scores['federer_games'] = opponent_games
		previous_scores['federer_points'] = opponent_points

		# Set opponent previous points
		previous_scores['nadal_sets'] = player_sets
		previous_scores['nadal_games'] = player_games
		previous_scores['nadal_points'] = player_points
		

	# Change player points to a number if it isn't Advantage so we can add to it 
	player_points = int(player_points) if player_points != 'Advantage' else player_points
	opponent_points = int(opponent_points) if opponent_points != 'Advantage' else opponent_points

	# Set a variable to tell us if we're in a fifth-set Wimbledon tiebreaker
	wimbledon_tiebreaker = (player_sets == 2 and opponent_sets == 2 and player_games >= 6 and opponent_games >= 6 and
							match_type['num_sets'] == 'Wimbledon')
	
	# Set a variable to tell us if we're in a regular tiebreaker
	regular_tiebreaker = (player_games == 6 and opponent_games == 6 and not wimbledon_tiebreaker)

	# Points are 0 and we aren't in a tiebreaker
	if player_points == 0 and not regular_tiebreaker:
		player_points += 15

	# We're in the tiebreaker, and should increment by 1
	elif player_points == 0 and regular_tiebreaker:
		player_points = int(player_points)
		player_points += 1

	# We're still in the tiebreaker, and should continue to increment by 1
	elif player_points != 0 and regular_tiebreaker:
		player_points = int(player_points)
		player_points += 1

		# Player is up by more than 2 points and has more than 7, winning the tiebreaker
		if player_points >= opponent_points + 2 and player_points >= 7:
			player_points = 0
			opponent_points = 0
			player_games = 0
			opponent_games = 0
			player_sets += 1


	# Points are 15 and we aren't in the tiebreaker (like 15-14 in the tiebreaker)
	elif player_points == 15 and not regular_tiebreaker:
		player_points += 15

	# Points are 30 and we aren't in the tiebreaker (like 30-29 in the tiebreaker)
	elif player_points == 30 and not regular_tiebreaker:
		player_points += 10

	# Points are 40 and we aren't in the tiebreaker (like 40-39 in the tiebreaker)
	elif player_points == 40 and not regular_tiebreaker:
		
		# Player has 40 and will win the game with this point
		if (opponent_points != 40 and opponent_points != 'Advantage'):
			# Reset the game points
			player_points = 0
			opponent_points = 0
			player_games += 1

		# We're at deuce and the player will have 'Advantage'	
		elif (opponent_points == 40):
			player_points = str(player_points)
			player_points = 'Advantage'
		
		# Opponent has the advantage and we return to deuce
		elif (opponent_points == 'Advantage'):
			opponent_points = '40'
			opponent_points = int(opponent_points)

	# Points are 'Advantage' and player wins the game
	elif player_points == 'Advantage':
		player_points = 0
		opponent_points = 0
		player_games += 1

	# Increment sets
	# If we're in a Wimbledon tiebreaker, the winner needs more than six games and to be ahead by more than two games
	if wimbledon_tiebreaker:
		if player_games >= 6 and player_games >= opponent_games + 2:
			player_games = 0
			opponent_games = 0
			player_sets += 1

	# If not in a Wimbledon tiebreaker, the winner needs to have six games and be ahead by two or be winning seven games to six games
	elif wimbledon_tiebreaker == False:
		if (player_games >= 6 and player_games >= opponent_games + 2) or (player_games == 7 and opponent_games == 6):
			player_games = 0
			opponent_games = 0
			player_sets += 1

	# Winner of 3 set match has been decided
	if player_sets == 2 and match_type['num_sets'] == 'ThreeSet':
		return redirect('alert_winner')
	
	# Winner of 5 set match or Wimbledon style has been decided
	elif player_sets == 3 and (match_type['num_sets'] == 'FiveSet' or match_type['num_sets'] == 'Wimbledon'):
		return redirect('alert_winner')

	# Winner not declared, now assign points to the right players
	if player == 'federer':
		# Set player points
		federer_sets = player_sets
		federer_games = player_games
		federer_points = player_points
		# Set opponent points
		nadal_sets = opponent_sets
		nadal_games = opponent_games
		nadal_points = opponent_points
	else:
		# Set player points
		federer_sets = opponent_sets
		federer_games = opponent_games
		federer_points = opponent_points
		# Set opponent points
		nadal_sets = player_sets
		nadal_games = player_games
		nadal_points = player_points
	
	# Return the points to the AJAX call so the HTML can be updated
	return jsonify({
		'federer_sets': federer_sets,
		'federer_games': federer_games,
		'federer_points': federer_points,
		'nadal_sets': nadal_sets,
		'nadal_games': nadal_games,
		'nadal_points': nadal_points,
		'winner_decided': 'no'
	})

if __name__ == '__main__':
	app.run()
