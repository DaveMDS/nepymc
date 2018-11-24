import QtQuick 2.11
import QtQuick.Controls 2.4
import "."


FocusScope {
    anchors.fill: parent


    /***  Header  **************************************************************/
    BorderImage {  // background image
        width: parent.width
        height: header_text.height + 35
        source: 'pics/header.png'
        border.left: 31
        border.right: 39
        border.top: 2
        border.bottom: 39
    }
    Text {  // header text
        id: header_text
        text: 'Emotion Media Center'
        anchors.horizontalCenter: parent.horizontalCenter
        color: Globals.font_color_topbar
        font.family: Globals.font3.name
        font.pixelSize: Globals.font_size_bigger // TODO pixel? or points
        style: Text.Raised
        styleColor: Globals.font_color_shadow
    }


    /***  Clock  ***************************************************************/
    Item {
        id: clock
        anchors.fill: parent

        Text {  // date
            id: clock_date
            text: 'test 4 gennaio'
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.margins: 12
            color: Globals.font_color_topbar
            font.family: Globals.font3.name
            font.pixelSize: Globals.font_size_big
            style: Text.Raised
            styleColor: Globals.font_color_shadow
        }

        Text {  // hour
            id: clock_time
            text: '19:54'
            anchors.left: parent.left
            anchors.bottom: clock_date.top
            anchors.leftMargin: 12
            color: Globals.font_color_topbar
            font.family: Globals.font3.name
            font.pixelSize: Globals.font_size_bigger
            style: Text.Raised
            styleColor: Globals.font_color_shadow
        }

        function timeChanged() {
            var now = new Date
            //console.log(now)
            clock_time.text = now.toLocaleTimeString(Globals.locale, Locale.ShortFormat)
            clock_date.text = now.toLocaleDateString(Globals.locale, Locale.LongFormat)
        }

        Timer {
            interval: 1000
            running: true
            repeat: true
            triggeredOnStart: true
            onTriggered: clock.timeChanged()
        }
    }


    /***  List  ****************************************************************/
    BorderImage {
        id: list_bg
        width: parent.width
        height: 128
        y: header_text.height + 100
        source: 'pics/mainmenu_bg.png'
        border.bottom: 13
        border.top: 7
        opacity: 0.7

        Image {
            source: 'pics/shine_large.png'
            anchors.top: parent.top
            anchors.topMargin: 4
            anchors.horizontalCenter: parent.horizontalCenter
            opacity: 1.0
        }
    }

    ListView {
        anchors.fill: list_bg
        anchors.leftMargin: 100
        anchors.rightMargin: 100
        orientation: ListView.Horizontal
        focus: true
        clip: false

        displayMarginBeginning: 9999   // TODO   wtf ??
        displayMarginEnd: 9999



        //model: ListModel {
            //ListElement { label: "UI tests"; icon: 'star' }
            //ListElement { label: "Optical Discs"; icon: 'optical' }
            //ListElement { label: "Musica"; icon: 'music' }
            //ListElement { label: "Film"; icon: 'movie' }
            //ListElement { label: "Serie TV"; icon: 'tv' }
            //ListElement { label: "Canali Online"; icon: 'olvideo' }
            //ListElement { label: "Photo"; icon: 'photo' }
            //ListElement { label: "Settings"; icon: 'config' }
            //ListElement { label: "Quit"; icon: 'exit' }
        //}
        model: MainMenuModel // this is managed from python (label, icon)



        //Rectangle {
            //color: "red"
            //opacity: 0.3
            //anchors.fill: parent
        //}


        delegate: FocusScope { // MainMenu items
            //width: childrenRect.width
            //height: childrenRect.height
            width: 128
            height: 128
            focus: true

            Keys.onReturnPressed: console.log(model.label) // TODO REMOVE ME
         
            Rectangle {
                id: positioner
                width: 128
                height: 128
                visible: false
            }
            Image {
                source: model.icon ? 'pics/icon_'+model.icon+'.png' : ''
                fillMode: Image.PreserveAspectFit
                mipmap: true
                anchors.fill: positioner
                anchors.margins: parent.activeFocus ? 0 : 16
                Behavior on anchors.margins {
                    NumberAnimation { duration: 200 }
                }
            }
            Text {
                text: model.label
                anchors.bottom: positioner.top
                anchors.left: positioner.left
                anchors.right: positioner.right
            
            
                horizontalAlignment: Text.AlignHCenter
                color: Globals.font_color
                font.family: Globals.font3.name
                style: Text.Outline
                styleColor: Globals.font_color_shadow

                font.pixelSize: parent.activeFocus ? Globals.font_size_bigger :  Globals.font_size_bigger / 2
                Behavior on font.pixelSize {
                    NumberAnimation { duration: 200 }
                }
                opacity: parent.activeFocus ? 1.0 : 0.0
                Behavior on opacity {
                    NumberAnimation { duration: 200 }
                }
            }
        }
    }


}
