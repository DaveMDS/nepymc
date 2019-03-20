import QtQuick 2.12
import QtQuick.Controls 2.12
import QtMultimedia 5.12


Item {
    id: root
    objectName: "EmcVideoPlayer_QtMultimedia"

    /* TODO THEME API */
    property alias source: emcVideo.source
    property alias position: emcVideo.position  // readonly
    property alias duration: emcVideo.duration  // readonly
    property alias volume: emcVideo.volume // log adjusted, 0.0-1.0
    property alias muted: emcVideo.muted  // bool r/w

    // QtAV specific (not supported by QtMultimedia)
    property var internalAudioTracks: []
    property int audioTrack: 0
    property var internalVideoTracks: []
    property int videoTrack: 0
    property var internalSubtitleTracks: []
    property int internalSubtitleTrack: -1


    function play() {
        emcVideo.play()
    }
    function pause() {
        emcVideo.pause()
    }
    function stop() {
        emcVideo.stop()
    }
    function seek(position) {
        emcVideo.seek(position)
    }


    Video {  // the actual video object
        id: emcVideo

        anchors.fill: parent
    }

}

