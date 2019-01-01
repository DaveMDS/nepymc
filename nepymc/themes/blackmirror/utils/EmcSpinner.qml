import QtQuick 2.12

Image {
    id: root

    source: "../pics/knob.png"

    Image {
        id: emcGlow
        z: -1

        source: "../pics/knob_glow.png"
        RotationAnimator {
            target: emcGlow
            from: 0
            to: 360
            duration: 1000
            running: root.visible
            loops: Animation.Infinite
        }
    }
}
