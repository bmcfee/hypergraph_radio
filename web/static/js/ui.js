// CREATED:2011-09-19 09:00:10 by Brian McFee <bmcfee@cs.ucsd.edu>
// UI control code for the radio 

// Handle keyboard events
$(document).keydown(function (e) {


    switch (e.which) {

        case $.ui.keyCode.LEFT:
            previousTrack();
            e.preventDefault();
            break;

        case $.ui.keyCode.DOWN:
            break;

        case $.ui.keyCode.RIGHT:
            nextTrack();
            e.preventDefault();
            break;

        case $.ui.keyCode.UP:
            break;

        case $.ui.keyCode.SPACE:
            if (! $("#search").is(":focus")) {
                playPauseMusic();
                e.preventDefault();
            }
            break
    }
});

// Initialize control widgets and start the player
$(function() {
    $( "#trackprogress" ).slider({slide: seekTrack, animate: true, disabled: true, range: "min", step: 1});

    $( "#previous" )
        .button({ text: false, icons: { primary: "ui-icon-seek-start" } })
        .click(previousTrack);

    $( "#playpause" )
        .button({ text: false, icons: { primary: "ui-icon-play" } })
        .click(playPauseMusic);

    $( "#next" )
        .button({ text: false, icons: { primary: "ui-icon-seek-end" } })
        .click(nextTrack);

    $( "#clear" )
        .button({ text: false, icons: { primary: "ui-icon-trash"}, disabled: true })
        .click(clearSongQueue);

    $( "#search" )
        .autocomplete({
            source: function( request, response ) {
                $.ajax({
                    url:        "/search/",
                    dataType:   "json",
                    data:       { query: request.term },
                    success:    response 
                });
            },
            minLength: 2,       // don't search if the length is less than 2 characters
            select: function( event, ui ) {
                if (ui.item) {
                    loadSong(ui.item.song_id);
                    $("#search").blur();
                }
                console.log( ui.item ?
                    "Selected: [" + ui.item.song_id + "] " + ui.item.artist + ' - ' + ui.item.title:
                    "Nothing selected, input was " + this.value );
                }
        })
        .data( "autocomplete" )._renderItem = function( ul, item ) {
            return $( "<li></li>" )
                    .data( "item.autocomplete", item )
                    .append( "<a><b>" + item.artist + "</b><br>" + item.title + "</a>" )
                    .appendTo( ul );
        };


    initRdioPlayer();
});
