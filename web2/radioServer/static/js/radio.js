var radioListener = {};
var player = null;
var paused = true;

var trackDuration       = 0;

function playPauseMusic() {
    if (player == null) {
        return;
    }

    startMusic();

    if (paused) {
        paused = false;
        player.rdio_play();
    } else {
        paused = true;
        player.rdio_pause();
    }
}

function startMusic() {

    if ($("li.playing").length == 0) {
        moveForward();
    }
}

function stopMusic() {
    if (player != null) {
        player.rdio_stop();
    }
    $("li.playing")
        .removeClass("playing")
        .addClass("playlist");
    resetPlayerDisplay();
}

function resetPlayer() {
    stopMusic();

    $("#clear")     .button("option", "disabled", true);
    $("#previous")  .button("option", "disabled", true);
    $("#playpause") .button("option", "disabled", true);
    $("#next")      .button("option", "disabled", true);
    $("#expand")    .button("option", "disabled", true);

    $("#trackprogress")
        .slider("option", "disabled", true)
        .slider("option", "value", 0);

}

function resetPlayerDisplay() {
    $("#song-title")    .text('');
    $("#artist-name")   .text('');
    $("#album-title")   .text('');
    $("#tags")          .text('');
    $("#album-art-img") .attr('src', '/static/i/markovoni.png');
    $("#artist-info")   .fadeOut('fast', function() {
                            $("#artist-image")  .attr('src', '');
                            $("#artist-bio")    .text('');
                        });

}

function previousTrack() {
    if (player != null) {
        moveBack();
    }
}

function nextTrack() {
    if (player != null) {
        moveForward();
    }
}

function seekTrack() {
    var progress = $("#trackprogress");
    if (player != null) {
        offset = Math.round(progress.slider("option", "value") * trackDuration / 100);
        player.rdio_seek(offset);
        progress.blur();
    }
}

function setMute(volume) {
    if (player != null) {
        player.rdio_setMute(! volume);
    }
}

radioListener.ready = function() {
    radioListener.is_ready = true;
    $("#volume")
        .button("option", "disabled", false);

    player = $("#player").get(0);
    console.log('Ready to play.');
}

radioListener.playStateChanged = function(playState) {
    //  The playback state has changed. 
    //  The state can be: 0 → paused, 1 → playing, 2 → stopped, 3 → buffering or 4 → paused.
    states = ['Paused', 'Playing', 'Stopped', 'Buffering', 'Paused']
    console.log('play state: ' + states[playState]);
    if (playState == 0 || playState == 4) {
        paused = true;
    } else {
        paused = false;
    }
    if (playState == 1) {
        $( "#playpause" ).button("option", "icons", {primary: 'ui-icon-pause'});
    } else {
        $( "#playpause" ).button("option", "icons", {primary: 'ui-icon-play'});
    }

    if (playState != 2) {
        $("#trackprogress").slider("option", "disabled", false);
    }

}


radioListener.playingTrackChanged = function(playingTrack, sourcePosition) {
    //  The currently playing track has changed. 
    //  Track metadata is provided as playingTrack and the position within the playing source as sourcePosition.

    if (playingTrack == null) {
        // we're all out of tracks
        resetPlayerDisplay();
        
        return;
    } else if ( infiniteRadio && $("li.playing").next().length == 0 ) {
        // we're on the last track, but in radio mode.. add another
        expandPlaylist();
    }
    console.log('Playing: ' + playingTrack.artist + ' - ' + playingTrack.name );

    trackDuration = playingTrack.duration;

    $("#song-title")
        .text(playingTrack.name);

    $("#artist-name")
        .text(playingTrack.artist);

    $("#album-title")
        .text(playingTrack.album);

    $("#album-art-img")
        .attr('src', playingTrack.icon);
}

radioListener.playingSourceChanged = function(playingSource) {
    //  The currently playing source changed. 
    //  The source metadata, including a track listing is inside playingSource.
    if (playingSource == null) {
        if ($("li.playing").next().length > 0) {
            moveForward();
        } else {
            stopMusic();
        }
    }
}

radioListener.volumeChanged = function(volume) {
    //  The volume changed to volume, a number between 0 and 1.
    console.log('Volume: ' + volume);
}

radioListener.muteChanged = function(mute) {
    //  Mute was changed. 
    //  mute will either be true (for muting enabled) or false (for muting disabled).
    console.log('Mute: ' + mute);
}

radioListener.positionChanged = function(position) {
    //  The position within the track changed to position seconds. 
    //  This happens both in response to a seek and during playback.

    if (! sliding) {
        $("#trackprogress").slider({value: Math.round(position * 100 / trackDuration)});
    }
}

radioListener.queueChanged = function(newQueue) {
    //  The queue has changed to newQueue.
    console.log('Queue: ' + JSON.stringify(newQueue));
}

