import QtQuick 2.12
import "../utils/"

Item {
    id: root

    property string emcUrl

    onEmcUrlChanged: {
        emcSpecialText.text = ''
        if (!emcUrl) {
            emcImage.source = ''
        } else if (emcUrl.startsWith('icon/')) {
            emcImage.source = '../pics/' + emcUrl + '.png'
        } else if (emcUrl.startsWith('image/')) {
            emcImage.source = '../pics/' + emcUrl
        } else if (emcUrl.startsWith('special/folder/')) {
            emcImage.source = '../pics/image/folder_vert.png'
            emcSpecialText.perc_top = 5
            emcSpecialText.perc_bottom = 5
            emcSpecialText.perc_left = 3
            emcSpecialText.perc_right = 11
            emcSpecialText.text = emcUrl.substring(15)
        } else if (emcUrl.startsWith('special/bd/')) {
            emcImage.source = '../pics/image/bd_cover_blank.png'
            emcSpecialText.perc_top = 8
            emcSpecialText.perc_bottom = 6
            emcSpecialText.perc_left = 2
            emcSpecialText.perc_right = 3
            emcSpecialText.text = emcUrl.substring(11)
        } else if (emcUrl.startsWith('special/cd/')) {
            emcImage.source = '../pics/image/cd_cover_blank.png'
            emcSpecialText.perc_top = 1
            emcSpecialText.perc_bottom = 1
            emcSpecialText.perc_left = 10
            emcSpecialText.perc_right = 1
            emcSpecialText.text = emcUrl.substring(11)
        } else {
            emcImage.source = emcUrl
        }
    }

    Image {
        id: emcImage

        anchors.fill: root
        fillMode: Image.PreserveAspectFit
//        sourceSize.width: 1024   // TODO this is an intresting optimization
//        sourceSize.height: 1024
        mipmap: true  // This gives better result but it's heavy :/

        onStatusChanged: {
            if (status == Image.Error) {
                emcSpinner.visible = false
                emcSpecialText.text = ''
                source = '../pics/error.png'
            } else if (status == Image.Loading) {
                emcSpinner.visible = true
                emcSpecialText.text = ''
            } else if (status == Image.Ready) {
                emcSpinner.visible = false
            }
        }
    }

    EmcText {
        id: emcSpecialText

        property int perc_top: 0
        property int perc_bottom: 0
        property int perc_left: 0
        property int perc_right: 0

        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
        wrapMode: Text.Wrap
        textFormat: Text.StyledText  // TODO StyledText or RichText ??
        color: "black"
        text: ''
        visible: text

        anchors {
            fill: parent
            topMargin: ((emcImage.height - emcImage.paintedHeight) / 2) +
                       (emcImage.paintedHeight / 100) * perc_top
            bottomMargin: ((emcImage.height - emcImage.paintedHeight) / 2) +
                          (emcImage.paintedHeight / 100) * perc_bottom
            leftMargin: ((emcImage.width - emcImage.paintedWidth) / 2) +
                        (emcImage.paintedWidth / 100) * perc_left
            rightMargin: ((emcImage.width - emcImage.paintedWidth) / 2) +
                         (emcImage.paintedWidth / 100) * perc_right
        }
    }

    EmcSpinner {
        id: emcSpinner

        anchors.verticalCenter: root.verticalCenter
        anchors.horizontalCenter: root.horizontalCenter
        visible: false

        EmcProgressBar {  // TODO move this inside EmcSpinner ?
            value: emcImage.progress
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.bottom
        }
    }
}
