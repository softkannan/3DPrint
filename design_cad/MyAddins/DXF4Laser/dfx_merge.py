# -*- coding: utf-8 -*-
"""
Deals with merging DXF files putting each source file onto its own layer.

Created on Sun Sep 25 15:40:31 2016

@author: Ross Korsky

http://images.autodesk.com/adsk/files/autocad_2012_pdf_dxf-reference_enu.pdf
"""
import numbers


def from_hex(value):
  return int(value, 16)


def to_hex(value):
  return format(value, 'X')


class DxfScanner(object):

  def __init__(self, code_lines, start_line_no=0):
    self._code_lines = code_lines
    self._start_line_no = start_line_no
    self._marker = 0
    self._at = 0
    self._limit = len(code_lines)
    self.tag_id = None
    self.value = ''
    assert self._code_lines is not None

  def mark(self):
    self._marker = self._at

  def clear_marker(self):
    self._marker = 0

  def reset(self):
    self._at = 0
    self.clear_marker()

  def backup(self):
    self._at -= 2
    if self._at < 0:
      self._at = 0

  @property
  def dxf_code(self):
    return self._code_lines

  @property
  def line_no(self):
    return self._start_line_no + self._at

  def read(self, expect_tag=None, expect_value=None):
    """Produces the next tag (tag id, tag value string) in the sequence."""
    if self._limit - self._at < 2:
      self.tag_id = None
      self.value = None
      return False
    r = (self._code_lines[self._at], self._code_lines[self._at + 1])

    self._at += 2
    try:
      self.tag_id = int(r[0])
    except ValueError:
      self.tag_id = None
      self.value = None
      return False
    self.value = r[1]
    assert expect_tag is None or self.tag_id == expect_tag, 'Unexpected tag encountered on line ' + str(self.line_no)
    assert expect_value is None or self.value == expect_value, 'Unexpected value encountered on line ' + str(self.line_no)
    return True

  def read_hex(self, expect_tag=None, expect_value=None):
    if expect_value and isinstance(expect_value, numbers.Number):
      expect_value = to_hex(expect_value)

    ret = self.read(expect_tag, expect_value)
    if ret:
      self.value = int(self.value, 16)
    return ret

  def overwrite_current(self, tag_id, value):
    assert self._at >= 2
    self.dxf_code[self._at - 2] = str(tag_id)
    self.dxf_code[self._at - 1] = str(value)

  def slice_from_marker(self):
    return DxfScanner(self._code_lines[self._marker:self._at], self._start_line_no + self._marker)

class DxfVariable(object):
  def __init__(self, name=None, table=None):
    self.name = name
    self._table = table or dict()

  def get(self, tag_id):
    return self._table[tag_id]

  def set(self, tag_id, value):
    self._table[tag_id] = value

  @property
  def value(self):
    k = self._table.keys()
    assert len(k) == 1
    return self._table[k[0]]

  @value.setter
  def value(self, v):
    k = self._table.keys()
    assert len(k) == 1
    self._table[k[0]] = v

  @property
  def x(self):
    return float(self._table['10'])

  @x.setter
  def x(self, x):
    self._table['10'] = x

  @property
  def y(self):
    return float(self._table['20'])

  @y.setter
  def y(self, y):
    self._table['20'] = y

  @property
  def z(self):
    return float(self._table['30'])

  @z.setter
  def z(self, z):
    self._table['30'] = z

class DxfCodeWriter(object):
  def __init__(self, code_lines=None):
    self.code_lines = code_lines if code_lines is not None else []

  def append(self, tag_id, value):
    self.code_lines.append(str(tag_id))
    self.code_lines.append(str(value))

  def append_hex(self, tag_id, value):
    self.code_lines.append(str(tag_id))
    self.code_lines.append(to_hex(value))

  def write_raw(self, code_lines):
    self.code_lines.extend(code_lines)


