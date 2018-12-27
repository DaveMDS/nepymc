import QtQuick 2.12
import "../utils/"
import "../utils/utils.js" as Utils


EmcFocusManager {
    id: emcDialog
    objectName: "EmcDialog: " + title

    property string title: ""
    property string main_text: ""
    property string content: ""
    property bool bigger: false
    property bool spinner: false

    function action_add(idx, label, icon) { /* TODO THEME API */
        console.log("QML button add " + idx + " " + label)

        // keep a reference to the last button (for the focus chain)
        var last = emcFooter.children[emcFooter.children.length - 1]

        // create a new EmcButton
        var btn = Utils.load_qml_obj("components/EmcButton.qml", emcFooter,
                                     {idx: idx, label: label, icon: icon})

        if (!last) {
            // first button, focus by default
            btn.forceActiveFocus()
        } else {
            // Build up the focus chain between buttons
            btn.KeyNavigation.left = last
        }

        return btn
    }

    function emcDestroy() { /* TODO THEME API */
        opacity = 0.0  // fade out
        focusAllow = false
        focus = false
        destroy(500)  // destroy after the fadeout
    }

    Keys.onUpPressed: emcMainText.ScrollBar.vertical.decrease()
    Keys.onDownPressed: emcMainText.ScrollBar.vertical.increase()

    anchors.fill: parent
    opacity: 0.0

    Behavior on opacity { NumberAnimation { duration: 200 } }
    Component.onCompleted: opacity = 1.0


    BorderImage {  // dialog background
        id: emcBG

        source: "../pics/dialog_bg.png"
        border { left: 15; right: 15; top: 15; bottom: 15 }

        width: bigger ? parent.width / 1.2 : parent.width / 1.9
        height: bigger ? parent.height / 1.2 : parent.height / 1.85
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter

        EmcTextBig {  // title
            id: emcTitle

            color: EmcGlobals.fontColorTitle
            font.family: EmcGlobals.font2.name
            text: title
            width: parent.width
            height: text != "" ? undefined : 10
            padding: 9
            horizontalAlignment: Text.AlignHCenter
        }

        Image {  // content image
            id: emcContentImage
            source: content != "" ? "../pics/" + content : ""
            fillMode: Image.PreserveAspectFit
            width: source != "" ? parent.width / 2.5 : 0
            x: 10
            anchors.top: emcMainText.top
            anchors.bottom: emcMainText.bottom
        }

        EmcScrollText {  // main scrollable text content
            id: emcMainText

            text: main_text
//            focusPolicy: Qt.NoFocus  // doesn't seems to work

            anchors {
                top: emcTitle.bottom
                bottom: emcSpinner.top
                left: emcContentImage.right
                right: parent.right
                rightMargin: 9
            }
        }

        EmcSpinner {
            id: emcSpinner
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: emcFooter.top
            visible: spinner
            height: spinner ? 40 : 0
        }

        Row {  // row of buttons in the footer
            id: emcFooter

//          layoutDirection: Qt.RightToLeft  // THIS WAS EPYMC BEHAVIOUR !!
            padding: 9
            spacing: 2

            anchors.bottom: parent.bottom
            anchors.horizontalCenter: parent.horizontalCenter
//            EmcButton { id: f1; label: "f1"; KeyNavigation.right: f2 }
//            EmcButton { id: f2; label: "f2"; KeyNavigation.left: f1 }
        }

    }
}
