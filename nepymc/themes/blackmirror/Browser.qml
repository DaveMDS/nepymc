import QtQuick 2.11
import QtQuick.Controls 2.4
import "components/"
import "utils/"


FocusScope {
    id: emcBrowser

    property bool emc_active: false
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
