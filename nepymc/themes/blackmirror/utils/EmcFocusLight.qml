import QtQuick
import QtQuick.Controls


Item {

    BorderImage {
        source: "../pics/box_glow.png"
        border { left: 12; right: 12; top: 12; bottom:12 }
        anchors {
            fill: parent
            leftMargin: -6
            rightMargin: -6
            topMargin: -6
            bottomMargin: -6
        }
    }

    // TODO make this thing pulse

}


