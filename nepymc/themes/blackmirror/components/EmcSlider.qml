import QtQuick 2.12
import QtQuick.Controls 2.12


Slider {  // video position slider
    id: root

    background: BorderImage {
        source: "../pics/slider_base_horiz.png"
        border { left: 3; right: 3 }

        width: root.availableWidth
        height: 5
        x: root.leftPadding
        y: root.topPadding + root.availableHeight / 2 - height / 2

        Image {
            source: "../pics/slider_run.png"
            y: 1
            height: 3
            width: root.visualPosition * parent.width
        }

    }

    handle: Image {
        source: "../pics/knob.png"
        width: 32; height: 32
        x: root.leftPadding + root.visualPosition * (root.availableWidth - width / 2) - width / 4
        y: root.topPadding + root.availableHeight / 2 - height / 2
    }

}
