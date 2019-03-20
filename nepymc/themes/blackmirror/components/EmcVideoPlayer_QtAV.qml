import QtQuick 2.12
import QtAV 1.6
import "../utils/"

Item {
    id: video
    objectName: "EmcVideoPlayer_QtAV"

    property alias startPosition: player.startPosition
    property alias stopPosition: player.stopPosition
    property alias videoFiltersGPU: videoOut.filters
    property alias audioFilters: player.audioFilters
    property alias videoFilters: player.videoFilters
    property alias audioBackends: player.audioBackends
    property alias supportedAudioBackends: player.supportedAudioBackends
    property alias backgroundColor: videoOut.backgroundColor
    property alias brightness: videoOut.brightness
    property alias contrast: videoOut.contrast
    property alias hue: videoOut.hue
    property alias saturation: videoOut.saturation
    property alias frameSize: videoOut.frameSize
    property alias sourceAspectRatio: videoOut.sourceAspectRatio
    property alias opengl: videoOut.opengl
    property alias fastSeek: player.fastSeek
    property alias timeout: player.timeout
    property alias abortOnTimeout: player.abortOnTimeout
    property alias subtitle: subtitle
    property alias subtitleText: text_sub // not for ass.
    property alias videoCapture: player.videoCapture
    property alias audioTrack: player.audioTrack
    property alias videoTrack: player.videoTrack
    property alias externalAudio: player.externalAudio
    property alias internalAudioTracks: player.internalAudioTracks
    property alias externalAudioTracks: player.externalAudioTracks
    property alias internalVideoTracks: player.internalVideoTracks
    property alias internalSubtitleTracks: player.internalSubtitleTracks
    property alias internalSubtitleTrack: player.internalSubtitleTrack


    property alias fillMode:            videoOut.fillMode
    property alias orientation:         videoOut.orientation
    property alias videoCodecPriority:   player.videoCodecPriority
    property alias channelLayout:        player.channelLayout
    property alias playbackState:        player.playbackState
    property alias autoLoad:        player.autoLoad
    property alias bufferProgress:  player.bufferProgress
    property alias bufferSize:  player.bufferSize
    property alias duration:        player.duration
    property alias error:           player.error
    property alias errorString:     player.errorString
    //property alias availability:    player.availability
    property alias hasAudio:        player.hasAudio
    property alias hasVideo:        player.hasVideo
    property alias metaData:        player.metaData
    property alias muted:           player.muted
    property alias playbackRate:    player.playbackRate
    property alias position:        player.position
    property alias seekable:        player.seekable
    property alias source:          player.source
    property alias status:          player.status
    property alias volume:          player.volume
    property alias autoPlay:        player.autoPlay

    signal paused
    signal stopped
    signal playing
    signal seekFinished

    //    function stepForward() {
    //        player.stepForward()
    //    }

    //    function stepBackward() {
    //        player.stepBackward()
    //    }
    function play() {
        player.play()
    }
    function pause() {
        player.pause()
    }
    function stop() {
        player.stop()
    }
    function seek(offset) {
        player.seek(offset)
    }

    MediaPlayer {
        id: player
        onPaused:  video.paused()
        onStopped: video.stopped()
        onPlaying: video.playing()
        onSeekFinished: video.seekFinished()
    }

    VideoOutput2 {
        id: videoOut
        anchors.fill: video
        source: player
    }

    SubtitleItem {
        id: ass_sub
//        rotation: -videoOut.orientation
        fillMode: videoOut.fillMode
        source: subtitle
        anchors.fill: videoOut
    }

    /*Text {
        id: text_sub
        rotation: -videoOut.orientation
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignBottom
        font {
            pointSize: 20
            bold: true
        }
        style: Text.Outline
        styleColor: "darkgray" //"blue"
        color: "white"
        anchors.fill: videoOut
        anchors.bottomMargin: 40
    }*/

    EmcTextBigger {
        id: text_sub
        style: Text.Outline
        styleColor: "black"
        anchors.fill: videoOut
        anchors.bottomMargin: 40
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignBottom
    }

    Subtitle {
        id: subtitle
        player: player
        onContentChanged: {
            if (!canRender || !ass_sub.visible)
                text_sub.text = text
        }
        onEngineChanged: { // assume a engine canRender is only used as a renderer
            ass_sub.visible = canRender
            text_sub.visible = !canRender
        }
        onEnabledChanged: {
            ass_sub.visible = enabled
            text_sub.visible = enabled
        }
    }

}

