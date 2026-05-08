import numpy as np

from life.domain.rules import apply_rules
from life.domain.types import Grid

_U8 = np.uint8


def _shift_left(
    p: np.ndarray, last_bit: np.uint8, pad_mask: np.uint8
) -> np.ndarray:
    """Shift packed bits left by 1 column (toward index 0) with toroidal wrap."""
    carry = (np.roll(p, -1, axis=1) >> _U8(7)) & _U8(1)
    result = (p << _U8(1)) | carry
    msb0 = (p[:, 0] >> _U8(7)) & _U8(1)
    result[:, -1] = (result[:, -1] & ~(_U8(1) << last_bit)) | (msb0 << last_bit)
    result[:, -1] &= pad_mask
    return result


def _shift_right(
    p: np.ndarray, last_bit: np.uint8, pad_mask: np.uint8
) -> np.ndarray:
    """Shift packed bits right by 1 column (toward last index) with toroidal wrap."""
    carry = (np.roll(p, 1, axis=1) & _U8(1)) << _U8(7)
    result = (p >> _U8(1)) | carry
    last_cell_bit = (p[:, -1] >> last_bit) & _U8(1)
    result[:, 0] = (result[:, 0] & _U8(0x7F)) | (last_cell_bit << _U8(7))
    result[:, -1] &= pad_mask
    return result


def _csa(
    a: np.ndarray, b: np.ndarray, c: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Carry-save adder: returns (sum_bit, carry_bit) on packed uint8 planes."""
    return a ^ b ^ c, (a & b) | (b & c) | (a & c)


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
    packed = np.packbits(s, axis=1)  # shape (rows, bytes_per_row)

    # Mask to zero padding bits in the last byte
    pad_mask = _U8(0xFF ^ ((1 << pad_cols) - 1)) if pad_cols else _U8(0xFF)
    # Bit position within the last byte of the last real column (MSB=7 in packbits)
    last_bit = _U8(7 - (cols - 1) % 8)

    row_up = np.roll(packed, 1, axis=0)
    row_dn = np.roll(packed, -1, axis=0)

    neighbors = [
        _shift_left(row_up, last_bit, pad_mask),    # top-left
        row_up,                                      # top
        _shift_right(row_up, last_bit, pad_mask),   # top-right
        _shift_left(packed, last_bit, pad_mask),    # left
        _shift_right(packed, last_bit, pad_mask),   # right
        _shift_left(row_dn, last_bit, pad_mask),    # bottom-left
        row_dn,                                      # bottom
        _shift_right(row_dn, last_bit, pad_mask),   # bottom-right
    ]

    # Sum 8 single-bit planes into a 3-bit count using a carry-save adder tree.
    # After the tree: count = bit0 + 2*bit1 + 4*bit2 (all in packed form).
    zero = np.zeros_like(packed)
    s0, c0 = _csa(neighbors[0], neighbors[1], neighbors[2])
    s1, c1 = _csa(neighbors[3], neighbors[4], neighbors[5])
    s2, c2 = _csa(neighbors[6], neighbors[7], zero)
    bit0, carry_mid = _csa(s0, s1, s2)
    bit1_pre, carry_hi = _csa(c0, c1, c2)
    bit1, _ = _csa(bit1_pre, carry_mid, zero)
    bit2 = carry_hi

    def unpack(plane: np.ndarray) -> np.ndarray:
        return np.unpackbits(plane, axis=1)[:, :cols].astype(np.int8)

    neighbor_count = unpack(bit0) + unpack(bit1) * 2 + unpack(bit2) * 4
    return apply_rules(neighbor_count, unpack(packed))
