import QtQuick
import QtQuick.Controls

ScrollView {

    property alias text: emcTextArea.text

//    clip: true

    function scrollUp() {
        ScrollBar.vertical.decrease()
    }
    function scrollDown() {
        ScrollBar.vertical.increase()
    }

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
