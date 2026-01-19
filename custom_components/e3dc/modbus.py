import asyncio
import struct

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException


class E3DCModbusClient:
    def __init__(self, host, port=502, unit_id=1, register_offset=0):
        self._host = host
        self._port = port
        self._unit_id = unit_id
        self._register_offset = register_offset

        self._client = AsyncModbusTcpClient(
            host=self._host,
            port=self._port,
        )

        self._lock = asyncio.Lock()

    async def connect(self):
        if not self._client.protocol:
            await self._client.connect()

    async def close(self):
        if self._client.protocol:
            await self._client.close()

    # --------------------------------------------------
    # Low-level access
    # --------------------------------------------------

    async def read_holding_registers(self, address: int, count: int):
        async with self._lock:
            await self.connect()
            result = await self._client.read_holding_registers(
                address=address + self._register_offset - 1,
                count=count,
                slave=self._unit_id,
            )

        if result.isError():
            raise ModbusException(result)

        return result.registers

    async def write_register(self, address: int, value: int):
        async with self._lock:
            await self.connect()
            result = await self._client.write_register(
                address=address + self._register_offset - 1,
                value=value,
                slave=self._unit_id,
            )

        if result.isError():
            raise ModbusException(result)

    # --------------------------------------------------
    # Decoding helpers
    # --------------------------------------------------

    @staticmethod
    def decode_int32(registers):
        raw = struct.pack(">HH", registers[0], registers[1])
        return struct.unpack(">i", raw)[0]

    @staticmethod
    def decode_uint16(registers):
        return registers[0]

    # --------------------------------------------------
    # High-level helper
    # --------------------------------------------------

    async def read_value(self, regdef: dict):
        regs = await self.read_holding_registers(
            regdef["addr"],
            regdef["len"],
        )

        rtype = regdef["type"]

        if rtype == "int32":
            return self.decode_int32(regs)

        if rtype == "uint16":
            return self.decode_uint16(regs)

        raise ValueError(f"Unsupported register type: {rtype}")
