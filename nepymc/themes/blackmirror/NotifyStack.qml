import QtQuick
import "components/"
import "utils/"

Item {
    id: root

    ListView {
        id: emcStackList

        anchors.fill: parent
        orientation: ListView.Vertical
        interactive: false

        model: EmcNotifyModel  // injected from python
        delegate: emcStackItemDelegate

        add: Transition {
            id: addTrans
            PropertyAnimation {
                property: "anchors.rightMargin"
                from: -addTrans.ViewTransition.item.width; to: 0
                duration: 300; easing.type: Easing.OutSine
            }
        }

        remove: Transition {
            id: removeTrans
            PropertyAnimation {
                property: "anchors.rightMargin"
                from: 0; to: -removeTrans.ViewTransition.item.width
                duration: 300; easing.type: Easing.InSine
            }
        }

        displaced: Transition {
            PropertyAnimation {
                property: "y"
                duration: 300; easing.type: Easing.InOutSine
            }
        }
    }

    Component {
        id: emcStackItemDelegate

        Item {

            width: emcBackground.width
            height: emcBackground.height
            anchors.right: parent.right

            BorderImage {
                id: emcBackground

                source: "pics/notify_bg.png"
                border { left: 13; right: 0; top: 8; bottom: 8 }

                anchors {
                    fill: emcContentRow
                    topMargin: -8
                    bottomMargin: -8
                }
            }

            Row {
                id: emcContentRow

                leftPadding: 12
                rightPadding: 12
                spacing: 12

                EmcImage {
                    id: emcImage
                    emcUrl: model.image
                    height: 100
                    width: 100
                }

                EmcTextBig {
                    id: emcText
                    text: model.text
                    color: EmcGlobals.fontColorInverse
                    width: Math.max(implicitWidth, 250)
                    height: Math.max(implicitHeight, 100)
                }
            }
        }
    }
}
