import QtQuick 2.11
import QtQuick.Controls 2.0


ApplicationWindow {

    minimumWidth: 960
    minimumHeight: 600
    visible: true
    title: "Emotion Media Center"

    Image {
        anchors.fill: parent
        source: "pics/background.jpg"
        fillMode: Image.PreserveAspectCrop
    }


    Browser {
//        focus: true
    }

    MainMenu {
        focus: true
    }



}
