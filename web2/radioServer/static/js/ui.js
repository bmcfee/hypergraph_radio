// CREATED:2011-09-19 09:00:10 by Brian McFee <bmcfee@cs.ucsd.edu>
// UI control code for the radio 

var volumeOn        = true;

var sliding         = false;

// Handle keyboard events
$(document).keydown(function (e) {
    if ($("#search").is(":focus")) {
        return;
    }
//     console.log(e.which);
    switch (e.which) {

        case 75:    // K        (up/prev)
        case $.ui.keyCode.LEFT:
            previousTrack();
            e.preventDefault();
            break;

        case 191:   // /
            $("#search").focus();
            e.preventDefault();
            break;
    
        case 88:    // X        (delete)
            deleteCurrentSong();
            e.preventDefault();
            break;

        case 74:    // J        (down/next)
        case $.ui.keyCode.RIGHT:
            nextTrack();
            e.preventDefault();
            break;

        case $.ui.keyCode.DOWN:
            break;
        case $.ui.keyCode.UP:
            break;

        case 65:    // A        (append)
            expandPlaylist();
            e.preventDefault();
            break;

        case 73:    // I        (insert)
            insertSong();
            e.preventDefault();
            break;

        case 77:    // M        (mute)
            toggleVolume($("#volume"));
            break;

        case 82:    // R        (replace)
            replaceCurrentSong();
            break;

        case $.ui.keyCode.SPACE:
            playPauseMusic();
            e.preventDefault();
            break
    }
});

function toggleVolume(buttonNode) {

    volumeOn ^= 1;

    buttonNode
        .button("option", "icons", { primary: volumeOn ? "ui-icon-volume-on" : "ui-icon-volume-off" });

    setMute(volumeOn);
}

// Initialize control widgets and start the player
$(function() {
    $( "#trackprogress" )
        .slider({   slide:      seekTrack, 
                    animate:    false, 
                    disabled:   true, 
                    range:      "min", 
                    start:      function() { sliding = true; },
                    stop:       function() { sliding = false;},
        });

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
                    url:        "/search",
                    dataType:   "json",
                    data:       { q: request.term },
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


function notify(message) {
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
