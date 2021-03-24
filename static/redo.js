$(document).ready(function() {

    $('.redoButton').on('click', function() {

        // Send a request to app.route('/redo') with the score before the point was improperly rewarded
        req = $.ajax({
            url : '/redo',
            type : 'POST',
        });

        // Update the scores to the old ones
        req.done(function(data) {
            $('#federer_sets').text(data.federer_sets);
            $('#federer_games').text(data.federer_games);
            $('#federer_points').text(data.federer_points);
            
            $('#nadal_sets').text(data.nadal_sets);
            $('#nadal_games').text(data.nadal_games);
            $('#nadal_points').text(data.nadal_points);
        });
    });
});