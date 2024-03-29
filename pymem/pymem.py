import ctypes, struct, sys
import pymem.process as process
from typing import List
from pymem.macho import Module

class Pymem:
  def __init__(self, process_name: str) -> None:
    assert sys.platform == "darwin", f"pymem-osx only supports MacOS (64-bit ARM), not {sys.platform}"
    self.process_name = process_name
    self.pid = process.get_pid_by_name(process_name)
    assert self.pid != -1, "Failed to find process"
    self.task = process.get_task(self.pid)

  def read_bytes(self, address: int, size: int) -> bytes:
    buffer = ctypes.create_string_buffer(size)
    bytes_read = process.read(self.task, ctypes.c_uint64(address), buffer, size)
    assert bytes_read == size, f"Failed to read buffer, only read {bytes_read} bytes out of {size} bytes"
    return buffer.raw

  def read_int32(self, address: int) -> int: return int.from_bytes(self.read_bytes(address, 4), "little")
  def read_int64(self, address: int) -> int: return int.from_bytes(self.read_bytes(address, 8), "little")
  def read_float(self, address: int) -> float: return struct.unpack('f', self.read_bytes(address, 4))[0]
  def read_double(self, address: int) -> float: return struct.unpack('d', self.read_bytes(address, 8))[0]
  def read_bool(self, address: int) -> bool: return struct.unpack('?', self.read_bytes(address, 1))[0]

  def write_bytes(self, address: int, buffer: bytes) -> None:
    buffer = ctypes.create_string_buffer(buffer)
    assert process.write(self.task, ctypes.c_uint64(address), buffer, len(buffer)), "Failed to write buffer"

  def write_int32(self, address: int, value: int) -> None: self.write_bytes(address, value.to_bytes(4, "little"))
  def write_int64(self, address: int, value: int) -> None: self.write_bytes(address, value.to_bytes(8, "little"))
  def write_float(self, address: int, value: float) -> None: self.write_bytes(address, struct.pack('f', value))
  def write_double(self, address: int, value: float) -> None: self.write_bytes(address, struct.pack('d', value))
  def write_bool(self, address: int, value: bool) -> None: self.write_bytes(address, struct.pack('?', value))

  def get_base_address(self) -> int: return process.get_base_address(self.task).value

  def get_modules(self, extended: bool = False) -> List[Module]:
    modules = process.get_modules(self.task)
    if extended: [x.add_sections(process.parse_macho(self.task, x.get_address())) for x in modules]
    return modules
