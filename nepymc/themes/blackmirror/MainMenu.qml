import QtQuick 2.11
import QtQuick.Controls 2.4
import "utils/"


FocusScope {
    id: emcMainMenu

    property bool emc_active: true

    anchors.fill: parent

//    function show() {
//        console.log("SHOW MAINMENU")
//        emc_active = true
//    }
//    function hide() {
//        console.log("HIDE MAINMENU")
//        emc_active = false
//    }

    /***  Header  *************************************************************/
    EmcTextBigger {  // header text
        id: emcHeaderText

        text: EmcBackend.application_name()
        anchors.horizontalCenter: emcMainMenu.horizontalCenter
        anchors.top: parent.top
        font.family: EmcGlobals.font3.name
        style: Text.Raised
        opacity: 0.8

//        anchors.bottom: parent.emc_visible ? undefined : parent.top

        BorderImage {  // background image
            x: -parent.x
            z: -1
            width: emcMainMenu.width
            height: parent.height + 35
            source: "pics/header.png"
            border { left: 31; right: 39; top: 2; bottom: 39 }
        }
    }

    /***  Clock  **************************************************************/
    Item {
        id: emcClock
        anchors.fill: parent

        EmcTextBig {  // date
            id: emcClockDate

            text: EmcGlobals.date_long  // auto-updating property binding
            font.family: EmcGlobals.font3.name
            style: Text.Raised
            anchors {
                bottom: parent.bottom
                left: parent.left
                margins: 12
            }
        }

        EmcTextBigger {  // hour
            id: emcClockTime

            text: EmcGlobals.time_short  // auto-updating property binding
            font.family: EmcGlobals.font3.name
            style: Text.Raised
            anchors {
                left: parent.left
                bottom: emcClockDate.top
                leftMargin: 12
            }
        }
    }

    /***  List  ***************************************************************/
    BorderImage {
        id: list_background

        width: parent.width
        height: 128
        y: emcHeaderText.height + 100
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
        //model: mainMenuModelTEST  // defined in this file (for testing)
        delegate: main_list_delegate
    }

    /***  Hidden state  *******************************************************/
    states: State {
        name: "hidden"
        when: !emc_active
        PropertyChanges {
            target: emcHeaderText
            anchors.topMargin: -(height + 35)
            opacity: 0.0
        }
        PropertyChanges {
            target: emcClock
            opacity: 0.0
        }
        PropertyChanges {
            target: list_background
            y: -height
        }
    }

    transitions: [
        Transition {
            from: ""; to: "hidden";
            SequentialAnimation {
                NumberAnimation {
                    duration: 200
                    properties: "anchors.topMargin, y, opacity"
                }
                ScriptAction { script: visible = false; }
            }
        },
        Transition {
            from: "hidden"; to: "";
            SequentialAnimation {
                ScriptAction { script: visible = true; }
                NumberAnimation {
                    duration: 200
                    properties: "anchors.topMargin, y, opacity"
                }
            }
        }
    ]

    /***  Main List item delegate  ********************************************/
    Component {
        id: main_list_delegate

        Item { // MainMenu items
            id: main_list_item

            width: 128  //width: childrenRect.width
            height: 128   //height: childrenRect.height

            Keys.onReturnPressed: {
                console.log(model.icon) // TODO REMOVE ME
//                    EmcBackend.mainmenu_item_selected(model.icon)
                    EmcBackend.mainmenu_item_selected(ListView.view.currentIndex)
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

                source: "pics/" + model.icon + ".png"
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
                opacity: 0.0
            }

            ListView {
                id: sub_list

                anchors.top: parent.bottom
                height: 1000  // TODO FILL IN WINDOW
                opacity: 0.0

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
                        target: sub_list
                        opacity: 1.0
                    }
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

    /***  Sub List item delegate  *********************************************/
    Component {
        id: sub_list_delegate

        EmcTextBig {
            property bool active: false

            // modelData when using python model, label otherwise (in testing)
            text: modelData.label ? modelData.label : label
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

    /*  This model can be used in place of the one from python for testing
    ListModel {
        id: mainMenuModelTEST

        ListElement {
            label: "Optical Discs"
            icon: "optical"
            subItems: [
                ListElement { label: "Play" },
                ListElement { label: "Eject" }
            ]
        }
        ListElement {
            label: "Music"
            icon: "music"
            subItems: [
                ListElement { label: "Artists" },
                ListElement { label: "Albums" },
                ListElement { label: "Songs" }
            ]
        }
        ListElement {
            label: "Film"
            icon: "movie"
            subItems: [
                ListElement { label: "Folder 1" },
                ListElement { label: "Folder 2" }
            ]
        }
        ListElement {
            label: "Photo"
            icon: "photo"
            subItems: [ ]
        }
        ListElement {
            label: "Settings"
            icon: "config"
            subItems: [ ]
        }
        ListElement {
            label: "Quit"
            icon: "exit"
            subItems: [ ]
        }
    }
    */
}
