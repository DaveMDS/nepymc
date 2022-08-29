import QtQuick
import "../utils/"
import "../components/"

/*
 *  A standard emc list item, with only one big image, model fields used:
 *   -icon
 *
 *  Can be used in both vertical and horizontal views
 */

Item {
    id: root

    width: view.orientation === ListView.Vertical ? view.width : 300
    height: view.orientation === ListView.Vertical ? 300 : view.height

    BorderImage {  // selection highlight background
        anchors.fill: parent
        source: "../pics/imagelist_sel_bg.png"
        border { left: 3; right: 3; top: 4; bottom: 5 }
        visible: view.currentIndex === model.index
    }

    EmcImage {  // content image
        id: emcImage

        emcUrl: model.icon
        anchors.fill: parent
        anchors.margins: 10
    }

    BorderImage {  // selection highlight foreground
        anchors.fill: parent
        source: "../pics/imagelist_sel_fg.png"
        border { left: 6; right: 6; top: 6; bottom: 0 }
        visible: view.currentIndex === model.index
    }

    MouseArea {
        anchors.fill: parent
        onClicked: {
            view.currentIndex = index
        }
        onDoubleClicked: {
            view.model.item_activated(index)
        }
    }

}
