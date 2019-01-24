import QtQuick 2.12
import QtQuick.Layouts 1.12


BorderImage {
    id: root

    property bool emcVisible: false
    property alias emcVolumeValue: emcVolumeSlider.value

    source: "../pics/frame_box_bottom.png"
    border { left: 17; right: 17; top: 17; bottom: 0 }

    width: 440; height: 55
    anchors.horizontalCenter: parent.horizontalCenter
    anchors.bottom: parent.bottom

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 22
        anchors.rightMargin: 22
        anchors.topMargin: 17

        Image {
            id: emcVolumeIcon
            source: "../pics/volume.png"  // TODO volume_muted.png
            Layout.preferredWidth: 40
            Layout.preferredHeight: 40
            Layout.fillHeight: true
        }

        EmcSlider {
            id: emcVolumeSlider
            Layout.fillWidth: true
            Layout.fillHeight: true
        }
    }

    states: [
        State {
            name: "visible"
            when: emcVisible
            PropertyChanges {
                target: root
                anchors.bottomMargin: 0
                visible: true
            }
        },
        State {
            name: "hidden"
            when: !emcVisible
            PropertyChanges {
                target: root
                anchors.bottomMargin: -height
                visible: false
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
                    properties: "anchors.bottomMargin"
                }
            }
        },
        Transition {
            from: "visible"; to: "hidden"
            SequentialAnimation {
                NumberAnimation {
                    easing.type: Easing.InQuad
                    duration: 300
                    properties: "anchors.bottomMargin"
                }
                PropertyAnimation {
                    duration: 0
                    property: "visible"
                }
            }
        }
    ]

}
