import QtQuick 2.12
import QtQuick.Controls 2.12


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


