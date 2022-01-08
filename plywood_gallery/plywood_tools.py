from __future__ import print_function
from IPython.core.magic import (Magics, magics_class,
                                cell_magic)
import json
from pathlib import Path
from IPython.core import magic_arguments
from IPython.core.magic import register_cell_magic
import json
import time
from base64 import b64decode
from io import BytesIO, StringIO
from IPython import get_ipython
from IPython.core import magic_arguments
from IPython.core.magic import register_cell_magic
import PIL

def rmtree(f: Path):
    if f.is_file():
        f.unlink()
    else:
        for child in f.iterdir():
            rmtree(child)
        f.rmdir()


class ChapterManager:
    """Recives instructions from  capture_png_test"""
    cell_counter = 0
    chapter_name = ""
    path = Path.cwd() / "gallery_assets/" # cwd of folder where jupyter notebook is in
    json_path = Path.cwd() / "gallery_assets/gallery_parameters.json"
    @staticmethod
    def set_chapter_name(new_chapter):
        """Makes a new chapter"""
        ChapterManager.chapter_name =  new_chapter     

    @staticmethod
    def sort(chapter):
        """Sort chapters in a certain way"""
        raise NotImplementedError

    @staticmethod
    def clean(chapter):
        """clean only one specific chapter"""
        raise NotImplementedError

    @staticmethod
    def clean():
        path  = ChapterManager.path
        """Cleans the whole gallery_assets tree"""
        try:
            rmtree(path)
        except:
            pass
        path.mkdir(parents=False, exist_ok=False)
        # create json file
        joson_file_path = ChapterManager.json_path
        with open(joson_file_path, "w") as jsonFile:
            json.dump({}, jsonFile, indent=2)


@magics_class
class PlywoodGalleryMagic(Magics):
    """Sends instruction to ChapterManager like increment cell counter.
    Here comes the magic, syntax is like here:  https://ipython.readthedocs.io/en/stable/config/custommagics.html
    """
  #  @needs_local_scope
    @cell_magic
    @magic_arguments.magic_arguments()
    @magic_arguments.argument(
        "--path",
        "-p",
        default=None,
        help=("the path where the image will be saved to"),
    )
    @magic_arguments.argument(
        "--celltype",
        "-c",
        default="Normal",
        help=("Cell can be of type 'Normal', 'Header', and 'Dependend'"),
    )
    @magic_arguments.argument(
        "--style",
        "-s",
        default="",
        help=("Add extra css style for the gallery enteries"),
    )
    def capture_png_test(self, line, cell):
        """Saves the png image and the css style for the html page"""
        args = magic_arguments.parse_argstring(PlywoodGalleryMagic.capture_png_test, line)

        postpath = args.path
        chapter_name= ChapterManager.chapter_name
        joson_file_path =  ChapterManager.json_path
        chapter_name_underscore = chapter_name.replace(" ", "_")
        prepath = "gallery_assets"
        global cell_counter
        ChapterManager.cell_counter +=1
        path = f"{prepath}/{chapter_name_underscore}_{ChapterManager.cell_counter:03}_{postpath}"  # include chaptername

        #path = path.split(".png")[0] + str(time.time_ns()) + ".png"
        if not path:
            raise ValueError('No path found!')

        style = args.style
        style = style.strip('"')  # remove quotes

        styles = {
            'Normal': 'border: 3px solid #007AB8;',
            'Header': 'border: 3px solid #ED6A5A;',
            'Dependend': 'border: 3px solid #A8DCF0;'
        }
        try:
            default_style = styles[args.celltype]
        except KeyError:
            raise ValueError('Not a valid cell type!')

        style = default_style + style

        # print(args.path,args.celltype, args.style)

        # init capturing cell output
        get_ipython().run_cell_magic(
            'capture',
            ' --no-stderr --no-stdout result',
            cell
        )

        raw_code_block = cell
        code_block = ""

        for codeline in StringIO(raw_code_block):
            if "#NOT" in codeline:
                pass
            else:
                code_block += codeline

        new_codeblock = ""
        for codeline in StringIO(code_block):
            if "#ONLY" in codeline:
                codeline = codeline.replace("#ONLY", "")
                new_codeblock += codeline
            else:
                pass

        if new_codeblock:  # checks if there are lines that include "#ONLY"
            code_block = new_codeblock

        # make sure that javascript can read the single quote character
        code_block = code_block.replace("'", "&#39;")
        code_block = code_block.strip("\n")

        # read + update + write json
        with open(joson_file_path, "r") as jsonFile:
            data = json.load(jsonFile)

        if not chapter_name in data:
            data[chapter_name] = []

        chapter_content = data[chapter_name]
        chapter_content.append(
            [{"image_path": path,
            "celltype": args.celltype,
            "css":style,
            "code":code_block}])

        data[chapter_name] = chapter_content
        with open(joson_file_path, "w") as jsonFile:
            json.dump(data, jsonFile, indent=2, sort_keys=False)
        print(ChapterManager.chapter_name)
        # save image
        for output in result.outputs: #here broken
            display(output)
            data = output.data
            if 'image/png' in data:
                png_bytes = data['image/png']
                if isinstance(png_bytes, str):
                    png_bytes = b64decode(png_bytes)
                assert isinstance(png_bytes, bytes)
                bytes_io = BytesIO(png_bytes)
                image = PIL.Image.open(bytes_io)
                image.save(path, 'png')