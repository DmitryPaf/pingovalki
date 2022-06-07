import os
import socket

url = 'yazasa.ru'


def calc_checksum(packet: bytes) -> int:
    words = [int.from_bytes(packet[_:_ + 2], "big") for _ in range(0, len(packet), 2)]
    checksum = sum(words)
    while checksum > 0xffff:
        checksum = (checksum & 0xffff) + (checksum >> 16)
    return 0xffff - checksum


def test() -> None:
    """
    Для самопроверки отловил ICMP пакет в Wireshark,
    Заменил в нём байты контрольной суммы на нули
    """
    packet = \
        b"\x08\x00\x00\x00\x1c\x64\x7a\x69\x64\x41\x45\x63\x64\x57\x34\x65" \
        b"\x57\x7a\x65\x75\x73\x63\x79\x64"
    excepted = int.from_bytes(b"\x75\x19", "big")  # Ожидаемая контрольная сумма
    checksum = calc_checksum(packet)
    if (checksum == excepted):
        print("ok")
    else:
        print("got", hex(checksum), "but excepted", hex(excepted))


def send_icmp(url_) -> None:
    ICMP_TYPE = b"\x08"
    ICMP_CODE = b"\x00"
    ICMP_CHECKSUM = b"\x00\x00"
    ICMP_ID = b"\xae\x58"
    ICMP_SEQ = b"\x7a\x69"
    ICMP_DATA = b""

    packet = bytearray(ICMP_TYPE + ICMP_CODE + ICMP_CHECKSUM + ICMP_ID + ICMP_SEQ + ICMP_DATA)
    checksum = calc_checksum(packet)
    checksum = checksum.to_bytes(2, "big")
    packet[2], packet[3] = checksum[0], checksum[1]
    packet = bytes(packet)
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
    try:

        while packet:
            sent = sock.sendto(packet, (url_, 1))
            packet = packet[sent:]

        reply, _ = sock.recvfrom(1024)
        reply = reply[20:]  # Cut down IP headers

        if not reply[0]:
            print(url_ + ' online')
        else:
            print(url_ + "  offline")
    except:
        print(url_ + "  offline")


send_icmp(url)