class DxfSection(object):
  """ABSTRACT base class for SECTION entries."""
  def __init__(self, group_code):
    assert group_code, 'Group Code required for any DXF section instance'
    self.__group_code = group_code
    pass

  @property
  def group_code(self):
    return self.__group_code

  def _write_dxf_code_preamble(self, writer):
    writer.append(0, 'SECTION')
    writer.append(2, self.group_code)

  def _write_dxf_code_postamble(self, writer):
    writer.append(0, 'ENDSEC')


class RawSection(DxfSection):

  def __init__(self, group_code, dxf_code):
    super().__init__(group_code)
    assert dxf_code is not None
    self._dxf_code = dxf_code

  @property
  def dxf_code(self):
    return self._dxf_code

  def write_dxf_code(self, writer):
    self._write_dxf_code_preamble(writer)
    writer.write_raw(self._dxf_code)
    self._write_dxf_code_postamble(writer)

  @staticmethod
  def from_scanner(scanner):
    scanner.read()
    if scanner.tag_id == 0 and scanner.value == 'SECTION':
      scanner.read()
    assert scanner.tag_id == 2
    group_code = scanner.value
    scanner.mark()
    while scanner.read():
      if scanner.tag_id == 0 and scanner.value == 'ENDSEC':
        break
    assert scanner.tag_id == 0 and scanner.value == 'ENDSEC'
    scanner.backup()
    dxf_code = scanner.slice_from_marker().dxf_code
    r = RawSection(group_code, dxf_code)
    scanner.read()
    return r

class DxfTables(DxfSection):
  SECTION_NAME = 'TABLES'

  def __init__(self):
    super().__init__(DxfTables.SECTION_NAME)
    self.__tables = []
    self.__table_lookup = dict()

  def add(self, table):
    self.__tables.append(table)
    self.__table_lookup[table.group_code] = table

  def get_table(self, table_name):
    return self.__table_lookup[table_name]

  def write_dxf_code(self, writer):
    super()._write_dxf_code_preamble(writer)
    for table in self.__tables:
      table.write_dxf_code(writer)
    super()._write_dxf_code_postamble(writer)

  @staticmethod
  def from_scanner(scanner):
    scanner.mark()
    scanner.read()
    if scanner.tag_id == 0 and scanner.value == 'SECTION':
      scanner.read()
      scanner.mark()
    assert scanner.tag_id == 2
    assert scanner.value == DxfTables.SECTION_NAME
    tables = DxfTables()
    while scanner.read():
      if scanner.tag_id == 0 and scanner.value == 'ENDSEC':
        break
      assert scanner.tag_id == 0 and scanner.value == 'TABLE'
      scanner.read()
      assert scanner.tag_id == 2
      scanner.backup()
      if scanner.value == DxfLayers.GROUP_CODE:
        table = DxfLayers.from_scanner(scanner)
      else:
        table = RawTable.from_scanner(scanner)
      tables.add(table)

    assert scanner.tag_id == 0 and scanner.value == 'ENDSEC'
    return tables


class DxfTable(object):
  """ABSTRACT base class for TABLE entries."""

  def __init__(self, group_code, handle):
    """
    Args:
      self: self
      group_code: typicly one of APPID, DIMSTYLE, LAYER, LTYPE, STYLE, UCS, VIEW, VPORT, or BLOCK_RECORD
    """
    assert group_code, 'Group Code required for any DXF Table instance'
    assert handle is not None, 'Handle Required'
    self.__group_code = group_code
    self.__handle = handle

  @property
  def group_code(self):
    return self.__group_code

  @property
  def count(self):
    assert False, 'count not implemented!'

  @property
  def handle(self):
    return self.__handle

  def _write_dxf_code_preamble(self, writer):
    writer.append(0, 'TABLE')
    writer.append(2, self.group_code)
    writer.append_hex(5, self.handle)
    writer.append(100, 'AcDbSymbolTable')
    if self.count > 0:
      writer.append(70, self.count)

  def _write_dxf_code_postamble(self, writer):
    writer.append(0, 'ENDTAB')


