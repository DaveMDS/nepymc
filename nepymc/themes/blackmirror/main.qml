import QtQuick 2.11
import QtQuick.Controls 2.0


ApplicationWindow {

    minimumWidth: 960
    minimumHeight: 600
    visible: true
    title: EmcBackend.application_name()

    Image {
        anchors.fill: parent
        source: "pics/background.jpg"
        //source: "pics/TESTBG.jpg"
        fillMode: Image.PreserveAspectCrop
    }

    /* theme API TODOC */
    function activate_section(section) {
        console.log("activate_section: " + section)
        if (section === "browser") {
//            emc_browser.show()
//            emc_mainmenu.hide()
            emc_browser.emc_active = true
            emc_browser.focus = true
            emc_mainmenu.emc_active = false
        }
    }

    Component.onCompleted: {
        emc_mainmenu.emc_active = true
        emc_mainmenu.focus = true
//        emc_browser.emc_active = true
//        emc_browser.focus = true
    }

    Browser {
        id: emc_browser
//        focus: true
    }

    MainMenu {
        id: emc_mainmenu
//        focus: true
    }



}
