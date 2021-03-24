$(document).ready(function() {

    $('.pointButton').on('click', function() {

        // Find out the player and their sets/games/points
        var player = ($(this).attr('player') == 'federer') ? 'federer' : 'nadal';
        var player_sets = (player == 'federer') ? $('#federer_sets').text() : $('#nadal_sets').text();
        var player_games = (player == 'federer') ? $('#federer_games').text() : $('#nadal_games').text();
        var player_points = (player == 'federer') ? $('#federer_points').text() : $('#nadal_points').text();

        // Do the same for the opponent
        var opponent = (player == 'federer') ? 'nadal' : 'federer';
        var opponent_sets = (player == 'nadal') ? $('#federer_sets').text() : $('#nadal_sets').text();
        var opponent_games = (player == 'nadal') ? $('#federer_games').text() : $('#nadal_games').text();
        var opponent_points = (player == 'nadal') ? $('#federer_points').text() : $('#nadal_points').text();

        // Send that to app.route('/point')
        req = $.ajax({
            url : '/point',
            type : 'POST',
            data : { player: player, player_sets: player_sets, player_games: player_games, player_points: player_points,
                     opponent: opponent, opponent_sets, opponent_games: opponent_games, opponent_points: opponent_points }
        });

        // Update each player's sets/games/points, and if there's a winner,
        // set everything to 0 for a new game and send an alert that a winner has been decided.
        // You can still have a successful challenge if you accidentally declare a winner.
        req.done(function(data) {
            // No winner yet
            if (data.winner_decided == 'no') {
                
                $('#federer_sets').text(data.federer_sets);
                $('#federer_games').text(data.federer_games);
                $('#federer_points').text(data.federer_points);
                
                $('#nadal_sets').text(data.nadal_sets);
                $('#nadal_games').text(data.nadal_games);
                $('#nadal_points').text(data.nadal_points);
            }
            // Winner has been decided
            else {
                $('#federer_sets').text('0');
                $('#federer_games').text('0');
                $('#federer_points').text('0');
                
                $('#nadal_sets').text('0');
                $('#nadal_games').text('0');
                $('#nadal_points').text('0');     
                alert(player + ' wins!');           
            }
        });
    });
});