import QtQuick 2.11
import QtQuick.Controls 2.4
import "."
import "utils/"




Item {

    BorderImage {
        anchors.fill: parent
        source: "pics/frame.png"
        border { left: 32; right: 32; top: 92; bottom: 78 }

        ListView {
            anchors {
                fill: parent
                leftMargin: 19
                rightMargin: 19
                topMargin: 18
                bottomMargin: 77
            }
            clip: true

            model: BrowserModel  // impemented python (label, icon)
            delegate: BrowserListItem { }

            ScrollBar.vertical: ScrollBar {}

            DebugRect {
                color: "green"
            }
        }


    }



}