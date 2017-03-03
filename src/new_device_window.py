import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, GObject, Gtk, Pango

from usbguard_dbus import Rule, USBGuardDBUS


class USBGuardNewDeviceWindow(Gtk.ApplicationWindow):

    def __init__(self, app, device):
        Gtk.ApplicationWindow.__init__(self, title='New USB device', application=app)
        self.application = app
        self.device = device

        grid = Gtk.Grid(margin=10)

        title_label = Gtk.Label(margin=10, justify=Gtk.Justification.CENTER)
        title_label.set_markup("<big><b>New USB Device inserted</b></big>")
        grid.attach(title_label, 0, 0, 2, 1)

        type_text = "Device type:\n<b>{}</b>".format(GObject.markup_escape_text(self.device.get_class_description_string()))
        type_label = Gtk.Label(margin=10, justify=Gtk.Justification.CENTER)
        type_label.set_markup(type_text)
        grid.attach(type_label, 0, 1, 1, 1)

        name_text = "Device name:\n<b>{}</b>".format(GObject.markup_escape_text(self.device.name))
        name_label = Gtk.Label(margin=10, justify=Gtk.Justification.CENTER)
        name_label.set_markup(name_text)
        grid.attach(name_label, 1, 1, 1, 1)

        action_label = Gtk.Label("Status:", margin=10)
        grid.attach(action_label, 0, 2, 1, 1)

        switch = Gtk.Switch(margin=10)
        switch.set_active(self.device.is_allowed())
        switch.connect("notify::active", self.application.on_switch_activated)
        grid.attach(switch, 1, 2, 1, 1)

        self.add(grid)


class USBGuardNewDeviceWindowExpert(Gtk.ApplicationWindow):

    DEVICES_LIST_COLUMNS = [
        'number', 'rule', 'id', 'name', 'port', 'interface', 'description'
    ]

    def __init__(self, app, device):
        Gtk.ApplicationWindow.__init__(self, title='New USB device', application=app)
        self.application = app
        self.device = device

        devices_list_model = Gtk.ListStore(int, str, str, str, str, str, str)
        devices_list_model.append(device.as_list())

        view = Gtk.TreeView(model=devices_list_model)
        for i in range(len(self.DEVICES_LIST_COLUMNS)):
            cell = Gtk.CellRendererText()
            # the text in the first column should be in boldface
            if i == 0:
                cell.props.weight_set = True
                cell.props.weight = Pango.Weight.BOLD
            col = Gtk.TreeViewColumn(self.DEVICES_LIST_COLUMNS[i], cell, text=i)
            view.append_column(col)

        # the label we use to show the selection
        # self.label = Gtk.Label()
        # self.label.set_text("")

        grid = Gtk.Grid()
        grid.attach(view, 0, 0, 1, 1)
        # grid.attach(self.label, 0, 1, 1, 1)

        switch = Gtk.Switch()
        switch.set_active(self.device.is_allowed())
        switch.connect("notify::active", self.application.on_switch_activated)
        grid.attach(switch, 2, 0, 1, 1)

        self.add(grid)


class USBGuardNewDeviceApplication(Gtk.Application):

    def __init__(self, device, usbguard_dbus):
        Gtk.Application.__init__(self)
        self.device = device
        self.usbguard_dbus = usbguard_dbus
        self.window = None

    def do_activate(self):
        self.window = USBGuardNewDeviceWindow(self, self.device)
        self.window.show_all()

    def do_startup(self):
        Gtk.Application.do_startup(self)

        # create a menu
        menu = Gio.Menu()
        # append to the menu three options
        menu.append("Quit", "app.quit")
        # set the menu as menu of the application
        self.set_app_menu(menu)

        # option "quit"
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", self.quit_cb)
        self.add_action(quit_action)

    def quit_cb(self, action, parameter):
        print("You have quit.")
        self.quit()

    def on_switch_activated(self, switch, gparam):
        if switch.get_active():
            state = "on"
            rule = Rule.ALLOW
        else:
            state = "off"
            rule = Rule.BLOCK
        print("Switch was turned", state)
        self.usbguard_dbus.apply_device_policy(self.device.number, rule, False)


def main():
    import sys
    from device import Device
    device = Device.generate_device([5, 'allow id 1d6b:0002 serial "0000:00:14.0" name "xHCI Host Controller" hash "Miigb8mx72Z0q6L+YMai0mDZSlYC8qiSMctoUjByF2o=" parent-hash "G1ehGQdrl3dJ9HvW9w2HdC//pk87pKzFE1WY25bq8k4=" via-port "usb1" with-interface 09:00:00'])
    usbguard_dbus = USBGuardDBUS()
    app = USBGuardNewDeviceApplication(device, usbguard_dbus)
    exit_status = app.run()
    sys.exit(exit_status)

if __name__ == "__main__":
    main()
