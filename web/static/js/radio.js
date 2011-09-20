var radioListener = {};
var player = null;
var paused = true;

var trackDuration       = 0;

function playPauseMusic() {
    if (player == null) {
        return;
    }

    if (paused) {
        paused = false;
        player.rdio_play();
    } else {
        paused = true;
        player.rdio_pause();
    }
}

function stopMusic() {
    if (player != null) {
        player.rdio_stop();
    }
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
    if (player != null) {
        offset = Math.round($("#trackprogress").slider("option", "value") * trackDuration / 100);
        player.rdio_seek(offset);
    }
}

radioListener.ready = function() {
    radioListener.is_ready = true;

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
        return;
    }
    console.log('Playing: ' + playingTrack.artist + ' - ' + playingTrack.name );

    trackDuration = playingTrack.duration;

    $("#song-title").text(playingTrack.name);
    $("#artist-name").text(playingTrack.artist);
    $("#album-art").html("<img id='album-art-img' style='width: 200px; height: 200px;' src='" + playingTrack.icon + "'/>");
}

radioListener.playingSourceChanged = function(playingSource) {
    //  The currently playing source changed. 
    //  The source metadata, including a track listing is inside playingSource.
//     console.log('New source: ' + JSON.stringify(playingSource));
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

    $("#trackprogress").slider({value: Math.round(position * 100 / trackDuration)});
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


function resetPlayer() {
    stopMusic();

    $("#clear")
        .button("option", "disabled", true);
    $("#previous")
        .button("option", "disabled", true);
    $("#playpause")
        .button("option", "disabled", true);
    $("#next")
        .button("option", "disabled", true);
    $("#trackprogress")
        .slider("option", "disabled", true)
        .slider("option", "value", 0);

    $("#song-title")
        .text('');
    $("#artist-name")
        .text('');
    $("#album-art")
        .html("<img src='/i/big-loader.gif' alt='' style='width:32px; height:32px; padding:84px' />");

}

function clearSongQueue() {
    resetPlayer();

    $("#playlist  > li")
        .remove();
}

function importSongs(data, shouldPlay) {
    for (i = 0; i < data.length; i++) {
        appendSong(data[i]);
    }
    shouldPlay && moveForward();
}

function loadSong(song_id) {
    $.getJSON('/queue/', {query: song_id}, function(data) { 
                                                importSongs(data, $("li.playing").length == 0); 
                                                updatePlayerFromList(false);
                                            });
}

function appendSong(song) {

    var li = $('<li />').addClass('playlist')
        .append('<div class="artistName">' + song.artist + '</div>')
        .append('<div class="songTitle">' + song.title + '</div>')
        .append('<input type="hidden" name="rdio_id" class="rdio_id" value="' + song.rdio_id + '"/>')
        .append('<input type="hidden" name="song_id" class="song_id" value="' + song.song_id + '"/>');

    li.bind('dblclick', function() { seekTo(li); });

    $("#playlist")
        .append(li);

    $("#clear")
        .button("option", "disabled", false);

    $("#playpause")
        .button("option", "disabled", false);
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

function updatePlayerFromList(changePlayer) {
    var playing_node    = $("li.playing");
    var rdio_id         = $("li.playing > input.rdio_id").val();

    if (changePlayer && rdio_id != undefined) { 
        player.rdio_play( rdio_id ); 
        $("#playlistWidget").scrollTo($("li.playing"));
    }

    
    $("#previous")
        .button("option", "disabled", playing_node.prev().length == 0);
    $("#next")
        .button("option", "disabled", playing_node.next().length == 0);
    
}

function initRdioPlayer() {
    var url = '/rdio/';
    
    clearSongQueue();

    $.getJSON(url, {}, function(data) {
        if (data) {
            params = {  'playbackToken':    data.playbackToken,
                        'domain':           encodeURIComponent('localhost'),
                        'listener':         'radioListener' };

            swfobject.embedSWF(     'http://www.rdio.com/api/swf',  // embed url
                                    'player',                       // element id to replace
                                    '1', '1',                       // width and height
                                    '9.0.0',                        // flash version
                                    'swf/expressInstall.swf',       // url to express install swf
                                    params, {allowScriptAccess: "always"});

        }
    });
}
