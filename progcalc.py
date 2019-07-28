from guizero import App, TextBox, Text, Combo, Waffle, Box, PushButton

class ProcCalc:
    def __init__(self):
        self.bin_sep = 8
        self.value = 0

        self.app = App(layout="grid")
        self.top_box = Box(self.app, layout = "grid", grid = [0, 0])
        self.bottom_box = Box(self.app, layout = "grid", grid = [0, 1])
        self.right_box = Box(self.app, layout = "grid", grid = [1, 0, 1, 2])

        # Create the text field to enter data
        self.input = TextBox(self.top_box, width=25, grid=[0,0,2,1], command=self.process_input)
        self.input.bg = "white"
        self.input.text_size = 16

        # Display the hex value
        self.out_hex = Text(self.top_box, grid=[0,1,2,1], text="0x<waiting for valid input>")

        # Display the binary value
        self.out_bin = Text(self.top_box, grid=[1, 2], text="0b<waiting for valid input>")

        # Display the binary value separation switch
        self.in_binsep = Combo(self.top_box, grid=[0, 2], options=["4", "8", "16", "32"], command=self.process_binsep, selected="8")

        # Prepare the waffle list
        self.waffles = []


        self.input.focus()
        self.app.display()

    def process_input(self, inp):
        try:
            self.value = int(self.input.value, 0)

            self.display_bin()
            self.display_hex()
            self.display_waffle()
        except ValueError:
            return

    def process_binsep(self, opt):
        self.bin_sep = int(opt)
        self.display_bin()

    def process_waffle(self, event_data):
        # Not sure if this is the best way, but it works
        waffleno = int(event_data.y / (event_data.widget.pixel_size + event_data.widget.pad))
        waffleno = event_data.widget.height - (waffleno + 1)

        # Get WafflePixel based on calculation above - reversed to take into account multiple waffles
        idx = 0
        for w in reversed(self.waffles):
            if event_data.widget == w:
                break
            idx += 1

        # See what bit needs to be changed
        bit = self.bin_sep * idx + waffleno
        if self.value & (1 << bit):
            self.value &= ~(1 << bit)
        else:
            self.value |= (1 << bit)
        # Refresh display
        self.display_bin()
        self.display_hex()
        self.display_waffle()

    def display_hex(self):
        self.out_hex.value = hex(self.value)

    def display_bin(self):
        # Get binary without 0b
        outstring = bin(self.value)[2:]
        n = len(outstring)

        # Add zeros at beginning if needed
        while n % self.bin_sep != 0:
            outstring = "0" + outstring
            n += 1

        # Split in groups of bin_sep
        idx = self.bin_sep
        while idx <= n:
            outstring = outstring[0:idx] + " " + outstring[idx:]
            idx += self.bin_sep + 1

        self.out_bin.value = outstring

    def display_waffle(self):
        # Clear previous waffles in case the number changes
        for w in self.waffles:
            w.hide()
            del w
        del self.waffles
        self.waffles = []

        # Display new ones, based on the binary representation of the number
        x_coord = 0
        for elem in self.out_bin.value.split(" "):
            # Somehow it gets a empty element, fix this
            if elem == "":
                break

            w = Waffle(self.bottom_box, height=len(elem), width= 1, grid = [x_coord, 3])
            w.when_clicked = self.process_waffle
            x_coord += 1

            # Set the individual pixels
            for i in range(0, len(elem)):
                wp = w.pixel(0, i)
                if elem[i] == "1":
                    wp.color = "blue"

            self.waffles.append(w)


if __name__ == "__main__":
    pc = ProcCalc()
