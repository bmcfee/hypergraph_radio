var radioListener = {};
var player = null;
var paused = true;

var trackDuration = 0;
var songQueue = [];

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
        player.rdio_previous();
    }
}

function nextTrack() {
    if (player != null) {
        playFromQueue();
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
    // Add to the queue?
    loadSongs();
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
    $("#album-art").html("<img id='album-art-img' src='" + playingTrack.icon + "'/>");
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
//     console.log('Position: ' + position);
//     minutes = Math.round(position / 60);
//     seconds = (Math.round(position) % 60).toString();
//     if (seconds.length < 2) {
//         seconds = '0' + seconds;
//     }

    $("#trackprogress").slider({value: position * 100 / trackDuration});
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

function loadSong(song_id) {

    $.getJSON('/queue/', {query: song_id}, function(data) {
        songQueue = data;
        playFromQueue();
    });

}

function loadSongs() {

    $.getJSON('/playlist/', {}, function(data) {

        for (i = 0; i < data.length; i++) {
         songQueue.push(data[i]);
        }
        playFromQueue();
    });
}

function playFromQueue() {
    if (songQueue.length < 1) {
        return;
    }

    $("#trackprogress").slider("option", "disabled", false);
    song = songQueue.shift();
    player.rdio_play(song);
}

function initRdioPlayer() {
    var url = '/rdio/';
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
