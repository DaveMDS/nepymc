import QtQuick 2.12
import QtQuick.Controls 2.12

ScrollView {

    property alias text: emcTextArea.text

//    clip: true

    ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
    ScrollBar.vertical.policy: ScrollBar.AlwaysOn
    TextArea {
        id: emcTextArea

        readOnly: true
        wrapMode: TextArea.Wrap
        textFormat: TextArea.RichText


        color: EmcGlobals.fontColor
        font.pixelSize: EmcGlobals.fontSize
        font.family: EmcGlobals.font1.name
//        DebugRect{color: "yellow"}
    }

}
