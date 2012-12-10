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
        $('li.playing > img').removeClass('hidden');
        player.rdio_play();
    } else {
        paused = true;
        $('li.playing > img').addClass('hidden');
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

    $("#previous")
        .addClass('disabled');
    $("#playpause")
        .addClass('disabled');
    $("#next")
        .addClass('disabled');
//     $("#trackprogress")
//         .slider("option", "disabled", true)
//         .slider("option", "value", 0);

}

function resetPlayerDisplay() {
    $("#song-title")    .text('');
    $("#artist-name")   .text('');
    $("#album-title")   .text('');
    $("#album-art-img") .attr('src', '/static/i/logo.png');
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
        .removeClass('disabled');

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
        $("#playpause > i")
            .removeClass('icon-play')
            .addClass('icon-pause');
    } else {
        $("#playpause > i")
            .removeClass('icon-pause')
            .addClass('icon-play');
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
    } else if ( $("li.playing").next().length == 0 ) {
        // we're on the last track, but in radio mode.. add another
        expandPlaylist();
    }
    console.log('Playing: ' + playingTrack.artist + ' - ' + playingTrack.name );

    trackDuration = playingTrack.duration;


    $("#artist-name")
        .text(playingTrack.artist);

    $("#song-title")
        .text(playingTrack.name);

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
}

function enablePlaylistWidgets() {
    $("#playpause").removeClass('disabled');
}

function addToPlaylist(song_id) {
    $.getJSON(
        '/song', 
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
            $("#playlist-header")
                .removeClass('hidden');
        });
}

function killSongNode(node) {
    node.remove();
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


function getCurrentSongIDs() {
    var current_ids     = [];

    $('.song_id').each(function() { current_ids.push($(this).val()); });

    return current_ids;
}

function askForSongs(node, replace) {

    var before_id   = null;
    var after_id    = null;
    
    if (node != null) {
        before_id   = node.find('.song_id').val();
        after_id    = node.next().find('.song_id').val();
    }

    $.post(  '/playlist', 
                {
                    seeds:      JSON.stringify([before_id]), 
                    not_list:   JSON.stringify(getCurrentSongIDs()),
                }, 
                function(data, textStatus, jqXHR) { 
                    if (data.length == 0) {
                        // no songs!
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
    if ($("#playlist > li").length > 0) {
        console.log('Trying to expand existing playlist');
        askForSongs($("#playlist >  li:last"));
    } else {
        console.log('Trying to expand from nothing?');
    }
}

function replaceCurrentSong() {

    var currentSong = $("li.playing");

    if (currentSong.length > 0) {
        askForSongs(currentSong, true);
    }
}

function createSongNode(song) {

    var delButton = $('<a class="btn ajax"></a>');
    delButton
        .append('<i class="media-object icon-remove icon-white" alt="remove this song"></i>');
    delButton
        .bind('click', function() { deleteSong($(this).parents('li')); });

    var replaceButton = $('<a class="btn ajax"></a>');
    replaceButton
        .append('<i class="media-object icon-refresh icon-white" alt="replace this song"></i>');
    replaceButton
        .bind('click', function() { askForSongs($(this).parents('li'), true); });

    var addButton = $('<a class="btn ajax"></a>');
    addButton
        .append('<i class="media-object icon-resize-full icon-white" alt="more like this"></i>');
    addButton
        .bind('click', function() { askForSongs($(this).parents('li'), false); });

    var controlGroup = $('<div></div>');
    controlGroup.addClass('btn-group');
    controlGroup.append(addButton);
    controlGroup.append(replaceButton);
    controlGroup.append(delButton);

    var controlBar = $('<div></div>');
    controlBar
        .addClass('hidden')
        .addClass('btn-toolbar')
        .addClass('pull-right');
    controlBar
        .append(controlGroup);

    var isplaying = $('<img src="/static/i/nowplaying.gif" />');

    isplaying
        .addClass('now-playing')
        .addClass('hidden')
        .addClass('pull-left');

    var li = $('<li></li>')
        .addClass('media')
        .append(controlBar)
        .append(isplaying)
        .append('<h5 class="media-heading">' + song.title + '</h5>')
        .append('<h5 class="muted media-heading">' + song.artist + '</div>')
        .append('<input type="hidden" name="rdio_id" class="rdio_id" value="' + song.rdio_id + '"/>')
        .append('<input type="hidden" name="song_id" class="song_id" value="' + song.song_id + '"/>')
        .append('<input type="hidden" name="edge_name" class="edge_name" value="' + song.edge + '"/>');


    li.bind('dblclick', function() { seekTo( $(this) ); });

    li.hover(function(e) {
        $(this).find('.btn-toolbar').removeClass('hidden');
    }, function(e) {
        $(this).find('.btn-toolbar').addClass('hidden');
    });

    return li;
}


function seekTo(node) {
    $("img.now-playing")
        .addClass('hidden');
    $("li.playing")
        .removeClass('playing');

    node
        .find('img')
        .removeClass('hidden');
    node
        .addClass('playing');

    updatePlayerFromList(true);
}

function moveForward() {
    var currentlyPlaying = $("li.playing");

    if (currentlyPlaying.length > 0) {
    
        var next = currentlyPlaying.next();

        if (next.length > 0) {
            currentlyPlaying
                .find('img')
                .addClass('hidden');
            currentlyPlaying
                .removeClass('playing');

            next
                .find('img')
                .removeClass('hidden');
            next
                .addClass('playing');

            updatePlayerFromList(true);
        }
    } else {
        $("li.playlist:first")
            .find('img')
            .removeClass('hidden');
        $("li.playlist:first")
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
                .find('img')
                .addClass('hidden');
            currentlyPlaying
                .removeClass('playing');

            prev
                .find('img')
                .removeClass('hidden');
            prev
                .addClass('playing');

            updatePlayerFromList(true);
        }
    }
}

function updatePlayerFromList(changePlayer) {
    var playing_node    = $("li.playing");
    var rdio_id         = $("li.playing > input.rdio_id").val();
    var song_id         = $("li.playing > input.song_id").val();

    if (changePlayer && rdio_id != undefined) { 
        player.rdio_play(   rdio_id ); 
    }
    
    if (playing_node.prev().length == 0) { $('#previous').addClass('disabled'); } 
                                    else { $('#previous').removeClass('disabled'); }

    if (playing_node.next().length == 0) { $('#next').addClass('disabled'); } 
                                    else { $('#next').removeClass('disabled'); }
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
