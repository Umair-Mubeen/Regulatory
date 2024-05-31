import argparse
import sys
import xml.etree.ElementTree as ET


def main():
    parser = FIXParser()
    parser.build_row_separator()
    parser.build_msg_separator()
    parser.init_fields()
    parser.parse_input_file()


class FIXParser:
    tag_column_length = 5
    field_name_column_length = 23
    trailing_column_length = 65
    msg_separator_length = 100

    def __init__(self):
        self.args = None
        self.fields = None
        self.msg_separator = None
        self.row_separator = None
        try:
            print("constructor...................")
            parser = argparse.ArgumentParser(description=(
                "Parse FIX messages from a text file against a Data Dictionary and output them with field names and "
                "enum information."))
            parser.add_argument("--hide_enums", action="store_true",
                                help="lists all possible enums in a row if field is of type enum.")
            parser.add_argument("--row_lines", action="store_true",
                                help="separates each row with lines for visual clarity.")

        except Exception as e:
            print("Argument Parser Exception :- " + str(e))

    def build_row_separator(self):
        try:
            print("row_separator...............")
            self.row_separator = ""
            for i in range(self.tag_column_length):
                self.row_separator += "-"
            self.row_separator += "-+-"
            for i in range(self.field_name_column_length):
                self.row_separator += "-"
            self.row_separator += "-+-"
            for i in range(self.trailing_column_length):
                self.row_separator += "-"
            self.row_separator += "\n"
        except Exception as e:
            print("Build_row_separator Exception :- " + str(e))

    def build_msg_separator(self):
        try:
            print("msg_separator...............")
            self.msg_separator = ""
            for i in range(self.msg_separator_length):
                self.msg_separator += "."  # after executing the fix parse it will print the . on the same row
            self.msg_separator += "\n"
        except Exception as e:
            print("build_msg_separator Exception :- " + str(e))

    def init_fields(self):
        try:
            print("init_fields....................")
            tree = ET.parse('FIX44.xml')
            root = tree.getroot()

            for child in root:
                if child.tag == "fields":
                    self.fields = child
        except Exception as e:
            print("init_fields Exception :- " + str(e))

    def get_enum_str(self, tag_number, tag_value):
        try:
            print("get_enum_str ...............")
            enums = ""
            field = self.fields.find(f"./field[@number='{tag_number}']")
            firstVal = field.find("./value")
            if not firstVal is None:
                meaning = field.find(f"./value[@enum='{tag_value}']")
                if not meaning is None:
                    enums += " (" + meaning.get("description") + ")"
                else:
                    enums += " (ERROR: NO MATCHING ENUM. CHECK DICTIONARY)"

            if field:
                enum_padding = self.trailing_column_length - len(enums)
                for i in range(enum_padding):
                    enums += " "
                for enum in field:
                    enums += enum.get("enum") + " : " + enum.get("description") + ", "

            return enums
        except Exception as e:
            print("get_enum_str Exception :- " + str(e))

    def make_readable(self, tags, output_file):
        try:
            print("enter into make_readable................")
            output_file.write(self.row_separator)
            for tag in tags:
                pair = tag.split("=")
                if len(pair) == 1:
                    continue

                tag_number = pair[0]
                tag_name = self.fields.find(f"./field[@number='{tag_number}']").get("name")
                tag_value = pair[1]

                padding1_len = self.tag_column_length - len(tag_number)
                padding1 = ""
                if padding1_len > 0:
                    for i in range(padding1_len):
                        padding1 = padding1 + " "

                padding2_len = self.field_name_column_length - len(tag_name)
                padding2 = ""
                if padding2_len > 0:
                    for i in range(padding2_len):
                        padding2 = padding2 + " "

                enums = ""
                enums = self.get_enum_str(tag_number, tag_value)

                line = tag_number + padding1 + " | " + tag_name + padding2 + " | " + tag_value + enums + "\n"  # write data into file
                output_file.write(line)
                output_file.write(self.row_separator)
        except Exception as e:
            print("tag number {} readable Exception :- ".format(tag_number) + str(e))

    def parse_input_file(self):
        try:
            input_file = open('Fix_Messages.txt', "r")
            line = input_file.readline()
            output_file = open('output.txt', "w")
            while line:
                line = line.strip()
                if line == "" or line[0] == "#":
                    line = input_file.readline()
                    continue
                tags = line.split("|")  #  |  make list of tags using the delimiter |
                self.make_readable(tags, output_file)
                output_file.write(self.msg_separator)
                line = input_file.readline()

            output_file.close()
        except Exception as e:
            print("parse_input_file Exception :- " + str(tags))
