pragma Singleton
import QtQuick

Item {

    // normal font used everywhere
    property FontLoader font1: FontLoader { source: "../fonts/Cuprum.otf" }

    // font for titles, secondary text and good for numbers
    property FontLoader font2: FontLoader { source: "../fonts/Oswald-Regular.ttf" }

    // font for the mainmenu
    property FontLoader font3: FontLoader { source: "../fonts/Sansation-Regular.ttf" }

    // UI element colors
    property color widgetBgColor: "#FF404040" // solid gray

    // font colors
    property color fontColor: "#FFFFFFFF"
    property color fontColorShadow: "#AA000000"  // white
    property color fontColorDisable: "#FF969696"  // gray
    property color fontColorTopbar: "#C8FFFFFF"  // a bit trasparent white
    property color fontColorTopbarShadow: "#AA000000"  // half trasparent black
    property color fontColorTitle: "#FF3399FF"  // efl blue
    property color fontColorInverse: "#FF303030" // "quite black" gray

    // font sizes     TODO pixel? or points
    property int fontSizeSmaller: 14
    property int fontSizeSmall: 18
    property int fontSize: 22
    property int fontSizeBig: 26
    property int fontSizeBigger: 48


    // Current system locale
    property var locale: Qt.locale()

    // Current time and date
    property date now: new Date()
    property string time_short: "00:00"
    property string time_long: "00:00:00"
    property string date_long: "venerdì 3 gennaio 2018"

    Timer {
        interval: 1000; running: true; repeat: true
        triggeredOnStart: true
        onTriggered: {
            now = new Date()
            time_short = now.toLocaleTimeString(locale, Locale.ShortFormat)
            time_long = now.toLocaleTimeString(locale, Locale.LongFormat)
            date_long = now.toLocaleDateString(EmcGlobals.locale, Locale.LongFormat)
        }
    }
}
