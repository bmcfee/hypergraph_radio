// CREATED:2011-09-19 09:00:10 by Brian McFee <bmcfee@cs.ucsd.edu>
// UI control code for the radio 

var volumeOn        = true;

var sliding         = false;

function toggleVolume() {

    volumeOn ^= 1;

    if (volumeOn) {
        $("#volume > i")
            .removeClass('icon-volume-off')
            .addClass('icon-volume-up');
    } else {
        $("#volume > i")
            .removeClass('icon-volume-up')
            .addClass('icon-volume-off');
    }
    setMute(volumeOn);
}

// Initialize control widgets and start the player
$(function() {

    $("#previous")
        .bind('click', previousTrack);
    $("#playpause")
        .bind('click', playPauseMusic);
    $("#volume")
        .bind('click', toggleVolume);
    $("#next")
        .bind('click', nextTrack);

    $("#hide-results")
        .bind('click', function() {
            $("#search-results > li").remove()
            $("#search-box").addClass('hidden');
        });
    $(".form-search").bind('submit', function() {
        var query = $(".search-query").val();

        //  clear the old search results, show a thinker
        $("#search-results > li").remove();
        $("#search-box").addClass('hidden');

        $.getJSON(  
            '/search',
            { q: query },
            function(data) {
                var ul = $("#search-results");

                $.each(data, function(i, item) {
                    console.log(JSON.stringify(item));
                    /* Construct a new media item */
                    var li = $('<li></li>');

                    li.addClass('media');

                    /* Construct a media object */

                    var addme = $('<a class="pull-right btn ajax"></a>');

                    addme
                        .append('<i class="media-object icon-plus icon-white"></i>');

                    addme.bind('click', function() {
                        addToPlaylist(item.song_id);
                        $(this).parent().remove();
                        
                        if (ul.children().length == 0) {
                            $("#search-box")
                                .addClass('hidden');
                        }
                    });

                    // TODO:   2012-12-09 14:38:33 by Brian McFee <brm2132@columbia.edu>
                    // check to see if the current song is already in the playlist 
                    // set the icon accordingly

                    li
                        .append(addme)
                        .append('<h5 class="media-heading">' + item.title + '</h5>')
                        .append('<div class="media-heading muted">' + item.artist + '</div>');

                    /* add it to the search results */
                    li.appendTo(ul);
                });
                $("#search-box").removeClass('hidden');
            }
        );
    });

    initRdioPlayer();
});


function notify(message) {
//TODO:   2012-12-10 08:40:54 by Brian McFee <brm2132@columbia.edu>
// redo this in bootstrap 

    var D = $('<div style="text-align: center;"></div>');
        
    D.append(message);
    D.dialog({  autoOpen:       true, 
                dialogClass:    'alert', 
                hide:           'fade',
                resizable:      false });
    D.delay(1000).queue(function() {
        D.dialog("close");
    });
}
