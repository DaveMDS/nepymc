import QtQuick 2.12
import QtQuick.Controls 2.12
import "../utils/"


Popup {
    id: root

    property var model  // must be set on component creation

    width: 200  // TOSCALE
    height: emcMenuList.height

    modal: true
    focus: true
    padding: 0
    margins: 0
    //closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutsideParent

    Component.onCompleted: {
        y = parent.height  // open below the parent
        // TODO open above parent if the parent is in the bottom of the screen
        model.populate()
        root.open()
    }

    enter: Transition {
        NumberAnimation { property: "opacity"; from: 0.0; to: 1.0 }
    }
    exit: Transition {
        NumberAnimation { property: "opacity"; from: 1.0; to: 0.0 }
    }

    Overlay.modal: Rectangle {
        color: "#88000000"
    }

    contentItem: ListView {
        id: emcMenuList

        focus: true
         //width: contentWidth  // fail :/
        height: contentHeight  // OK

        model: root.model
        delegate: emcMenuItem

        Keys.onBackPressed: root.close()
        Keys.onEscapePressed: root.close()
        Keys.onDownPressed: {
            var original_index = emcMenuList.currentIndex
            // jump to the first enabled item
            while (emcMenuList.currentIndex < emcMenuList.count - 1) {
                emcMenuList.currentIndex += 1
                if (emcMenuList.currentItem.enabled)
                    break
            }
            // fix the case of the last item disabled (or a separator)
            if (emcMenuList.currentIndex == emcMenuList.count - 1) {
                if (!emcMenuList.currentItem.enabled)
                    emcMenuList.currentIndex = original_index
            }

        }
        Keys.onUpPressed: {
            var original_index = emcMenuList.currentIndex
            // jump to the first enabled item
            while (emcMenuList.currentIndex > 0) {
                emcMenuList.currentIndex -= 1
                if (emcMenuList.currentItem.enabled)
                    break
            }
            // fix the case of the first item disabled (or a separator)
            if (emcMenuList.currentIndex == 0) {
                if (!emcMenuList.currentItem.enabled)
                    emcMenuList.currentIndex = original_index
            }
        }
    }

    //
    //    MENU ITEM
    //
    Component {
        id: emcMenuItem

        Item {
            property bool is_separator: model.is_separator
            property bool is_checkable: model.checkable
            property bool is_disabled: model.disabled

            height: is_separator ? 5 : emcLabel.height
            width: parent.width
            enabled: is_disabled || is_separator ? false : true

            Image {  // separator item
                visible: is_separator
                source: "../pics/separator.png"
                width: parent.width
                anchors.centerIn: parent
            }

            Image {  // selection hilight
                visible: enabled && emcMenuList.currentIndex === model.index
                source: "../pics/vgrad_med_dark.png"
                anchors.fill: parent
            }

            EmcImage {  // checked state on the left
                id: emcIcon
                emcUrl: "icon/check_" + (model.checked ? "on" : "off")
                visible: is_checkable
                height: emcLabel.height
                width: is_checkable ? height : 0
            }

            EmcText {  // item label
                id: emcLabel
                padding: 4  // TOSCALE
                text: model.label
                anchors.right: emcIconEnd.left
                anchors.left: emcIcon.right
                color: enabled ? EmcGlobals.fontColor
                               : EmcGlobals.fontColorDisable
            }

            EmcImage {  // the icon on the right
                id: emcIconEnd
                emcUrl: model.icon
                visible: emcUrl
                height: emcLabel.height
                width: height
                anchors.right: parent.right
            }

            function activate_current() {
                root.model.item_activated(index)
                root.close()
            }
            MouseArea {
                anchors.fill: parent
                hoverEnabled: true
                onEntered: emcMenuList.currentIndex = index
                onClicked: activate_current()
            }
            Keys.onSelectPressed: activate_current()
        }
    }

    //
    //    MENU BACKGROUND
    //
    background: Rectangle {

        color: EmcGlobals.widgetBgColor

        BorderImage {  // bevel
            source: "../pics/bevel_out.png"
            border { left: 2; right: 2; top: 2; bottom: 2 }
            anchors.fill: parent
        }

        BorderImage {  // shadow
            source: "../pics/win_shadow.png"
            border { left: 8; right: 8; top: 8; bottom: 13 }
            anchors {
                fill: parent
                leftMargin: -7
                rightMargin: -7
                topMargin: -3
                bottomMargin: -11
            }
        }
    }
}

