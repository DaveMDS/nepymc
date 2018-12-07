import QtQuick 2.11
import QtQuick.Controls 2.4
import "utils/"


FocusScope {
    anchors.fill: parent

    /***  Header  **************************************************************/
    BorderImage {  // background image
        width: parent.width
        height: header_text.height + 35
        source: "pics/header.png"
        border.left: 31
        border.right: 39
        border.top: 2
        border.bottom: 39
    }
    EmcTextBigger {  // header text
        id: header_text
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
            id: clock_date
            anchors {
                bottom: parent.bottom
                left: parent.left
                margins: 12
            }
            font.family: EmcGlobals.font3.name
            style: Text.Raised
        }

        EmcTextBigger {  // hour
            id: clock_time
            anchors {
                left: parent.left
                bottom: clock_date.top
                leftMargin: 12
            }
            font.family: EmcGlobals.font3.name
            style: Text.Raised
        }

        function timeChanged() {
            var now = new Date
            //console.log(now)
            clock_time.text = now.toLocaleTimeString(EmcGlobals.locale, Locale.ShortFormat)
            clock_date.text = now.toLocaleDateString(EmcGlobals.locale, Locale.LongFormat)
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
        id: list_background

        width: parent.width
        height: 128
        y: header_text.height + 100
        source: "pics/mainmenu_bg.png"
        border { top: 7; bottom: 13 }
        opacity: 0.7

        Image {
            source: "pics/shine_large.png"
            anchors.top: parent.top
            anchors.topMargin: 4
            anchors.horizontalCenter: parent.horizontalCenter
        }
    }

    ListView {
        id: main_list

        anchors.fill: list_background
        anchors.leftMargin: 100
        anchors.rightMargin: 100
        orientation: ListView.Horizontal
        focus: true
        clip: false

        displayMarginBeginning: 100
        displayMarginEnd: 100

        model: MainMenuModel  // injected from python
        delegate: main_list_delegate
    }


    // main list item delegate
    Component {
        id: main_list_delegate

        Item { // MainMenu items
            id: main_list_item

            width: 128  //width: childrenRect.width
            height: 128   //height: childrenRect.height
            focus: true

            Keys.onReturnPressed: {
                console.log(model.icon) // TODO REMOVE ME
    //                EmcBackend.mainmenuItemSelected(model.icon)
    //                var translated = EmcBackend.i18n(model.label)
    //                console.log(translated)
            }

            // give focus to the sublist on DOWN pressed
            Keys.onDownPressed: {
                sub_list.focus = true
            }

            Rectangle {
                id: positioner

                width: 128
                height: 128
                visible: false
            }

            Image {
                id: item_icon

                source: "pics/icon_" + model.icon + ".png"
                fillMode: Image.PreserveAspectFit
                mipmap: true
                anchors.fill: positioner
                anchors.margins: 16
            }

            EmcTextBigger {
                id: item_text

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

            ListView {
                id: sub_list

                anchors.top: parent.bottom
                height: 1000  // TODO FILL IN WINDOW

                model: subItems
                delegate: sub_list_delegate

                // select the first item when the sublist take the focus
                onFocusChanged: {
                    if (focus) {
                        currentIndex = 0
                    }
                }

                // give focus back to the main item if UP pressed on first item
                Keys.onUpPressed: {
                    if (currentIndex == 0) {
                        main_list_item.focus = true
                    } else {
                        event.accepted = false  // let the ListView manage it
                    }
                }

            }

            states: [
                State {
                    name: "active"
                    when: main_list_item.ListView.isCurrentItem
                    PropertyChanges {
                        target: item_icon
                        anchors.margins: 0
                    }
                    PropertyChanges {
                        target: item_text
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

    // subList delegate
    Component {
        id: sub_list_delegate

        EmcTextBig {
            property bool active: false

            text: modelData.label
            font.family: EmcGlobals.font3.name
            style: Text.Raised

            BorderImage {
                height: parent.height
                width: 128  // TODO link with positioner.width
                z: -1
                source: "pics/menu_bg_submenu.png"
                border { top: 1; bottom: 1 }

                visible: parent.ListView.isCurrentItem && parent.activeFocus

                Image {
                    y: parent.y - 2
                    anchors.horizontalCenter: parent.horizontalCenter
                    source: "pics/shine_large.png"
                }
            }
        }
    }

}