class RawTable(DxfTable):
  def __init__(self, group_code, handle, dxf_code, entry_count):
    super().__init__(group_code, handle)
    assert dxf_code is not None
    assert entry_count is not None and entry_count >= 0
    self.__dxf_code = dxf_code
    self.__count = entry_count

  @property
  def count(self):
    return self.__count

  def write_dxf_code(self, writer):
    super()._write_dxf_code_preamble(writer)
    writer.write_raw(self.__dxf_code)
    super()._write_dxf_code_postamble(writer)

  @staticmethod
  def from_scanner(scanner):
    scanner.read()
    if scanner.tag_id == 0 and scanner.value == 'TABLE':
      scanner.read()
    assert scanner.tag_id == 2
    group_code = scanner.value
    scanner.read_hex()
    assert scanner.tag_id == 5 or (group_code == 'DIMSTYLE' and scanner.tag_id == 105)
    handle = scanner.value
    scanner.read(100, 'AcDbSymbolTable')
    scanner.read()
    if scanner.tag_id != 70:
      scanner.backup()

    scanner.mark()
    count = 0
    while scanner.read():
      if scanner.tag_id == 0:
        if scanner.value == 'ENDTAB':
          break
        if scanner.value == group_code:
          count += 1

    assert scanner.tag_id == 0 and scanner.value == 'ENDTAB'
    scanner.backup()
    dxf_code = scanner.slice_from_marker().dxf_code
    table = RawTable(group_code, handle, dxf_code, count)
    scanner.read()
    return table

class DxfLayers(DxfTable):
  GROUP_CODE = 'LAYER'

  def __init__(self, handle):
    super().__init__(DxfLayers.GROUP_CODE, handle)
    self.layers = []

  def add(self, layer):
    self.layers.append(layer)

  @property
  def count(self):
    return len(self.layers)

  def write_dxf_code(self, writer):
    super()._write_dxf_code_preamble(writer)
    for layer in self.layers:
      layer.write_dxf_code(writer)
    super()._write_dxf_code_postamble(writer)

  @staticmethod
  def from_scanner(scanner):
    scanner.mark()
    scanner.read()
    if scanner.tag_id == 0 and scanner.value == 'TABLE':
      scanner.read()
      scanner.mark()
    assert scanner.tag_id == 2
    assert scanner.value == DxfLayers.GROUP_CODE
    scanner.read_hex(5)
    handle = scanner.value
    scanner.read(100, 'AcDbSymbolTable')
    scanner.read()
    if scanner.tag_id != 70:
      scanner.backup()

    layers = DxfLayers(handle)
    while scanner.read(0):
      if scanner.value == 'ENDTAB':
        break
      assert scanner.value == DxfLayers.GROUP_CODE
      layers.add(DxfLayer.from_scanner(scanner))

    assert scanner.tag_id == 0 and scanner.value == 'ENDTAB'
    return layers


class DxfLayer(object):

  def __init__(self, name='0', color=0, handle=None, flags=0, linetype='CONTINUOUS'):
    self.name = name.upper()
    # NUMERIC 1-255! see: ftp://ftp.ecn.purdue.edu/jshan/86/help/html/import_export/dxf_colortable.htm
    # 0 - default
    # 1 - red
    # 2 - yellow
    # 3 - green
    # 4 - cyan
    # 5 - blue
    # 6 - magenta
    # 7 - white
    # 8 - gray
    # 255 - black
    # and apparently negative numbers mean the layer is turned off or something
    self.color = color
    self.handle = handle # Number, must be unique across all objects in the DXF file. Fusion360 appears to have 0x50+ (maybe as far as to 0xFF) allocated for layers
    self.flags = flags  # bit field - not really relavant for output from Fusion
    self.line_type = linetype # this string must either be 'CONTINUOUS' or a name defined in the LTYPE table
    pass

  def write_dxf_code(self, writer):
    assert self.handle is not None, 'handle required'
    writer.append(0, 'LAYER')
    writer.append_hex(5, self.handle)
    writer.append(100, 'AcDbSymbolTableRecord')
    writer.append(100, 'AcDbLayerTableRecord')
    writer.append(2, self.name.upper())
    writer.append(70, self.flags)
    if self.color != 0:
      writer.append(62, self.color)
    writer.append(6, self.line_type)

  @staticmethod
  def from_scanner(scanner):
    assert scanner.value == DxfLayers.GROUP_CODE
    scanner.read_hex(5)
    handle = scanner.value
    scanner.read(100, 'AcDbSymbolTableRecord')
    scanner.read(100, 'AcDbLayerTableRecord')
    d = dict()
    while scanner.read():
      if scanner.tag_id == 0:
        scanner.backup()
        break
      d[scanner.tag_id] = scanner.value

    return DxfLayer(d[2], d.get(62, 0), handle, flags=d.get(70, 0), linetype=d.get(6, 'CONTINUOUS'))

