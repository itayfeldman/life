import numpy as np

from life.domain.rules import apply_rules
from life.domain.types import Grid


def bitpack(state: Grid) -> Grid:
    """
    Next state via bitpacked uint8 rows with toroidal wrap.

    Rows are packed with np.packbits (MSB-first). Neighbor columns are
    obtained by byte-level bit-shifts with toroidal carry. The 8 neighbor
    planes are summed with a carry-save adder tree, keeping all arithmetic
    in packed form until the final np.unpackbits call.

    Examples
    --------
        >>> import numpy as np
        >>> state = np.array([[0, 1, 0], [0, 1, 0], [0, 1, 0]], dtype=np.int8)
        >>> bitpack(state)
        array([[0, 0, 0],
               [1, 1, 1],
               [0, 0, 0]], dtype=int8)
    """
    _, cols = state.shape

    pad_cols = (8 - cols % 8) % 8
    if pad_cols:
        s = np.pad(state, ((0, 0), (0, pad_cols)), constant_values=0).astype(np.uint8)
    else:
        s = state.astype(np.uint8)

    # packed[r, b]: MSB of byte b = leftmost cell of that byte's 8-column block
    packed = np.packbits(s, axis=1)   # shape (rows, bytes_per_row)

    # Mask to zero padding bits in the last byte (bits below the last real cell)
    pad_mask = np.uint8(0xFF ^ ((1 << pad_cols) - 1)) if pad_cols else np.uint8(0xFF)
    # Bit position within last byte of the last real column (MSB=7 in packbits)
    last_bit = np.uint8(7 - (cols - 1) % 8)

    def shift_left(p: np.ndarray) -> np.ndarray:
        """Shift bits left by 1 column (toward lower index) with toroidal wrap."""
        # Each byte shifts left; MSB of byte b+1 becomes LSB of byte b.
        carry = (np.roll(p, -1, axis=1) >> np.uint8(7)) & np.uint8(1)
        result = (p << np.uint8(1)) | carry
        # Toroidal: MSB of byte 0 (col 0) wraps to the last real column's bit.
        msb0 = (p[:, 0] >> np.uint8(7)) & np.uint8(1)
        result[:, -1] = (result[:, -1] & ~(np.uint8(1) << last_bit)) | (
            msb0 << last_bit
        )
        result[:, -1] &= pad_mask
        return result

    def shift_right(p: np.ndarray) -> np.ndarray:
        """Shift bits right by 1 column (toward higher index) with toroidal wrap."""
        # Each byte shifts right; LSB of byte b-1 becomes MSB of byte b.
        carry = (np.roll(p, 1, axis=1) & np.uint8(1)) << np.uint8(7)
        result = (p >> np.uint8(1)) | carry
        # Toroidal: last real column's bit wraps to MSB of byte 0 (col 0).
        last_cell_bit = (p[:, -1] >> last_bit) & np.uint8(1)
        result[:, 0] = (result[:, 0] & np.uint8(0x7F)) | (last_cell_bit << np.uint8(7))
        result[:, -1] &= pad_mask
        return result

    def csa(
        a: np.ndarray, b: np.ndarray, c: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        """Carry-save adder: (sum_bits, carry_bits) on packed uint8 planes."""
        return a ^ b ^ c, (a & b) | (b & c) | (a & c)

    row_up = np.roll(packed, 1, axis=0)
    row_dn = np.roll(packed, -1, axis=0)

    neighbors = [
        shift_left(row_up),    # top-left
        row_up,                # top
        shift_right(row_up),   # top-right
        shift_left(packed),    # left
        shift_right(packed),   # right
        shift_left(row_dn),    # bottom-left
        row_dn,                # bottom
        shift_right(row_dn),   # bottom-right
    ]

    # Sum 8 single-bit planes into a 4-bit count (max=8, fits in 4 bits)
    s0, c0 = csa(neighbors[0], neighbors[1], neighbors[2])
    s1, c1 = csa(neighbors[3], neighbors[4], neighbors[5])
    s2, c2 = csa(neighbors[6], neighbors[7], np.zeros_like(packed))
    bit0, tc0 = csa(s0, s1, s2)
    t1, tc1 = csa(c0, c1, c2)
    bit1, _ = csa(t1, tc0, np.zeros_like(packed))
    bit2 = tc1

    def unpack(plane: np.ndarray) -> np.ndarray:
        return np.unpackbits(plane, axis=1)[:, :cols].astype(np.int8)

    neighbor_count = unpack(bit0) + unpack(bit1) * 2 + unpack(bit2) * 4
    return apply_rules(neighbor_count, unpack(packed))