radioListener.shuffleChanged = function(shuffle) {
    //  The shuffle mode has changed. 
    //  shuffle is a boolean, true for shuffle, false for normal playback order.
}

radioListener.repeatChanged = function(repeatMode) {
    //  The repeat mode change. 
    //  repeatMode will be one of: 0 → no-repeat, 1 → track-repeat or 2 → whole-source-repeat.
}

radioListener.updateFrequencyData = function(arrayAsString) {
    //  Receive a frequency update. 
    //  The data comes as a string that is a comma separated array of floats in the range 0-1.
}

radioListener.playingSomewhereElse = function() {
    //  An Rdio user can only play from one location at a time. 
    //  If playback begins somewhere else then playback will stop and radioListener callback will be called.
    console.log("CAN'T PLAY HERE");
}


function clearSongQueue() {
    resetPlayer();

    $("#playlist  > li")
        .remove();

    $("#howto")
        .removeClass("hidden");
}

function enablePlaylistWidgets() {
    $("#clear")
        .button("option", "disabled", false);

    $("#expand")
        .button("option", "disabled", false);

    $("#playpause")
        .button("option", "disabled", false);

    $("#howto")
        .addClass("hidden");
}

function loadSong(song_id) {
    $.getJSON(
        '/song/', 
        {query: song_id}, 
        function(data) { 
            var startPlaying    = ($("li.playing").length == 0);
            var playlist        = $("#playlist");
            for (var i = 0; i < data.length; i++) {
                playlist.append(createSongNode(data[i]));
            }
            
            if (startPlaying) {
                moveForward();
            }
            
            enablePlaylistWidgets();
            updatePlayerFromList(false);
        });
}

function killSongNode(node) {
    node.hide('blind', 'fast', function() { node.remove(); });
}

function deleteSong(node) {
    console.log('Deleting song: ' + node.find('input.song_id').val());

    if (node.hasClass('playing')) {
        if (node.next().length > 0) {
            moveForward();
            killSongNode(node);
        } else if (node.prev().length > 0) {
            moveBack();
            killSongNode(node);
        } else {
            clearSongQueue();
        }
    } else {
        killSongNode(node);
        updatePlayerFromList(false);
    }
}
function deleteCurrentSong() {
    var currentSong = $("li.playing");
    deleteSong(currentSong);
}

function getActiveTags() {
    var taglist = [];

    $(".tag-item-name").each(function() {
        taglist.push($(this).val());
    });

    return taglist;
}

function getCurrentSongIDs() {
    var bad_ids     = [];

    $('.song_id').each(function() { bad_ids.push($(this).val()); });

    return bad_ids;
}

function askForSongs(node, replace) {

    var before_id   = null;
    var after_id    = null;
    
    if (node != null) {
        before_id   = node.find('.song_id').val();
        after_id    = node.next().find('.song_id').val();
    }

    $.post(  '/playlist/', 
                {
                    before:     before_id, 
                    after:      after_id,
                    not_list:   JSON.stringify(getCurrentSongIDs()),
                    tag_filter: JSON.stringify(getActiveTags())
                }, 
                function(data, textStatus, jqXHR) { 
                    if (data.length == 0) {
                        // no songs!
                        showTagDialog();
                        $("#no-songs-message")
                            .removeClass("hidden");
                        return;
                    }
                    if (node != null) {
                        for (var i = data.length - 1; i >= 0; i--) {
                            node.after(createSongNode(data[i]));
                        }
                        if (replace) {
                            deleteSong(node);
                        }
                    } else {
                        var playlist = $("#playlist");
                        for (var i = 0; i < data.length; i++) {
                            playlist.append(createSongNode(data[i]));
                        }
                    }
                    enablePlaylistWidgets();
                    updatePlayerFromList(false);
                }, 'json');
}

function insertSong() {
    var currentSong = $("li.playing");

    if (currentSong) {
        askForSongs(currentSong, false);
    }
}

function expandPlaylist() {
    if ($("#playlistWidget li").length > 0) {
        askForSongs($("#playlistWidget li:last"));
    } else {
        askForSongs(null);
    }
}

function replaceCurrentSong() {

    var currentSong = $("li.playing");

    if (currentSong.length > 0) {
        askForSongs(currentSong, true);
    }
}

