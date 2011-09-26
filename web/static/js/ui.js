// CREATED:2011-09-19 09:00:10 by Brian McFee <bmcfee@cs.ucsd.edu>
// UI control code for the radio 

var infiniteRadio   = true;
var volumeOn        = true;
var tagDialogOn     = false;

// Handle keyboard events
$(document).keydown(function (e) {
    if ($("#search").is(":focus") || tagDialogOn) {
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

function toggleRadio(buttonNode) {

    infiniteRadio ^= 1;

    console.log("Infinite radio is now: " + infiniteRadio);
    buttonNode
        .button("option", "label", "Radio " + (infiniteRadio ? "ON" : "OFF"));

    if (infiniteRadio && $("li.playing").length > 0 && $("li.playing").next().length == 0) {
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

    $( "#autopilot" )
        .button({ label: "Auto-pilot " + (infiniteRadio ? "ON" : "OFF"), icons: { primary: "ui-icon-signal-diag"}, disabled: false})
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


    $( "#tag-dialog" )
        .dialog({   autoOpen:   false, 
                    modal:      true,
                    title:      'Modify your playlist tag filter',
                    buttons:    {
                        "Clear tags": function() {
                            $("#activetags > div.tag-item").remove();
                        },
                        Done: function() {
                            $( this ).dialog( "close" );
                        }
                    },
                    close: function(e, ui) {
                        tagDialogOn = false;
                    }
                });
    $( "#showtagdialog" )
        .button({ label: 'Tag filter', icons: {primary: 'ui-icon-plus'}, disabled: false})
        .click(function() {
            tagDialogOn = true;
            $("#tag-dialog").dialog("open");
            $(this).removeClass("update");
            return false;
        });

    initTagSearch();
    initRdioPlayer();
});

function tagExists(term) {

    var match = false;

    /* check for existing tag */
    $("input.tag-item-name").each( function(i, E) {
        if (term == E.value) {
            match = true;
            return false;
        }
    });

    return match;
}

function addTerm(term) {
    if (tagExists(term)) {
        return false;
    }

    console.log('Adding term: ' + term);

    var tagNode = $("<div class='tag-item'></div>");

    tagNode.text(term);
    var killButton = $("<button style='font-size: 5pt; float:right; margin-left: 4pt;'>Delete tag</button>");
    killButton.button({text: false, icons: { primary: "ui-icon-close"}})
        .click(function() {$(this).parent().remove();});
    tagNode.append(killButton);

    tagNode.append($('<input type="hidden" class="tag-item-name" />')
                        .attr('value', term));
    $("#activetags")
        .append(tagNode);
    return true;
}

function removeTerm(term) {
    $("input.tag-item-name").each(function(i,E) {
        if (term == E.value) {
            $(E).parent().remove();
            return false;
        }
    });
}

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

function initTagSearch() {
    var terms;

    $.getJSON('/terms/', {}, function(data) {
        $("#tagsearch")
            .autocomplete({ 
                source:     data, 
                minLength:  2, 
                closeOnEscape: false,
                select:     function(e, ui) {
                    if (ui.item) {
                        addTerm(ui.item.value);
                    }
                    $(this).val('');
                    return false;
                },
            });
    });
}