class DxfFile(object):
  def __init__(self):
    self.sections = []
    self.section_index = dict()

  def add_section(self, section):
    assert section
    self.sections.append(section)
    self.section_index[section.group_code] = section

  def set_section(self, section):
    assert section
    assert section.group_code in self.section_index
    self.section_index[section.group_code] = section
    for i, s in enumerate(self.sections):
      if s.group_code == section.group_code:
        self.sections[i] = section
        break

  def get_section(self, section_name):
    return self.section_index[section_name]

  def write_dxf_code(self, writer=None):
    if not writer: writer = DxfCodeWriter()
    for section in self.sections:
      section.write_dxf_code(writer)
    writer.append(0, 'EOF')
    return writer.code_lines

  def read_file(self, filename):
    self.sections = []
    self.section_index = dict()
    with open(filename, 'r') as f:
      dxf_code = [l.strip() for l in f.readlines()]
    assert dxf_code, 'Failed to read DXF file.'
    scanner = DxfScanner(dxf_code)
    self.__read_sections(scanner)

  def __read_sections(self, scanner):
    s = scanner
    while s.read() and not (s.tag_id == 0 and s.value == 'EOF'):
      assert s.tag_id == 0 and s.value == 'SECTION', 'Invalid DXF file - expected TAG(0) and SECTION group code.'
      s.read(2)
      section_name = s.value
      s.backup()
      if section_name == DxfTables.SECTION_NAME:
        self.add_section(DxfTables.from_scanner(s))
      else:
        self.add_section(RawSection.from_scanner(s))


class DxfEntitiesMerger(RawSection):
  SECTION_NAME = 'ENTITIES'

  def __init__(self):
    super().__init__(DxfEntitiesMerger.SECTION_NAME, [])
    self.__next_handle = 0x100
    self._writer = DxfCodeWriter(self._dxf_code)

  def merge_from(self, entities_raw_code, set_layer):
    s = DxfScanner( entities_raw_code )
    while s.read():
      if s.tag_id == 5:
        self._writer.append_hex(5, self.__next_handle)
        self.__next_handle += 1
      elif s.tag_id == 8:
        self._writer.append(8, set_layer)
      else:
        self._writer.append(s.tag_id, s.value)

class DxfFileMerger(object):
  def __init__(self):
    self.__file_specs = []

  def add_file(self, filename, layer_name, layer_color):
    assert layer_name
    assert layer_color in range(0, 256)
    self.__file_specs.append((filename, layer_name, layer_color))

  def save(self, filename):
    layers = []
    layers.append(DxfLayer('0', 0, 0x50))
    dxf_file = DxfFile()
    combined_entites = DxfEntitiesMerger()
    for (input_filename, layer_name, layer_color) in self.__file_specs:
      layer = DxfLayer(layer_name, layer_color, len(layers) + 0x50)
      layers.append(layer)
      dxf_file.read_file(input_filename)
      combined_entites.merge_from(dxf_file.section_index[DxfEntitiesMerger.SECTION_NAME].dxf_code, layer.name)

    dxf_file.set_section(combined_entites)
    layers_table = dxf_file.get_section(DxfTables.SECTION_NAME).get_table(DxfLayers.GROUP_CODE)
    layers_table.layers = layers

    dxf_code_lines = dxf_file.write_dxf_code()
    with open(filename, 'w') as f:
      for line in dxf_code_lines:
        print(line, file=f)