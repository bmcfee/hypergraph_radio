// CREATED:2011-09-19 09:00:10 by Brian McFee <bmcfee@cs.ucsd.edu>
// UI control code for the radio 

var infiniteRadio   = true;
var volumeOn        = true;

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

        case 77:
            toggleVolume($("#volume"));
            break;

        case $.ui.keyCode.SPACE:
            if (! $("#search").is(":focus")) {
                playPauseMusic();
                e.preventDefault();
            }
            break
    }
});

function toggleRadio(buttonNode) {

    infiniteRadio ^= 1;

    console.log("Infinite radio is now: " + infiniteRadio);
    buttonNode
//         .button("option", "icons", { primary: infiniteRadio ? "ui-icon-signal-diag" : "ui-icon-link" })
        .button("option", "label", "Radio " + (infiniteRadio ? "ON" : "OFF"));

    if (infiniteRadio && $("li.playing").length > 0 && $("li.playing").next().length == 0) {
        // radio mode was enabled while we were on the last song.  add a track.
        expandPlaylist();
    }

}

function toggleVolume(buttonNode) {

    volumeOn ^= 1;

    buttonNode
        .button("option", "icons", { primary: volumeOn ? "ui-icon-volume-on" : "ui-icon-volume-off" });

    setMute(volumeOn);
}

// Initialize control widgets and start the player
$(function() {
    $( "#trackprogress" ).slider({slide: seekTrack, animate: true, disabled: true, range: "min", step: 1});

    $( "#previous" )
        .button({ text: false, icons: { primary: "ui-icon-seek-start" }, disabled: true })
        .click(previousTrack);

    $( "#playpause" )
        .button({ text: false, icons: { primary: "ui-icon-play" }, disabled: true })
        .click(playPauseMusic);

    $( "#next" )
        .button({ text: false, icons: { primary: "ui-icon-seek-end" }, disabled: true })
        .click(nextTrack);

    $( "#clear" )
        .button({ text: false, icons: { primary: "ui-icon-trash"}, disabled: true })
        .click(clearSongQueue);

    $( "#volume" )
        .button({ text: false, icons: { primary: "ui-icon-volume-on"}, disabled: true })
        .click(function() {toggleVolume($(this));});

    $( "#toolbar" )
        .buttonset();

    $( "#infinite" )
        .button({ label: "Radio " + (infiniteRadio ? "ON" : "OFF"), icons: { primary: "ui-icon-signal-diag"}, disabled: false})
        .click(function() {toggleRadio($(this));});

    $( "#expand" )
        .button({ text: false, icons: { primary: "ui-icon-triangle-1-s"}, disabled: true })
        .click(expandPlaylist);

    $( "#playlist" )
        .sortable({
                update: function(e, ui) { 
                            updatePlayerFromList(false); 
                        },
                scroll: true,
                revert: 'invalid'
        })
        .disableSelection();

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
