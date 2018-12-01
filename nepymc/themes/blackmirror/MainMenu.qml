import QtQuick 2.11
import QtQuick.Controls 2.4
import "utils/"


FocusScope {
    anchors.fill: parent

    /***  Header  **************************************************************/
    BorderImage {  // background image
        width: parent.width
        height: headerText.height + 35
        source: "pics/header.png"
        border.left: 31
        border.right: 39
        border.top: 2
        border.bottom: 39
    }
    EmcTextBigger {  // header text
        id: headerText
        text: "Emotion Media Center"
        anchors.horizontalCenter: parent.horizontalCenter
        font.family: EmcGlobals.font3.name
        style: Text.Raised
        opacity: 0.8
    }


    /***  Clock  ***************************************************************/
    Item {
        id: clock
        anchors.fill: parent

        EmcTextBig {  // date
            id: clockDate
            anchors {
                bottom: parent.bottom
                left: parent.left
                margins: 12
            }
            font.family: EmcGlobals.font3.name
            style: Text.Raised
        }

        EmcTextBigger {  // hour
            id: clockTime
            anchors {
                left: parent.left
                bottom: clockDate.top
                leftMargin: 12
            }
            font.family: EmcGlobals.font3.name
            style: Text.Raised
        }

        function timeChanged() {
            var now = new Date
            //console.log(now)
            clockTime.text = now.toLocaleTimeString(EmcGlobals.locale, Locale.ShortFormat)
            clockDate.text = now.toLocaleDateString(EmcGlobals.locale, Locale.LongFormat)
        }

        Timer {
            interval: 1000
            running: true
            repeat: true
            triggeredOnStart: true
            onTriggered: clock.timeChanged()
        }
    }


    /***  List  ****************************************************************/
    BorderImage {
        id: listBackground

        width: parent.width
        height: 128
        y: headerText.height + 100
        source: "pics/mainmenu_bg.png"
        border { top: 7; bottom: 13 }
        opacity: 0.7

        Image {
            source: "pics/shine_large.png"
            anchors.top: parent.top
            anchors.topMargin: 4
            anchors.horizontalCenter: parent.horizontalCenter
            opacity: 1.0
        }
    }

    ListView {
        id: mainMenuList

        anchors.fill: listBackground
        anchors.leftMargin: 100
        anchors.rightMargin: 100
        orientation: ListView.Horizontal
        focus: true
        clip: false

        displayMarginBeginning: 100
        displayMarginEnd: 100

        model: MainMenuModel  // implemented in python
        delegate: itemDelegateComponent
    }



    // main item delegate
    Component {
        id: itemDelegateComponent

        Item { // MainMenu items
            id: delegateItem

            width: 128  //width: childrenRect.width
            height: 128   //height: childrenRect.height
            focus: true

            Keys.onReturnPressed: {
                console.log(model.icon) // TODO REMOVE ME
    //                EmcBackend.mainmenuItemSelected(model.icon)
    //                var translated = EmcBackend.i18n(model.label)
    //                console.log(translated)
            }

            Rectangle {
                id: positioner
                width: 128
                height: 128
                visible: false
            }

            Image {
                id: itemIcon

                source: "pics/icon_" + model.icon + ".png"
                fillMode: Image.PreserveAspectFit
                mipmap: true
                anchors.fill: positioner
                anchors.margins: 16
            }

            EmcTextBigger {
                id: itemText

                text: model.label
                anchors {
                    bottom: positioner.top
                    left: positioner.left
                    right: positioner.right
                }
                horizontalAlignment: Text.AlignHCenter
                font.family: EmcGlobals.font3.name
                font.pixelSize: EmcGlobals.fontSizeBigger / 2
                style: Text.Outline
                opacity: 0.0;
            }

            Column {
                anchors.top: positioner.bottom
                Repeater {
                    model: subItems
                    delegate: subitemDelegate
                }
            }

            states: [
                State {
                    name: "active"
                    when: delegateItem.ListView.isCurrentItem
                    PropertyChanges {
                        target: itemIcon
                        anchors.margins: 0
                    }
                    PropertyChanges {
                        target: itemText
                        font.pixelSize: EmcGlobals.fontSizeBigger
                        opacity: 1.0
                    }
                }
            ]

            transitions: Transition {
                from: ""; to: "active"; reversible: true
                NumberAnimation {
                    duration: 200
                    properties: "anchors.margins, font.pixelSize, opacity"
                }
            }

        }
    }

    // subitems delegate
    Component {
        id: subitemDelegate
        EmcTextBig {
            text: modelData.label
            font.family: EmcGlobals.font3.name
            style: Text.Raised
        }
    }

}
