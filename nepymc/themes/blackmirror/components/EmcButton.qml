import QtQuick 2.12
import QtQuick.Controls 2.12
import "../utils/"

Item {
    id: root

    /* THEME API */
    property alias label: emcLabel.text
    property string icon: ""
    property int idx  // TODO usato da Dilalog... NON E' IL SUO POSTO !!

    // signal emitted when whe button is pressed (with mouse or keys)
    signal emcButtonClicked(int idx)

    width: emcBG.width
    height: emcBG.height

    Keys.onSelectPressed: emcButtonClicked(idx)

    Row {
        id: emcRow

        Image {  // button icon
            id: emcIcon
            source: icon != "" ? "../pics/" + icon + ".png" : ""
            height: emcLabel.height * 1.125
            width: icon != "" ? height : 5
        }

        EmcText {  // button label
            id: emcLabel
            text: label
        }
    }

    BorderImage {  // button background
        id: emcBG

        z: -1
        source: "../pics/button_normal.png"
        border {left: 4; right: 4; top:3; bottom: 5}

        anchors {
            fill: emcRow
            leftMargin: -4
            rightMargin: -9
            topMargin: -2
            bottomMargin: -4
        }
    }

    EmcFocusLight {
        id: emcFocus
        anchors.fill: emcBG
        visible: root.activeFocus
    }

    MouseArea {
        anchors.fill: emcBG
        onClicked: emcButtonClicked(idx)
        onPressed: {
            emcBG.source = "../pics/button_clicked.png"
            root.forceActiveFocus()
        }
        onReleased: {
            emcBG.source = "../pics/button_normal.png"
        }
    }
}
