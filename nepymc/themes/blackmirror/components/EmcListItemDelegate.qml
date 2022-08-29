import QtQuick
import "../utils/"

/*
 *  A standard emc list item, the model must implement the fields:
 *   -label
 *   -label_end
 *   -icon
 *   -icon_end
 *
 *  Can only be used in vertical views
 */

Item {
    id: root

    width: view.width
    height: emcLabel.height


    BorderImage {  // selection highlight background
        anchors.fill: parent
//        anchors.bottomMargin: parent.height / 2  // FOR BROWSER
//        source: "../pics/list_item_sel_fg.png"  // FOR BROWSER
//        opacity: 0.25 // FOR BROWSER
        source: "../pics/list_selection.png"
        border { top: 2; bottom: 2 }
        visible: view.currentIndex === model.index

        Image { // shine
            source: "../pics/shine.png"
            anchors.top: parent.top
            anchors.topMargin: -2
            anchors.horizontalCenter: parent.horizontalCenter
        }
        BorderImage { //shadow
            source: "../pics/shadow_rounded_horiz.png"
            border.top: 9
            border.bottom: 9
            anchors.fill: parent
            anchors.topMargin: -4
            anchors.bottomMargin: -6
            z: -1
        }
    }

    Row {
        id: emcRightRow
        anchors.right: parent.right
        anchors.rightMargin: 4
        spacing: 3

        EmcText { // right (end) label
            id: emcLabelEnd

            text: model.label_end ? model.label_end : ""
            font.pixelSize: EmcGlobals.fontSize - 2
            color: EmcGlobals.fontColorDisable

            verticalAlignment: Text.AlignVCenter
            height: emcLabel.height
        }

        EmcImage {  // right (end) icon
            id: emcIconEnd
            emcUrl: model.icon_end
            visible: emcUrl
            height: emcLabel.height
            width: height
        }
    }

    Row {
        id: emcLeftRow

        anchors.left: parent.left
        anchors.leftMargin: 4
        anchors.right: emcRightRow.left
        spacing: 3

        EmcImage {  // main (left) icon
            id: emcIcon
            emcUrl: model.icon
            visible: emcUrl
            height: emcLabel.height
            width: height
        }

        // TODO make this text "slide-able"
        EmcText {  // main (left) label
            id: emcLabel
            padding: 4
            text: model.label
        }
    }
//    DebugRect {color:"blue";anchors.fill: emcLeftRow}


    Image {  // separator
        source: "../pics/separator.png"
        height: 2
        width: parent.width
        anchors.bottom: parent.bottom
        anchors.bottomMargin: -2
    }

    MouseArea {
        anchors.fill: parent
        onClicked: {
            view.currentIndex = index
        }
        onDoubleClicked: {
            view.model.item_activated(index)
        }
    }

}
