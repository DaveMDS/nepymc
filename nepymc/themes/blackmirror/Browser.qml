import QtQuick 2.11
import QtQuick.Controls 2.4
import "utils/"


FocusScope {
    id: emcBrowser

    property bool emc_active: false

//    property bool focus: emcBrowserList.focus

    anchors.fill: parent

//    function show() {
//        console.log("SHOW BROWSER")
//        emcBrowserList.focus = true
//    }
//    function hide() {
//        console.log("HIDE BROWSER")
//    }



    /***  TopBar  *************************************************************/
    EmcTextBig {  // header text
        id: emcBrowserHeader

        text: "TODO FILL"
        anchors.horizontalCenter: parent.horizontalCenter
        font.family: EmcGlobals.font2.name

        BorderImage {  // background image
            x: -parent.x
            width: emcBrowser.width
            height: parent.height + 35
            source: "pics/header.png"
            border { left: 31; right: 39; top: 2; bottom: 39 }
        }
    }

    /***  ListView  ***********************************************************/
    BrowserList {
        id: emcBrowserList

        anchors {
            top: emcBrowserHeader.bottom
            topMargin: 25
            bottom: parent.bottom
            left: parent.left
            right: parent.right
        }
    }

    /***  Hidden state  *******************************************************/
    states: State {
        name: "hidden"
        when: !emc_active
        PropertyChanges {
            target: emcBrowserList
            opacity: 0.0
        }
        PropertyChanges {
            target: emcBrowserHeader
            opacity: 0.0
        }
        PropertyChanges {
            target: emcBrowser
            focus: false
        }
    }

    transitions: [
        Transition {
            from: ""; to: "hidden";
            SequentialAnimation {
                NumberAnimation {
                    duration: 200
                    properties: "opacity"
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
                    properties: "opacity"
                }
            }
        }
    ]
}
