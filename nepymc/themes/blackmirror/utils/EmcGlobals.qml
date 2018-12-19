pragma Singleton
import QtQuick 2.0

QtObject {

    // normal font used everywhere
    property FontLoader font1: FontLoader { source: "../fonts/Cuprum.otf" }

    // font for titles, secondary text and good for numbers
    property FontLoader font2: FontLoader { source: "../fonts/Oswald-Regular.ttf" }

    // font for the mainmenu
    property FontLoader font3: FontLoader { source: "../fonts/Sansation-Regular.ttf" }


    // font colors
    property color fontColor: "#FFFFFFFF"
    property color fontColorShadow: "#AA000000"
    property color fontColorDisable: "#FF969696"

    // font sizes     TODO pixel? or points
    property int fontSizeSmaller: 14
    property int fontSizeSmall: 18
    property int fontSize: 22
    property int fontSizeBig: 26
    property int fontSizeBigger: 48


    // Current system locale
    property var locale: Qt.locale()

}
