import QtQuick
import QtQuick.Controls
import "."
import "utils/"
import "components/"


Item {
    id: emcBrowserListView

    property bool infoVisible: false
    property bool posterVisible: false

    property alias currentIndex: emcBrowserList.currentIndex

    Timer {  // info box and big image are delayed
        id: emcInfoDelayTimer
        interval: 500; running: false; repeat: false
        onTriggered: {
            var data = BrowserModel.get(currentIndex, "info");
            if (data) {
                emcBrowserInfoText.text = data
                infoVisible = true
            } else {
                // hide animation will run, not clearing the text
                infoVisible = false
            }
            data = BrowserModel.get(currentIndex, "poster") ||
                   BrowserModel.get(currentIndex, "cover")
            if (data) {
                emcBrowserPoster.emcUrl = data
                posterVisible = true
            } else {
                // hide animation will run, not clearing the image
                posterVisible = false
            }
        }
    }

    Timer {  // backdrop (fanart) still more delayed
        id: emcBackdropDelayTimer
        interval: 1000; running: false; repeat: false
        onTriggered: {
            var data = BrowserModel.get(currentIndex, "fanart")
            if (data)
                emcApplicationWindow.backdropSource = data
        }
    }

    /**  List View (inside a big frame)  **************************************/
    BorderImage {
        anchors.fill: parent
        anchors.rightMargin: parent.width / 2
        anchors.bottomMargin: -13
        source: "pics/frame.png"
        border { left: 32; right: 32; top: 92; bottom: 78 }

        ListView {
            id: emcBrowserList

            onCurrentIndexChanged: {
                emcInfoDelayTimer.restart()
                emcBackdropDelayTimer.restart()
            }

            anchors {
                fill: parent
                leftMargin: 19
                rightMargin: 19
                topMargin: 18
                bottomMargin: 77
            }
            clip: true
            focus: true

            model: BrowserModel  // implemented in python
            delegate: emcBrowserListItemComponent

            ScrollBar.vertical: ScrollBar { }
            boundsMovement: Flickable.StopAtBounds
            highlightMoveDuration: 0
            highlightMoveVelocity: -1
            pixelAligned: true
            reuseItems: true
        }
    }

    /**  Info box  ************************************************************/
    BorderImage {
        id: emcBrowserInfo

        source: "pics/frame2.png"
        border { left: 8; right: 8; top: 8; bottom: 8 }

        width: parent.width / 2
        height: parent.height / 2.66
        anchors.right: parent.right  // align right
        anchors.bottom: parent.bottom  // align bottom
        anchors.bottomMargin: -height // hidden below the window

        EmcText {
            id: emcBrowserInfoText

            anchors {
                fill: parent
                topMargin: 9
                leftMargin: 15
                rightMargin: 12
                bottomMargin: 10
            }
        }

        states: State {
            name: "visible"
            when: infoVisible
            PropertyChanges {
                target: emcBrowserInfo
                anchors.bottomMargin: 7
            }
        }
        transitions: Transition {
            from: ""; to: "visible"; reversible: true
            NumberAnimation {
                easing.type: Easing.OutCubic
                duration: 350
                properties: "anchors.bottomMargin"
            }
        }
    }

    /**  Big poster/cover  ****************************************************/
    EmcImage {
        id: emcBrowserPoster

        width: parent.width / 2
        anchors.right: parent.right  // align right
        anchors.bottom: emcBrowserInfo.top
        anchors.bottomMargin: 7
        anchors.top: parent.top
        anchors.rightMargin: -(width + 25) // hidden outside the window

        states: State {
            name: "visible"
            when: posterVisible
            PropertyChanges {
                target: emcBrowserPoster
                anchors.rightMargin: 7
            }
        }
        transitions: Transition {
            from: ""; to: "visible"; reversible: true
            NumberAnimation {
                easing.type: Easing.OutCubic
                duration: 350
                properties: "anchors.rightMargin"
            }
        }
    }

    /**  List Items Delegate **************************************************/
    Component {
        id: emcBrowserListItemComponent

        Item {
            id: emcBrowserListItem

            width: parent.width
//           height: childrenRect.height  // TODO should fit the font
            height: 42

            Keys.onSelectPressed: {
                BrowserModel.item_selected(index)
            }

            BorderImage {  // selection highlight background
                anchors.fill: parent
                source: "pics/list_item_sel_bg.png"
                border { top: 1; bottom: 1 }
                opacity: 0.25
                visible: parent.ListView.isCurrentItem
            }

            EmcImage {  // left icon
                id: emcIcon
                emcUrl: model.icon
                width: emcUrl ? parent.height : 0
                height: parent.height
                x: 3
            }

            EmcImage {  // right icon
                id: emcIconEnd
                emcUrl: model.icon_end
                width: emcUrl ? parent.height : 0
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

            EmcFocusLight {
                anchors.fill: parent
                visible: emcBrowserListItem.activeFocus
            }

            MouseArea {
                anchors.fill: parent
                onClicked: {
                    emcBrowserList.currentIndex = index
                    emcBrowserListItem.forceActiveFocus()
                }
                onDoubleClicked: BrowserModel.item_selected(index)
            }
        }
    }
}
