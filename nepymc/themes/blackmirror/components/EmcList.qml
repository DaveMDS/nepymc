import QtQuick
import QtQuick.Controls
import "../utils/"


ListView {
    id: root

    property string delegate_name: "EmcListItemDelegate.qml"

    clip: true

    delegate: Component {
        Loader {
            property var view: root  // expose the view to the delegate
            source: delegate_name
        }
    }

    ScrollBar.vertical: ScrollBar { }

    onCurrentIndexChanged: model.selection_changed(currentIndex)
}
