import argparse
from guizero import App, TextBox, Text, Combo, Waffle, Box, ListBox
import openpyxl


class ProgCalc:
    def __init__(self, input_excel_db):
        self.bin_sep = 8
        self.value = 0
        self.bit_map = {}

        self.app = App(layout="grid")
        self.top_box = Box(self.app, layout = "grid", grid = [0, 0])
        self.bottom_box = Box(self.app, layout = "grid", grid = [0, 1])
        self.right_box = Box(self.app, grid = [1, 0, 1, 2])

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
        self.boxes = []

        # Read the worksheets in the input dictionary and create the list
        self.in_excel = openpyxl.load_workbook(filename = '/home/andreic/workspace/py_progcalc/mpc831x.xlsx', read_only=True)
        self.in_regs = self.in_excel.sheetnames
        self.in_regs.insert(0, "OFF")

        # Display the list of registers
        self.in_reglist = ListBox(self.right_box, items = self.in_regs, command=self.process_reglist)

        self.input.focus()
        self.app.display()

    def process_input(self, inp):
        try:
            self.value = int(self.input.value, 0)

            self.refresh_all()
        except ValueError:
            return

    def process_binsep(self, opt):
        self.bin_sep = int(opt)
        self.refresh_all()

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
        self.refresh_all()

    def process_reglist(self, selected):
        if selected == "OFF":
            self.bit_map = {}
            self.refresh_all()
            return

        tmp = self.in_excel[selected]
        self.bit_map = {}
        for row in tmp.iter_rows():
            try:
                bits = row[0].value
                if bits == None:
                    break
            except IndexError:
                break
            name = row[1].value
            descr = row[2].value

            try:
                bit = int(bits)
                self.bit_map[bit] = name
            except ValueError:
                if bits == "Bits":
                    continue
                else:
                    bits = str.replace(bits, "–", "-")
                    interval = bits.split("-")
                    for i in range(int(interval[0]), int(interval[1]) + 1):
                        self.bit_map[i] = name
        self.refresh_all()

    def refresh_all(self):
        if "0x" in self.input.value:
            self.input.value = hex(self.value)
        else:
            self.input.value = str(self.value)

        # TODO: improve?
        self.display_hex()
        self.display_bin()
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

        for b in self.boxes:
            b.hide()
            del b
        del self.boxes
        self.boxes = []

        # Display new ones, based on the binary representation of the number
        idx = 0
        x_coord = 0
        for elem in self.out_bin.value.split(" "):
            # Somehow it gets a empty element, fix this
            if elem == "":
                break

            w = Waffle(self.bottom_box, height=len(elem), width= 1, grid = [x_coord, 0])
            w.when_clicked = self.process_waffle
            if len(self.bit_map) != 0:
                b = Box(self.bottom_box, grid = [x_coord + 1, 0])
                self.boxes.append(b)
                tx = Text(b, grid = [x_coord + 1, 0], height="fill", width="fill", size=16, text="\n")

            # Set the individual pixel
            y_coord = 0
            for i in range(0, len(elem)):
                wp = w.pixel(0, i)
                if len(self.bit_map) != 0:
                    tx.value += self.bit_map[idx] + "\n"
                idx += 1
                if elem[i] == "1":
                    wp.color = "blue"

            x_coord += 2

            self.waffles.append(w)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Special calculator that interprets registers")
    parser.add_argument('excel_db', help='Path to an excel database file')

    args = parser.parse_args()

    pc = ProgCalc(args.excel_db)
