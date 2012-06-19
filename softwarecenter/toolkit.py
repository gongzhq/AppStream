import sys

class UIToolkits:
    GTK2 = 0
    GTK3 = 1
    QML = 2
    FALLBACK = GTK3


if 'software-center' in sys.argv[0]:
    CURRENT_TOOLKIT = UIToolkits.GTK3
elif 'software-center-gtk2' in sys.argv[0]:
    CURRENT_TOOLKIT = UIToolkits.GTK2
elif 'software-center-qml' in sys.argv[0]:
    CURRENT_TOOLKIT = UIToolkits.QML
else:
    CURRENT_TOOLKIT = UIToolkits.FALLBACK
