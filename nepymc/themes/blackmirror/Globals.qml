pragma Singleton
import QtQuick 2.0

QtObject {

   // normal font used everywhere
   property FontLoader font1: FontLoader { source: "fonts/Cuprum.otf" }

   // font for titles, secondary text and good for numbers
   property FontLoader font2: FontLoader { source: "fonts/Oswald-Regular.ttf" }

   // font for the mainmenu
   property FontLoader font3: FontLoader { source: "fonts/Sansation-Regular.ttf" }


   // font colors
   property color font_color_topbar: "#C8FFFFFF"
   property color font_color: "#FFFFFFFF"
   property color font_color_shadow: "#40000000"

   // font sizes
   property int font_size_smaller: 14   // TODO pixel? or points
   property int font_size_small: 18
   property int font_size: 22
   property int font_size_big: 26
   property int font_size_bigger: 48


   // Current system locale
   property var locale: Qt.locale()

}
