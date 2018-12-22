import QtQuick 2.11
import QtQuick.Controls 2.4
import "utils/"


Item {
    width: parent.width
    height: emcTitle.height

    property string title

    BorderImage {  // background image
        id: emcBG
        source: "pics/header.png"
        border { left: 31; right: 39; top: 2; bottom: 39 }
        width: parent.width
        height: parent.height + 33
    }

    Image {  // left icon
        id: emcIcon
        source: "pics/icon/home.png"
        width: parent.height + 4
        height: parent.height + 4
        x: 20
    }

    EmcTextTopbar {  // title
        id: emcTitle
        text: title
        anchors.left: emcIcon.right
        y: 3
    }

    EmcTextTopbar {  // clock
        id: emcClock
        text: EmcGlobals.time_short  // auto-updating property binding
        anchors.right: parent.right
        anchors.rightMargin: 35
        y: 3
    }
}
