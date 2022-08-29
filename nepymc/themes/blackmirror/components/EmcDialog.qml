import QtQuick
import "../components/"
import "../utils/"
import "../utils/utils.js" as Utils


EmcFocusManager {
    id: root
    objectName: "EmcDialog: " + title

    /* TODO THEME API */
    property string title: ""
    property string main_text: ""
    property string content: ""
    property bool bigger: false
    property bool spinner: false
    property double progress: -1.0  // 0->1  -1=do not show
    property var list_model: undefined
    property string style: ""

    signal emcQuitRequested()

    function action_add(idx, label, icon, def) { /* TODO THEME API */
        console.log("QML button add " + idx + " " + label)

        // keep a reference to the last button (for the focus chain)
        var last = emcFooter.children[emcFooter.children.length - 1]

        // create a new EmcButton
        var btn = Utils.load_qml_obj("components/EmcButton.qml", emcFooter,
                                     {idx: idx, label: label, icon: icon})

        if (!last) {
            // first button focus by default
            btn.forceActiveFocus()
        } else {
            // Build up the focus chain between buttons
            btn.KeyNavigation.right = last
        }
        if (def) {
            btn.forceActiveFocus()
        }

        return btn
    }

    function actions_clear() { /* TODO THEME API */
        for(var i = emcFooter.children.length; i > 0 ; i--) {
            emcFooter.children[i-1].destroy()
        }
        emcFooter.children = []
    }

    function emcDestroy() {  /* TODO THEME API */
        opacity = 0.0  // fade out
        focusAllow = false
        focus = false
        destroy(500)  // destroy after the fadeout
    }

    Keys.onPressed: {
        switch(event.key) {
        case Qt.Key_Back:
        case Qt.Key_Exit:
            root.emcQuitRequested()
            event.accepted = true
            break
        case Qt.Key_Up:
            if (root.list_model)
                emcList.decrementCurrentIndex()
            else
                emcMainText.scrollUp()
            event.accepted = true
            break
        case Qt.Key_Down:
            if (root.list_model)
                emcList.incrementCurrentIndex()
            else
                emcMainText.scrollDown()
            event.accepted = true
            break
        case Qt.Key_Right:
            if (root.style === "image_list_portrait") {
                emcList.incrementCurrentIndex()
                event.accepted = true
            }
            break
        case Qt.Key_Left:
            if (root.style === "image_list_portrait") {
                emcList.decrementCurrentIndex()
                event.accepted = true
            }
            break
        }
    }

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

        EmcImage {  // content image
            id: emcContentImage

            emcUrl: root.content

            width: root.content != "" ? parent.width / 2.5 : 0
            x: 10
            anchors.top: emcMainText.top
            anchors.bottom: emcMainText.bottom
        }

        EmcScrollText {  // main scrollable text content
            id: emcMainText

            visible: !list_model

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

        EmcList {
            id: emcList

            model: root.list_model
            delegate_name: style.startsWith('image_list') ?
                               "EmcImageListItemDelegate.qml" :
                               "EmcListItemDelegate.qml"
            orientation: style === 'image_list_portrait' ?
                             ListView.Horizontal :
                             ListView.Vertical

            anchors {
                top: emcTitle.bottom
                bottom: emcSpinner.top
                left: parent.left
                right: parent.right
                leftMargin: 10
                rightMargin: 10
            }
        }

        EmcSpinner {
            id: emcSpinner

            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: emcProgress.top
            visible: spinner
            height: spinner ? 40 : 0
        }

        EmcProgressBar {  // optional progress bar
            id: emcProgress

            value: root.progress
            visible: root.progress != -1

            anchors {
                left: parent.left
                leftMargin: 18
                right: parent.right
                rightMargin: 18
                bottom: emcFooter.top
            }
        }

        Row {  // row of buttons in the footer
            id: emcFooter

            layoutDirection: Qt.RightToLeft  // THIS WAS EPYMC BEHAVIOUR !!
            padding: 9
            spacing: 2

            anchors.bottom: parent.bottom
            anchors.horizontalCenter: parent.horizontalCenter
//            EmcButton { id: f1; label: "f1"; KeyNavigation.right: f2 }
//            EmcButton { id: f2; label: "f2"; KeyNavigation.left: f1 }
        }

    }
}
