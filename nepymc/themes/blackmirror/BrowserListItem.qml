import QtQuick 2.11
import QtQuick.Controls 2.4
import "."
import "utils/"


Item {
    width: parent.width
//    height: childrenRect.height
    height: 42

    DebugRect {}


    EmcText {
        text: model.label
        anchors.verticalCenter: parent.verticalCenter
    }


}

