import QtQuick
import QtQuick.Controls
import "components/"
import "utils/"


EmcFocusManager {
    id: emcBrowser
    objectName: 'Browser'

    property string page_title: "page title"
    property string page_icon: "icon/home"

    property alias currentIndex: emcBrowserList.currentIndex

    anchors.fill: parent

    /***  TopBar  *************************************************************/
    EmcTopbar {
        id: emcBrowserHeader
        title: page_title
        icon: page_icon
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
        when: !focus
        PropertyChanges {
            target: emcBrowserList
            opacity: 0.0
        }
        PropertyChanges {
            target: emcBrowserHeader
            opacity: 0.0
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
