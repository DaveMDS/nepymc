import QtQuick 2.11
import QtQuick.Controls 2.0


ApplicationWindow {
   id: main_window
   minimumWidth: 960
   minimumHeight: 600
   visible: true
   title: 'NepyMC'

   Image {
      id: background
      anchors.fill: parent
      source: 'pics/background.jpg'
      fillMode: Image.PreserveAspectCrop
   }

   //Rectangle {
      //width: parent.width
      //height: 30
      //color: 'green'

      //Text {
         //text: 'Hello World'
         //anchors.centerIn: parent
      //}
   //}

   MainMenu {
      focus: true
   }

}
