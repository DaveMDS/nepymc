import QtQuick 2.12
import QtQuick.Controls 2.12
import "../utils/"



ListView {

    spacing: 1
    clip: true

    delegate: EmcListItemDelegate { }

    ScrollBar.vertical: ScrollBar { }

    onCurrentIndexChanged: model.selection_changed(currentIndex)
}
