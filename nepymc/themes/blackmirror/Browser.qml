import QtQuick 2.11
import QtQuick.Controls 2.4
import "utils/"


FocusScope {
    anchors.fill: parent

    /***  Header  *************************************************************/
    BorderImage {  // background image
        id: emcHeader

        width: parent.width
        height: emcHeaderText.height + 35
        source: "pics/header.png"
        border { left: 31; right: 39; top: 2; bottom: 39 }
    }
    Text {  // header text
        id: emcHeaderText

        text: "TODO FILL"
        anchors.horizontalCenter: parent.horizontalCenter
//        color: Globals.font_color_topbar
        font.family: EmcGlobals.font3.name
//        font.pixelSize: Globals.font_size_bigger
        style: Text.Raised
//        styleColor: Globals.font_color_shadow
    }

    /***  ListView  ***********************************************************/
    BrowserList {
        anchors {
            top: emcHeader.bottom
            bottom: parent.bottom
            left: parent.left
            right: parent.right
            rightMargin: parent.width / 2
        }

    }
}