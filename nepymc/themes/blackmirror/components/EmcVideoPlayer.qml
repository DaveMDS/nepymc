import QtQuick
import QtQuick.Controls
import QtMultimedia


Item {
    id: root
    objectName: "EmcVideoPlayer"

    /* TODO THEME API */
    property alias source: emcVideo.source
    property alias position: emcVideo.position  // readonly
    property alias duration: emcVideo.duration  // readonly
    property alias volume: emcVideo.audioOutput.volume // log adjusted, 0.0-1.0
    property alias muted: emcVideo.audioOutput.muted  // bool r/w

    property alias audioTracks: emcVideo.audioTracks
    property alias audioTrack: emcVideo.activeAudioTrack
    property alias videoTracks: emcVideo.videoTracks
    property alias videoTrack: emcVideo.activeVideoTrack
    property alias subtitleTracks: emcVideo.subtitleTracks
    property alias subtitleTrack: emcVideo.activeSubtitleTrack

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
        // TODO milliseconds?
        // TODO just use the position prop ?
        emcVideo.position = position
    }

    MediaPlayer {
        id: emcVideo
        audioOutput: AudioOutput {}
        videoOutput: emcVideoOutput
    }

    VideoOutput {
        id: emcVideoOutput
        anchors.fill: parent
    }

}

