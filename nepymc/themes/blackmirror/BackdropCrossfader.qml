import QtQuick 2.12

Item {
    id: root

    property url source

    onSourceChanged: {
        if (state === "show2")
            img1.source = source
        else
            img2.source = source
    }

    Rectangle {
        anchors.fill: parent
        color: "black"
    }

    Image {
        id: img1

        anchors.fill: parent
        asynchronous: true
        cache: false
        fillMode: Image.PreserveAspectCrop

        onStatusChanged: {
            if (status === Image.Ready)
                root.state = "show1"
        }
    }

    Image {
        id: img2

        anchors.fill: parent
        asynchronous: true
        cache: false
        fillMode: Image.PreserveAspectCrop

        onStatusChanged: {
            if (status === Image.Ready)
                root.state = "show2"
        }
    }

    states: [
        State {
            name: "show1"
            PropertyChanges { target: img1; opacity: 1.0 }
            PropertyChanges { target: img2; opacity: 0.0 }
        },
        State {
            name: "show2"
            PropertyChanges { target: img1; opacity: 0.0 }
            PropertyChanges { target: img2; opacity: 1.0 }
        }
    ]

    transitions: [
        Transition {
            from: "show1"; to: "show2"
            SequentialAnimation {
                NumberAnimation {
                    property: "opacity";
                    easing.type: Easing.InOutSine
                    duration: 1000
                }
                ScriptAction {
                    script: img1.source = ""
                }
            }
        },
        Transition {
            from: "show2"; to: "show1"
            SequentialAnimation {
                NumberAnimation {
                    property: "opacity";
                    easing.type: Easing.InOutSine;
                    duration: 1000
                }
                ScriptAction {
                    script: img2.source = ""
                }
            }
        }
    ]

}
