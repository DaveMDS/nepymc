import QtQuick 2.12
import QtQuick.Controls 2.12
import QtMultimedia 5.12
import "../utils/"
import "../utils/utils.js" as Utils

EmcFocusManager {
    id: root
    objectName: "EmcVideoPlayer"

    /* TODO THEME API */
    property string url
    property string title
    property string poster

    function emcDestroy() {  /* TODO THEME API */
        root.opacity = 0.0  // fade out
        root.focusAllow = false
        root.focus = false
        root.destroy(500)  // destroy after the fadeout
    }

    anchors.fill: parent
    opacity: 0.0

    Behavior on opacity { NumberAnimation { duration: 350 } }
    Component.onCompleted: opacity = 1.0

    Keys.onSelectPressed: {  // show controls
        emcControls.emcVisible = true
        emcBtnPlay.forceActiveFocus()
    }
    Keys.onBackPressed: {
        if (emcControls.emcVisible) {  // hide controls if visible...
            emcControls.emcVisible = false
            emcVideo.forceActiveFocus()
        } else {  // ... or quit videoplayer
            emcVideo.pause()
            root.emcDestroy()
        }
    }

    Rectangle {  // big black background rect
        anchors.fill: parent
        color: "black"
    }

    Video {  // the actual video object
        id: emcVideo

        source: url
        autoPlay: true
        volume: emcVolume.emcVolumeValue

        anchors.fill: parent

        MouseArea {
            anchors.fill: parent
            onClicked: emcControls.emcVisible = !emcControls.emcVisible
        }
    }

    Item {
        id: emcControls

        property bool emcVisible: false

        anchors.fill: parent

        BorderImage {  // controls background
            id: emcControlsBG

            source: "../pics/mp_controls_bg.png"
            width: parent.width
            height: 94
            border.bottom: 15
        }

        EmcImage {  // poster image
            id: emcControlsCover

            emcUrl: root.poster

            x: 6
            width: root.poster ? parent.width / 4 : 0
            height: width * 1.1
        }

        EmcTextTopbar {  // clock
            id: emcControlsClock

            text: EmcGlobals.time_short  // auto-updating property binding
            anchors.right: parent.right
            anchors.rightMargin: 9
            y: 4
        }

        Row {  // row of buttons on the left (media controls)
            id: emcControlsButtonRow
            padding: 1

            anchors.left: emcControlsCover.right
            anchors.leftMargin: 6
            anchors.top: parent.top
            anchors.topMargin: 7

            EmcButton {  // button: Fast Backward
                id: emcBtnFBwd
                icon: "icon/fbwd"
                onEmcButtonClicked: {
                    emcVideo.seek(emcVideo.position - 60 * 1000)
                }
                KeyNavigation.right: emcBtnBwd
            }
            EmcButton {  // button: Backward
                id: emcBtnBwd
                icon: "icon/bwd"
                onEmcButtonClicked: {
                    emcVideo.seek(emcVideo.position - 10 * 1000)
                }
                KeyNavigation.right: emcBtnStop
            }
            EmcButton {  // button: Stop
                id: emcBtnStop
                icon: "icon/stop"
                onEmcButtonClicked: {
                    emcVideo.pause()
                    root.emcDestroy()
                }
                KeyNavigation.right: emcBtnPlay
            }
            EmcButton {  // button: Play / Pause
                id: emcBtnPlay
                icon: emcVideo.playbackState == MediaPlayer.PlayingState ? "icon/pause" : "icon/play"
                onEmcButtonClicked: {
                    if (emcVideo.playbackState == MediaPlayer.PlayingState) {
                        emcVideo.pause()
                    } else {
                        emcVideo.play()
                    }
                }
                KeyNavigation.right: emcBtnFwd
            }
            EmcButton {  // button: Forward
                id: emcBtnFwd
                icon: "icon/fwd"
                onEmcButtonClicked: {
                    emcVideo.seek(emcVideo.position + 10 * 1000)
                }
                KeyNavigation.right: emcBtnFFwd
            }
            EmcButton {  // button: Fast Forward
                id: emcBtnFFwd
                icon: "icon/ffwd"
                onEmcButtonClicked: {
                    emcVideo.seek(emcVideo.position + 60 * 1000)
                }
            }
        }

        Row {  // row of buttons on the right (actions)
            id: emcControlsActionRow
            padding: 1

            anchors.right: emcControlsClock.left
            anchors.top: parent.top
            anchors.topMargin: 7

            EmcButton {  // action: Audio
                label: "Audio"
            }
            EmcButton {  // action: Video
                label: "Video"
            }
            EmcButton {  // action: Subtitles
                label: "Subtitles"
            }
        }
//        DebugRect{anchors.fill: emcControlsButtonRow}
//        DebugRect{anchors.fill: emcControlsActionRow; color: "green"}

        EmcText {  // video position label
            id: emcControlsPosition

            text: Utils.ms_to_duration(emcVideo.position, true)  // "0:00:00"
            font.family: EmcGlobals.font2.name
            color: EmcGlobals.fontColorInverse
            anchors.left:emcControlsButtonRow.left
            y: 46
        }

        EmcSlider {  // video position slider
            id: emcControlsSlider

            from: 0.0
            to: emcVideo.duration
            value: emcVideo.position

            anchors.left: emcControlsPosition.right
            anchors.right: emcControlsLength.left
            anchors.top: emcControlsPosition.top
            anchors.bottom: emcControlsPosition.bottom

            onMoved: emcVideo.seek(value)
        }

        EmcText {  // video length label
            id: emcControlsLength

            text: Utils.ms_to_duration(emcVideo.duration, true)  // "0:00:00"
            font.family: EmcGlobals.font2.name
            color: EmcGlobals.fontColorInverse
            anchors.right: emcControlsClock.right
            y: 46
        }

        EmcTextBigger {  // video title
            id: emcControlsTitle

            anchors.top: emcControlsBG.bottom
            anchors.topMargin: -18
            anchors.left:emcControlsButtonRow.left
            text: root.title
            font.family: EmcGlobals.font2.name
            style: Text.Raised

        }

        states: [
            State {
                name: "visible"
                when: emcControls.emcVisible
                PropertyChanges {
                    target: emcControls
                    anchors.topMargin: 0
                }
                PropertyChanges {
                    target: emcControlsCover
                    y: 6
                }
                PropertyChanges {
                    target: emcControlsTitle
                    opacity: 1.0
                }
                PropertyChanges {
                    target: emcVolume
                    emcVisible: true
                }
            },
            State {
                name: "hidden"
                when: !emcControls.emcVisible
                PropertyChanges {
                    target: emcControls
                    anchors.topMargin: -150
                    visible: false
                }
                PropertyChanges {
                    target: emcControlsCover
                    y: -(height / 2)
                }
                PropertyChanges {
                    target: emcControlsTitle
                    opacity: 0.0
                }
                PropertyChanges {
                    target: emcVolume
                    emcVisible: false
                }
            }
        ]

        transitions: [
            Transition {
                from: "hidden"; to: "visible"
                SequentialAnimation {
                    PropertyAnimation {
                        duration: 0
                        property: "visible"
                    }
                    NumberAnimation {
                        easing.type: Easing.OutQuad
                        duration: 300
                        properties: "anchors.topMargin, opacity, y"
                    }
                }
            },
            Transition {
                from: "visible"; to: "hidden"
                SequentialAnimation {
                    NumberAnimation {
                        easing.type: Easing.InQuad
                        duration: 300
                        properties: "anchors.topMargin, opacity, y"
                    }
                    PropertyAnimation {
                        duration: 0
                        property: "visible"
                    }
                }
            }
        ]

    }

    EmcVolumeIndicator {
        id: emcVolume
    }

}

