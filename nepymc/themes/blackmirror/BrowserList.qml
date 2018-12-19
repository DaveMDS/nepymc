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
            focus: true

            model: BrowserModel  // impemented python (label, icon)
            delegate: emcBrowserListComponent

            ScrollBar.vertical: ScrollBar { }

        }
    }

    /**  List Items  **********************************************************/
    Component {
        id: emcBrowserListComponent

        Item {
            id: emcBrowserListItem

            width: parent.width
//           height: childrenRect.height  // TODO should fit the font
            height: 42

            Keys.onReturnPressed: {
                console.log(model.label) // TODO REMOVE ME
//                EmcBackend.browser_item_selected(model.icon)
                EmcBackend.browser_item_selected(ListView.view.currentIndex)
            }

            BorderImage {  // selection highlight background
                anchors.fill: parent
                source: "pics/list_item_sel_bg.png"
                border { top: 1; bottom: 1 }
                opacity: 0.25
                visible: parent.ListView.isCurrentItem
            }

            Image {  // left icon
                id: emcIcon
                source: model.icon ? "pics/icon_" + model.icon + ".png" : ""
                width: source != "" ? parent.height : 0
                height: parent.height
            }

            Image {  // right icon
                id: emcIconEnd
                source: model.icon_end ? "pics/icon_" + model.icon_end + ".png" : ""
                width: source != "" ? parent.height : 0
                height: parent.height
                anchors.right: parent.right
            }

            EmcText {  // main label
                id: emcLabel
                text: model.label
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: emcIcon.right
                anchors.right: emcLabelEnd.left
                // TODO make this autoscrollable! EmcSlideText ??
            }

            EmcText {  // right label
                id: emcLabelEnd
                text: model.label_end ? model.label_end : ""// TODO are 2 calls ??
                font.pixelSize: EmcGlobals.fontSize - 2
                color: EmcGlobals.fontColorDisable
                anchors.verticalCenter: parent.verticalCenter
                anchors.right: emcIconEnd.left
            }

            Image {  // separator
                source: "pics/separator.png"
                height: 2
                width: parent.width
                y: parent.height - 1
            }

            BorderImage {  // selection highlight foreground
                anchors.fill: parent
                anchors.bottomMargin: parent.height / 2
                source: "pics/list_item_sel_fg.png"
                border { top: 1; bottom: 1 }
                opacity: 0.25
                visible: parent.ListView.isCurrentItem
            }
        }
    }



}