function createSongNode(song) {

    var delButton = $('<button style="float: right;"/>')
        .text('Delete this song')
        .button({text: false, icons: {primary: 'ui-icon-close'}})
        .click(function() { deleteSong( $(this).parents('li') ); });

    var addButton = $('<button style="float: right;"/>')
        .text('Add a song')
        .button({text: false, icons: {primary: 'ui-icon-plusthick'}})
        .click(function() { askForSongs( $(this).parents('li'), false ); });

    var replaceButton = $('<button style="float: right;"/>')
        .text('Replace this song')
        .button({text: false, icons: {primary: 'ui-icon-arrowreturnthick-1-w'}})
        .click(function() { askForSongs( $(this).parents('li'), true ); });

    var bs = $('<div style="float: right; font-size: 8pt;"></div>')
                    .append(delButton)
                    .append(replaceButton)
                    .append(addButton)
                    .buttonset();

    var li = $('<li />')
        .addClass('playlist')
        .append(bs)
        .append('<div class="artistName">' + song.artist + '</div>')
        .append('<div class="songTitle">' + song.title + '</div>')
        .append('<input type="hidden" name="rdio_id" class="rdio_id" value="' + song.rdio_id + '"/>')
        .append('<input type="hidden" name="song_id" class="song_id" value="' + song.song_id + '"/>');

    li.find('button')
        .addClass('hidden');

    li.bind('dblclick', function() { seekTo( $(this) ); });

    li.hover(function(e) {
        $(this).find('button').removeClass('hidden');
    }, function(e) {
        $(this).find('button').addClass('hidden');
    });

    return li;
}


function seekTo(node) {
    $("li.playing")
        .removeClass('playing')
        .addClass('playlist');

    node
        .removeClass('playlist')
        .addClass('playing');

    updatePlayerFromList(true);
}

function moveForward() {
    var currentlyPlaying = $("li.playing");

    if (currentlyPlaying.length > 0) {
    
        var next = currentlyPlaying.next();

        if (next.length > 0) {
            currentlyPlaying
                .removeClass('playing')
                .addClass('playlist');

            next
                .removeClass('playlist')
                .addClass('playing');

            updatePlayerFromList(true);
        }
    } else {
        $("li.playlist:first")
            .removeClass('playlist')
            .addClass('playing');
        updatePlayerFromList(true);
    }
}

function moveBack() {
    var currentlyPlaying = $("li.playing");

    if (currentlyPlaying.length > 0) {
        
        var prev = currentlyPlaying.prev();

        if (prev.length > 0) {
            currentlyPlaying
                .removeClass('playing')
                .addClass('playlist');
            prev
                .removeClass('playlist')
                .addClass('playing');

            updatePlayerFromList(true);
        }
    }
}

function getArtistInfo(song_id) {

    $.getJSON('/artist/', {query: song_id}, function(data) {

        var current_song_id = $("li.playing > input.song_id").val();
        if (data['song_id'] != current_song_id) {
            return;
        }

        $("#artist-info").fadeOut('fast', function() {
            $("#artist-image")
                .attr("src", data['image']);
    
            $("#artist-bio")
                .text(data['bio']);

            $("#artist-info-artist_id")
                .attr('value', data['artist_id']);
            $("#artist-info-song_id")
                .attr('value', data['song_id']);

            $("#artist-info").fadeIn('fast');

        });
    });
}

function getTags(song_id) {
    $.getJSON('/tags/', {query: song_id}, function(data) { 
        var tagbox  = $("#tags");
        var std     = $("#showtagdialog");

        $("#tags > a").remove();

        $.each(data, function(i, v) {
            var link = $("<a class='artist-tag'></a>")
                            .text(v)
                            .click(function() {
                                if (addTerm(v)) {
                                    // create a popup
                                    
                                    notify("Added <span style='font-weight: bold; color: #4488cc;'>" + v + "</span> to tag filter");
                                    std.addClass("update");
                                } else {
                                    removeTerm(v);
                                    notify("Removed <span style='font-weight: bold; color: red;'>" + v + "</span> from tag filter");
                                    std.addClass("update");

                                }
                            });
            tagbox.append(link);
            tagbox.append(' ');
        });
    });
}

function updatePlayerFromList(changePlayer) {
    var playing_node    = $("li.playing");
    var rdio_id         = $("li.playing > input.rdio_id").val();
    var song_id         = $("li.playing > input.song_id").val();

    if (changePlayer && rdio_id != undefined) { 
        player.rdio_play(   rdio_id ); 
        
        getTags(            song_id );
        getArtistInfo(      song_id );

        $("#playlistWidget").scrollTo($("li.playing"));
    }
    
    $("#previous")  .button("option", "disabled", playing_node.prev().length == 0);
    $("#next")      .button("option", "disabled", playing_node.next().length == 0);
}

function initRdioPlayer() {
    
    resetPlayer();

    $.getJSON(
        '/rdio', 
        {}, 
        function(data) {
            if (data) {
                params = {  'playbackToken':    data.playbackToken,
                            'domain':           encodeURIComponent(data.domain),
                            'listener':         'radioListener' };

                swfobject.embedSWF(     'http://www.rdio.com/api/swf',  // embed url
                                        'player',                       // element id to replace
                                        '1', '1',                       // width and height
                                        '9.0.0',                        // flash version
                                        'swf/expressInstall.swf',       // url to express install swf
                                        params, 
                                        {allowScriptAccess: "always"});

            }
        });
}
