from collections import namedtuple
from bs4 import BeautifulSoup


class TKGridFromTable:
    """


    """

    def __init__(self, window_handle, html, window_title='Window Title'):

        self.window_name = window_handle
        self.html = html
        self.window_title = window_title
        self.table = self.__generateTuple__()

    def __generateTuple__(self):
        counter = 0
        # Create named tuples
        Cell = namedtuple('Cell', 'name column row columnspan rowspan image')
        GridTable = namedtuple('GridTable', 'name dimensions geometry cells')
        # Parse the html
        soup = BeautifulSoup(self.html, 'html.parser')
        table = soup.find("table")
        # Get the resolution of the table (If given, else a default of 640x480)
        if "width" in table.attrs:
            table_width = table['width']
        else:
            table_width = '640'
        if "height" in table.attrs:
            table_height = table['height']
        else:
            table_height = '480'
        geometry = table_width + "x" + table_height

        # Get the dimensions of the table
        rows = table.find_all('tr')
        dim_rows = len(rows)
        dim_columns = 0
        tds = rows[0].find_all('td')
        for cell in tds:
            if 'colspan' in cell.attrs:
                dim_columns = dim_columns + int(cell.attrs['colspan'])
            else:
                dim_columns += 1

        # Create table grid for checking which cells have already been filled
        column_fill = []
        for columnCount in range(0, dim_columns):
            column_fill.append(0)
        table_grid = []
        for c in range(dim_rows):
            table_grid.append(list(column_fill))
        # cells list for populating
        cells = []
        # names list for checking for duplicate names
        names = []
        for row in range(0, len(rows)):
            tds = rows[row].find_all('td')
            column = 0
            for html_cell in tds:
                # Finding out which column we have to work in by checking which
                # columns have already been filled with cells
                for c in range(dim_columns):
                    if table_grid[row][c] == 0:
                        column = c
                        break
                # Go through all the columns and get their properties and add those to
                # the cell named tuple
                if 'colspan' in html_cell.attrs:
                    columnspan = int(html_cell.attrs['colspan'])
                else:
                    columnspan = 1
                if 'rowspan' in html_cell.attrs:
                    rowspan = int(html_cell.attrs['rowspan'])
                else:
                    rowspan = 1
                images = html_cell.find_all('img')
                # if no image was found, generate cell name
                if len(images) == 0:
                    image_src = None
                    cell_name = "cell_column{}_row{}".format(column, row)
                else:
                    image_src = images[0]['src']
                    cell_name = (images[0]['src'].split("/")[-1]).split(".")[-2]
                    # Check for illegal characters in the name
                    illegal_chars = "'.-()[]{}!@|"
                    for char in illegal_chars:
                        cell_name = cell_name.replace(char, "_")
                # name has been taken from image filename or generated
                # since duplicate names are possible check if name already exists,
                # if so generate new name
                if cell_name in names:
                    i = 1
                    while True:
                        new_name = cell_name + str(i)
                        if new_name in names:
                            i += 1
                        else:
                            cell_name = new_name
                            break
                names.append(cell_name)
                cell = Cell(cell_name, column, row, columnspan, rowspan, image_src)
                cells.append(cell)
                # column_fill[column] += rowspan
                for c in range(column, column+columnspan):
                    for r in range(row, row+rowspan):
                        table_grid[r][c] = 1
                counter += 1
                column += columnspan

        full_table = GridTable(self.window_name, (dim_columns, dim_rows), geometry, cells)
        return full_table

    @property
    def generate_code(self):
        # create shortcur for window handle, since it comes back a lot
        win = self.table.name
        code = "# Generated code from TKGridFromTable \n" \
               "import tkinter\n" \
               "from PIL import ImageTk, Image\n" \
               "#initialising TKinter window.\n"
        code = code + win + " = tkinter.Toplevel()\n"
        code = code + "{}.title('{}')\n".format(self.window_name, self.window_title)
        code = code + "{}.geometry('{}')\n".format(self.window_name, self.table.geometry)

        code = code + "# now the cells of the table \n"
        for cell in self.table.cells:
            if cell.image:
                code = code + "{0.name}_image = ImageTk.PhotoImage(Image.open('{0.image}'))\n".format(cell)
                code = code + "{0.name} = tkinter.Label({1}, image={0.name}_image, " \
                              "borderwidth=0, highlightthickness=0)\n".format(cell, win)
            else:
                code = code + "{0.name} = tkinter.Label({1}, " \
                              "borderwidth=0, highlightthickness=0)\n".format(cell, win)
            code = code + "{0.name}.grid(column={0.column}, row={0.row}, " \
                          "columnspan={0.columnspan}, rowspan={0.rowspan}, sticky='nw')\n".format(cell)
        code = code + "{}.mainloop()".format(win)
        return code

    def test_table(self):
        # I know the use of exec is frowned upon, but that is mainly because a
        # user might be able to execute malignant code. Since it only executes
        # self generated code, that is less of an issue (Although it could pose a problem)
        # Also, this project is to generate code to use in other projects.

        exec(self.generate_code)


if __name__ == "__main__":
    filename = input("Please enter html filename: ")
    with open(filename, 'r') as htmlFile:
        htmlcode = htmlFile.read()
    gridTable = TKGridFromTable("test_grid", htmlcode, "Test Grid From file:" + filename)
    print(gridTable.generate_code)
    # Uncomment this if you want to show the tkinter window
    # gridTable.test_table()
