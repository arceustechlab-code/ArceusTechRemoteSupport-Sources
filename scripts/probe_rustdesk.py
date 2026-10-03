"""Non-registering RustDesk TCP/UDP protocol probes for the existing VPS.

Wire fields and TCP framing match the pinned hbb_common rendezvous.proto and
BytesCodec. The UDP request has a deliberately short invalid ID: hbbs rejects
it before looking up or registering a device. No credentials or sessions.
"""
import json
import socket
from datetime import datetime, timezone
from pathlib import Path

HOST = '89.58.39.204'


def varint(value):
    output = bytearray()
    while value > 127:
        output.append((value & 127) | 128)
        value >>= 7
    output.append(value)
    return bytes(output)


def field(number, data):
    return varint((number << 3) | 2) + varint(len(data)) + data


def read_varint(data, offset):
    value = 0
    for shift in range(0, 70, 7):
        assert offset < len(data), 'Truncated protobuf'
        current = data[offset]
        offset += 1
        value |= (current & 127) << shift
        if current < 128:
            return value, offset
    raise ValueError('Oversized varint')


def fields(data):
    output = {}
    offset = 0
    while offset < len(data):
        tag, offset = read_varint(data, offset)
        if tag & 7 == 0:
            value, offset = read_varint(data, offset)
        elif tag & 7 == 2:
            size, offset = read_varint(data, offset)
            assert offset + size <= len(data)
            value = data[offset:offset + size]
            offset += size
        else:
            raise ValueError('Unexpected response protobuf type')
        output[tag >> 3] = value
    return output


def receive_exact(stream, length):
    output = b''
    while len(output) < length:
        chunk = stream.recv(length - len(output))
        assert chunk, 'Unexpected TCP EOF'
        output += chunk
    return output


def test_tcp(port):
    # RendezvousMessage.test_nat_request (field 20), serial 0.
    request = field(20, b'')
    with socket.create_connection((HOST, port), timeout=10) as stream:
        stream.settimeout(10)
        stream.sendall(bytes([len(request) << 2]) + request)
        first = receive_exact(stream, 1)
        size = (first[0] & 3) + 1
        length = int.from_bytes(first + receive_exact(stream, size - 1), 'little') >> 2
        assert 0 < length < 4096, 'Unexpected RustDesk frame size'
        response = fields(receive_exact(stream, length))
        assert 21 in response, 'No TestNatResponse from hbbs'
        port_value = fields(response[21]).get(1)
        assert isinstance(port_value, int) and 0 < port_value <= 65535
    return 'RustDesk TestNatResponse received'


def test_udp():
    # RegisterPk has nonempty UUID/PK but an ID shorter than six characters.
    # The pinned server returns UUID_MISMATCH before touching its peer database.
    request = field(15, field(1, b'probe') + field(2, b'arceus-protocol-probe') + field(3, b'\x01'))
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as stream:
        stream.settimeout(10)
        stream.connect((HOST, 21116))
        stream.send(request)
        response = fields(stream.recv(4096))
        assert 16 in response and fields(response[16]).get(1) == 2, 'Unexpected UDP rejection response'
    return 'RustDesk RegisterPkResponse rejection received; no device registered'


def main():
    report = {'utc': datetime.now(timezone.utc).isoformat(), 'host': HOST, 'remote_desktop_session': 'not_tested', 'checks': {}}
    for port in (21115, 21116):
        report['checks'][f'tcp_{port}'] = test_tcp(port)
    report['checks']['udp_21116'] = test_udp()
    with socket.create_connection((HOST, 21117), timeout=10):
        report['checks']['relay_tcp_21117'] = 'reachable; relay session not tested'
    Path('SERVER-PROTOCOL-VERIFICATION.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
